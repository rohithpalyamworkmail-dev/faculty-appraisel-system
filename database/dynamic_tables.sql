create table if not exists public.dynamic_table_registry(
    id bigint generated always as identity primary key,
    logical_database text not null,
    logical_table text not null,
    physical_table text not null unique,
    columns jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(logical_database,logical_table)
);

alter table public.dynamic_table_registry enable row level security;

revoke all on public.dynamic_table_registry from anon;
revoke all on public.dynamic_table_registry from authenticated;


create or replace function public.dynamic_list_tables(
    p_database text
)
returns table(table_name text)
language plpgsql
security definer
set search_path=public,pg_temp
as $$
begin
    return query
    select logical_table
    from public.dynamic_table_registry
    where logical_database=p_database
    order by logical_table;
end;
$$;


create or replace function public.dynamic_create_table(
    p_database text,
    p_table text,
    p_columns jsonb,
    p_rows jsonb default '[]'::jsonb
)
returns boolean
language plpgsql
security definer
set search_path=public,pg_temp
as $$
declare
    v_physical text;
    v_definitions text='';
    v_item jsonb;
    v_name text;
    v_type text;
    v_sql_type text;
    v_first boolean=true;
    v_seen text[]='{}';
begin
    if p_database is null or btrim(p_database)='' then
        raise exception 'Database / scope cannot be empty';
    end if;

    if p_table is null or btrim(p_table)='' then
        raise exception 'Table name cannot be empty';
    end if;

    if p_columns is null
       or jsonb_typeof(p_columns)<>'array'
       or jsonb_array_length(p_columns)=0 then
        raise exception 'At least one column is required';
    end if;

    if exists(
        select 1
        from public.dynamic_table_registry
        where logical_database=p_database
        and logical_table=p_table
    ) then
        raise exception 'Table "%" already exists in "%"',p_table,p_database;
    end if;

    v_physical='dyn_'||substr(md5(p_database||'|'||p_table),1,24);

    if exists(
        select 1
        from information_schema.tables
        where table_schema='public'
        and table_name=v_physical
    ) then
        raise exception 'Internal physical table name collision';
    end if;

    for v_item in
        select value
        from jsonb_array_elements(p_columns)
    loop
        v_name=v_item->>'name';
        v_type=upper(coalesce(v_item->>'type','TEXT'));

        if v_name is null or v_name!~'^[A-Za-z_][A-Za-z0-9_]*$' then
            raise exception 'Invalid column name: %',v_name;
        end if;

        if v_name=any(v_seen) then
            raise exception 'Duplicate column name: %',v_name;
        end if;

        v_seen=array_append(v_seen,v_name);

        case v_type
            when 'INTEGER' then v_sql_type='bigint';
            when 'BIGINT' then v_sql_type='bigint';
            when 'REAL' then v_sql_type='double precision';
            when 'DOUBLE PRECISION' then v_sql_type='double precision';
            when 'FLOAT' then v_sql_type='double precision';
            when 'TEXT' then v_sql_type='text';
            else
                raise exception 'Unsupported data type "%" for column "%"',v_type,v_name;
        end case;

        if not v_first then
            v_definitions=v_definitions||',';
        end if;

        v_definitions=v_definitions||format('%I %s',v_name,v_sql_type);
        v_first=false;
    end loop;

    execute format(
        'create table public.%I (%s)',
        v_physical,
        v_definitions
    );

    execute format(
        'alter table public.%I enable row level security',
        v_physical
    );

    insert into public.dynamic_table_registry(
        logical_database,
        logical_table,
        physical_table,
        columns
    )
    values(
        p_database,
        p_table,
        v_physical,
        p_columns
    );

    if p_rows is not null
       and jsonb_typeof(p_rows)='array'
       and jsonb_array_length(p_rows)>0 then

        execute format(
            'insert into public.%I
             select *
             from jsonb_populate_recordset(null::public.%I,$1)',
            v_physical,
            v_physical
        )
        using p_rows;
    end if;

    return true;
end;
$$;


create or replace function public.dynamic_get_table(
    p_database text,
    p_table text
)
returns jsonb
language plpgsql
security definer
set search_path=public,pg_temp
as $$
declare
    v_physical text;
    v_columns jsonb;
    v_rows jsonb;
begin
    select physical_table,columns
    into v_physical,v_columns
    from public.dynamic_table_registry
    where logical_database=p_database
    and logical_table=p_table;

    if not found then
        raise exception 'Table "%" does not exist in "%"',p_table,p_database;
    end if;

    execute format(
        'select coalesce(jsonb_agg(to_jsonb(t)),''[]''::jsonb)
         from public.%I t',
        v_physical
    )
    into v_rows;

    return jsonb_build_object(
        'columns',v_columns,
        'rows',coalesce(v_rows,'[]'::jsonb)
    );
end;
$$;


create or replace function public.dynamic_replace_table_data(
    p_database text,
    p_table text,
    p_rows jsonb
)
returns boolean
language plpgsql
security definer
set search_path=public,pg_temp
as $$
declare
    v_physical text;
begin
    select physical_table
    into v_physical
    from public.dynamic_table_registry
    where logical_database=p_database
    and logical_table=p_table;

    if not found then
        raise exception 'Table "%" does not exist in "%"',p_table,p_database;
    end if;

    if p_rows is null then
        p_rows='[]'::jsonb;
    end if;

    if jsonb_typeof(p_rows)<>'array' then
        raise exception 'Rows must be a JSON array';
    end if;

    execute format(
        'truncate table public.%I',
        v_physical
    );

    if jsonb_array_length(p_rows)>0 then
        execute format(
            'insert into public.%I
             select *
             from jsonb_populate_recordset(null::public.%I,$1)',
            v_physical,
            v_physical
        )
        using p_rows;
    end if;

    update public.dynamic_table_registry
    set updated_at=now()
    where logical_database=p_database
    and logical_table=p_table;

    return true;
end;
$$;


create or replace function public.dynamic_drop_table(
    p_database text,
    p_table text
)
returns boolean
language plpgsql
security definer
set search_path=public,pg_temp
as $$
declare
    v_physical text;
begin
    select physical_table
    into v_physical
    from public.dynamic_table_registry
    where logical_database=p_database
    and logical_table=p_table;

    if not found then
        raise exception 'Table "%" does not exist in "%"',p_table,p_database;
    end if;

    execute format(
        'drop table if exists public.%I',
        v_physical
    );

    delete from public.dynamic_table_registry
    where logical_database=p_database
    and logical_table=p_table;

    return true;
end;
$$;


revoke all on function public.dynamic_list_tables(text) from public;
revoke all on function public.dynamic_create_table(text,text,jsonb,jsonb) from public;
revoke all on function public.dynamic_get_table(text,text) from public;
revoke all on function public.dynamic_replace_table_data(text,text,jsonb) from public;
revoke all on function public.dynamic_drop_table(text,text) from public;

grant execute on function public.dynamic_list_tables(text) to service_role;
grant execute on function public.dynamic_create_table(text,text,jsonb,jsonb) to service_role;
grant execute on function public.dynamic_get_table(text,text) to service_role;
grant execute on function public.dynamic_replace_table_data(text,text,jsonb) to service_role;
grant execute on function public.dynamic_drop_table(text,text) to service_role;

notify pgrst,'reload schema';