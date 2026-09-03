create or replace function public.initialize_faculty_app_schema(
    p_department text default null
)
returns jsonb
language plpgsql
security definer
set search_path=public,pg_temp
as $$
declare
    schemas jsonb;
    table_record record;
    column_record record;
    t_name text;
    c_name text;
    c_type text;
    total_tables integer:=0;
begin

    create table if not exists public.departments_registry(
        id bigint generated always as identity primary key,
        department text unique not null,
        created_at timestamptz default now()
    );

    if p_department is not null and btrim(p_department)<>'' then
        insert into public.departments_registry(department)
        values(btrim(p_department))
        on conflict(department) do nothing;
    end if;

    schemas:=$schema$
    {
        "subjects":{
            "department":"text",
            "subject_name":"text",
            "subject_code":"text",
            "subject_semister":"integer",
            "subject_type":"text",
            "subject_credits":"double precision",
            "alloted_faculty_ids":"text",
            "alloted_sections":"text"
        },

        "faculty":{
            "department":"text",
            "faculty_name":"text",
            "faculty_department":"text",
            "faculty_id":"text",
            "faculty_salary":"integer",
            "faculty_overall_experience":"integer",
            "faculty_experience_mtiet":"integer",
            "faculty_password":"text",
            "faculty_permanent_district":"text",
            "faculty_permanent_state":"text",
            "faculty_current_district":"text",
            "faculty_current_state":"text",
            "is_controller":"text",
            "is_hod":"text",
            "is_principal":"text",
            "is_admin":"text",
            "designation":"text",
            "is_phd_holder":"text"
        },

        "students":{
            "department":"text",
            "student_name":"text",
            "student_age":"integer",
            "stuent_batch":"text",
            "student_regulation":"text",
            "student_adress":"text",
            "student_district":"text",
            "student_state":"text",
            "student_gender":"text",
            "student_roll_number":"text",
            "student_mentor_id":"text"
        },

        "students_academic_details":{
            "department":"text",
            "student_roll_numner":"text",
            "student_batch":"text",
            "student_department":"text",
            "regulation":"text",
            "status":"text"
        },

        "alumni":{
            "department":"text",
            "student_roll_number":"text",
            "student_batch":"text",
            "student_department":"text",
            "student_regulation":"text"
        },

        "faculty_images":{
            "department":"text",
            "faculty_image":"bytea",
            "faculty_id":"text"
        },

        "examination_results_faculty":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "awarded_credits":"double precision",
            "academic_year":"text",
            "quarter":"text",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "academic_results":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "subject_name":"text",
            "subject_code":"text",
            "subject_semister":"integer",
            "subject_sections":"text",
            "pass_percent":"double precision",
            "subject_credits":"double precision",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "feedback":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "subject_name":"text",
            "subject_semester":"integer",
            "subject_type":"text",
            "feed_back_score":"double precision",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "hod_feedbacks":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text",
            "reason":"text"
        },

        "project_guidence":{
            "department":"text",
            "batches":"text",
            "student_roll_numbers":"text",
            "project_title":"text",
            "is_conference":"text",
            "is_journal":"text",
            "is_patent":"text",
            "paper_proof":"text",
            "scopus_proof":"text",
            "is_published":"text",
            "is_granted":"text",
            "proof_certificate_url":"text",
            "credits":"double precision",
            "faculty_id":"text",
            "faculty_name":"text",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "innovation_in_teaching":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "subject_type":"text",
            "problems_faced":"text",
            "innovation":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "obe_practice":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "obe_practice_type":"text",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "product_development_by_student":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "students_names_roll_numbers":"text",
            "team_name":"text",
            "product_name":"text",
            "product_description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "seminar_workshop_conference_symposium_by_students":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "name_roll_number":"text",
            "batch":"text",
            "participated_in":"text",
            "result":"text",
            "participation_type":"text",
            "team_name":"text",
            "proof_url":"text",
            "prize_position":"integer",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "competetion_contest__by_students":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "name_roll_number":"text",
            "batch":"text",
            "participated_in":"text",
            "result":"text",
            "participation_type":"text",
            "team_name":"text",
            "proof_url":"text",
            "prize_position":"integer",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "language_certifications":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "language":"text",
            "country":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "online_certifications":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "certification_name":"text",
            "certification_type":"text",
            "certification_company":"text",
            "description":"text",
            "duration":"integer",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "internships_inplant_training":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "students_names_roll_numbers":"text",
            "batch":"text",
            "company_name":"text",
            "duration_days":"integer",
            "stipend_offered":"integer",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "special_awards":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "award_name":"text",
            "award_received_from":"text",
            "issuer_name":"text",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "student_involvements_in_startups":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "batch":"text",
            "student_name_roll_number":"text",
            "team_name":"text",
            "description":"text",
            "startup_enterpernurship_name":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "competetive_examinations":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "exam_name":"text",
            "result":"text",
            "description":"text",
            "proof_url":"text",
            "student_name_roll_numbers":"text",
            "batch":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "placements":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "company":"text",
            "package":"double precision",
            "student_names_roll_numbers":"text",
            "batch":"text",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "ict_skill_rack":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "ict_skill_rack_target":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "coding_data":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "batch":"text",
            "student_name_roll_number":"text",
            "platform":"text",
            "number_of_problems_solved":"integer",
            "type":"text",
            "credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "publications_conferences_journals_book_chapters":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "publication_type":"text",
            "paper_title":"text",
            "journal_name":"text",
            "issn_number":"text",
            "scopus_indexed":"text",
            "quartile":"text",
            "impact_factor_or_snip":"double precision",
            "author_position":"integer",
            "author_type":"text",
            "doi_link":"text",
            "paper_proof_url":"text",
            "journal_scopus_proof_url":"text",
            "name_of_the_conference":"text",
            "isbn_number":"text",
            "chapter_title":"text",
            "title_of_the_book":"text",
            "book_level":"text",
            "year_of_publication":"integer",
            "chapter_isbn_issn_number":"text",
            "chapter_proof":"text",
            "credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "patent_copy_rights":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "patent_name":"text",
            "patent_type":"text",
            "patent_status":"text",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "consultancy_funding_grants":{
            "department":"text",
            "faculty_id":"text",
            "faculty_number":"text",
            "faculty_name":"text",
            "type":"text",
            "description":"text",
            "proof_url":"text",
            "amount":"double precision",
            "is_amount_greater_than_10_lakhs":"text",
            "credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "citation_impacts":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "paper_name":"text",
            "number_of_citations":"integer",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "phd_guidance":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "research_type":"text",
            "external":"integer",
            "internal_full_time":"integer",
            "part_time":"integer",
            "full_time":"integer",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "book_publications":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "book_name":"text",
            "book_category":"text",
            "publisher_name":"text",
            "published_year":"integer",
            "author_type":"text",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "on_campus_recruitments_by_faculty":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "credits":"double precision",
            "company_name":"text",
            "academic_year":"text",
            "number_of_students_placed":"integer",
            "highest_package":"double precision",
            "average_package":"double precision",
            "approval_of_principal":"integer",
            "approval_of_placement_cell":"integer",
            "is_admin_approved":"text",
            "proof_url":"text",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "guest_lectures":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "institute_type":"text",
            "institution_name":"text",
            "number_of_days":"integer",
            "topics_covered":"text",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "online_certifications_4weeks":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "certificate_type":"text",
            "certificate_name":"text",
            "duration":"integer",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "mooc_courses_by_faculty":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "course_name":"text",
            "duration":"text",
            "uploaded_in":"text",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "news_letters_and_magazines":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "type":"text",
            "name":"text",
            "description":"text",
            "proof_url":"text",
            "credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "nirf_event_participations":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "event_name":"text",
            "event_type":"text",
            "number_of_days":"integer",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "special_awards_fellowships":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "award_type":"text",
            "name":"text",
            "issued_institution":"text",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "membership":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "membership_name":"text",
            "duration_in_years":"double precision",
            "issued_body_name":"text",
            "academic_year":"text",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "faculty_exchanges":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "exchange_faculty_name":"text",
            "designation":"text",
            "employer":"text",
            "type":"text",
            "number_of_days":"integer",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "extension_activities":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "activity_name":"text",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "alumni_connection_by_faculties":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "type":"text",
            "batch":"text",
            "student_name_roll_numbers":"text",
            "title":"text",
            "description":"text",
            "proof_url":"text",
            "credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "collaborations_industry_institute":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "colloboration_type":"text",
            "colloboration_name":"text",
            "description":"text",
            "proof_url":"text",
            "funding":"integer",
            "colloboration_with":"text",
            "organization_name":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "value_added_courses":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "course_name":"text",
            "number_of_days":"integer",
            "number_of_students":"integer",
            "type":"text",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "organizing_international_conference":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "conference_name":"text",
            "partner":"text",
            "scopused_in_index":"integer",
            "description":"text",
            "proof_url":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "event_organizations":{
            "department":"text",
            "faculty_id":"text",
            "faculty_name":"text",
            "event_name":"text",
            "organized_with":"text",
            "number_of_days":"integer",
            "proof_url":"text",
            "description":"text",
            "awarded_credits":"double precision",
            "hod_approval":"text",
            "admin_approval":"text"
        },

        "max_scores_for_fs":{
            "table_name":"text",
            "score":"integer",
            "min_score_professor":"integer"
        }
    }
    $schema$::jsonb;


    for table_record in
        select key,value from jsonb_each(schemas)
    loop

        t_name:=table_record.key;

        execute format(
            'create table if not exists public.%I(
                id bigint generated always as identity primary key
            )',
            t_name
        );


        if not exists(
            select 1
            from information_schema.columns
            where table_schema='public'
            and table_name=t_name
            and column_name='id'
        ) then

            execute format(
                'alter table public.%I
                 add column id bigint generated always as identity',
                t_name
            );

        end if;


        for column_record in
            select key,value
            from jsonb_each_text(table_record.value)
        loop

            c_name:=column_record.key;
            c_type:=column_record.value;

            execute format(
                'alter table public.%I
                 add column if not exists %I %s',
                t_name,
                c_name,
                c_type
            );

        end loop;


        execute format(
            'alter table public.%I enable row level security',
            t_name
        );


        execute format(
            'create unique index if not exists %I
             on public.%I(id)',
            'uq_'||substr(md5(t_name||'_id'),1,20),
            t_name
        );


        if table_record.value ? 'department'
           and table_record.value ? 'faculty_id' then

            execute format(
                'create index if not exists %I
                 on public.%I(department,faculty_id)',
                'idx_'||substr(md5(t_name||'_department_faculty'),1,20),
                t_name
            );

        elsif table_record.value ? 'department' then

            execute format(
                'create index if not exists %I
                 on public.%I(department)',
                'idx_'||substr(md5(t_name||'_department'),1,20),
                t_name
            );

        end if;


        total_tables:=total_tables+1;

    end loop;


    /*
       IMPORTANT MIGRATIONS FOR TABLES THAT MAY ALREADY EXIST
    */

    if exists(
        select 1 from information_schema.columns
        where table_schema='public'
        and table_name='subjects'
        and column_name='subject_credits'
    ) then

        alter table public.subjects
        alter column subject_credits type double precision
        using subject_credits::double precision;

    end if;


    if exists(
        select 1 from information_schema.columns
        where table_schema='public'
        and table_name='academic_results'
        and column_name='subject_credits'
    ) then

        alter table public.academic_results
        alter column subject_credits type double precision
        using subject_credits::double precision;

    end if;


    create unique index if not exists uq_faculty_department_faculty_id
    on public.faculty(department,faculty_id);


    create unique index if not exists uq_students_department_roll
    on public.students(department,student_roll_number);


    create unique index if not exists uq_examination_results
    on public.examination_results_faculty(
        department,
        faculty_id,
        academic_year,
        quarter
    );


    create table if not exists public.dynamic_table_registry(
        id bigint generated always as identity primary key,
        logical_database text not null,
        logical_table text not null,
        physical_table text not null unique,
        columns jsonb not null,
        created_at timestamptz default now(),
        updated_at timestamptz default now(),
        unique(logical_database,logical_table)
    );


    alter table public.dynamic_table_registry
    enable row level security;


    perform pg_notify('pgrst','reload schema');


    return jsonb_build_object(
        'success',true,
        'department',p_department,
        'tables_ready',total_tables
    );

end;
$$;


revoke all
on function public.initialize_faculty_app_schema(text)
from public;


grant execute
on function public.initialize_faculty_app_schema(text)
to service_role;


notify pgrst,'reload schema';