import time
import ssl
import httpx
import pandas as pd
from supabase_client import get_supabase


def _filters(query,filters):
    if filters:
        for column,value in filters.items():
            if value is None:query=query.is_(column,"null")
            else:query=query.eq(column,value)
    return query


def _transient_error(error):
    if isinstance(error,(httpx.TransportError,ssl.SSLError,ConnectionError,EOFError,OSError)):return True
    text=str(error).lower()
    messages=["eof occurred","server disconnected","connection reset","connection aborted","remoteprotocolerror","readerror","connecterror","readtimeout","ssl"]
    return any(message in text for message in messages)


def _execute(operation,retries=3):
    last_error=None

    for attempt in range(retries):
        try:
            client=get_supabase()
            return operation(client)

        except Exception as e:
            last_error=e

            if not _transient_error(e) or attempt==retries-1:
                raise

            try:get_supabase.clear()
            except:pass

            time.sleep(attempt+1)

    raise last_error


def get_rows(table,filters=None,columns="*",order_by=None,descending=False):
    def operation(client):
        query=_filters(client.table(table).select(columns),filters)
        if order_by:query=query.order(order_by,desc=descending)
        return query.execute()

    response=_execute(operation)
    return response.data or []


def get_one(table,filters=None,columns="*"):
    def operation(client):
        query=_filters(client.table(table).select(columns),filters)
        return query.limit(1).execute()

    response=_execute(operation)
    return response.data[0] if response.data else None


def insert_row(table,data):
    response=_execute(lambda client:client.table(table).insert(data).execute())
    return response.data or []


def _clean_value(value):
    if value is None:return None

    try:
        if pd.isna(value):return None
    except:pass

    if hasattr(value,"item"):
        try:return value.item()
        except:pass

    if isinstance(value,pd.Timestamp):return value.isoformat()

    return value


def _records(data):
    if isinstance(data,pd.DataFrame):
        if data.empty:return []
        records=data.astype(object).where(pd.notnull(data),None).to_dict("records")
        return [{key:_clean_value(value) for key,value in row.items()} for row in records]

    if isinstance(data,dict):
        return [{key:_clean_value(value) for key,value in data.items()}]

    if isinstance(data,list):
        return [{key:_clean_value(value) for key,value in row.items()} if isinstance(row,dict) else row for row in data]

    return []


def insert_rows(table,data):
    records=_records(data)
    if not records:return []

    response=_execute(lambda client:client.table(table).insert(records).execute())
    return response.data or []


def update_rows(table,data,filters):
    def operation(client):
        query=_filters(client.table(table).update(data),filters)
        return query.execute()

    response=_execute(operation)
    return response.data or []


def delete_rows(table,filters):
    def operation(client):
        query=_filters(client.table(table).delete(),filters)
        return query.execute()

    response=_execute(operation)
    return response.data or []


def upsert_rows(table,data,on_conflict=None):
    records=_records(data)
    if not records:return []

    def operation(client):
        if on_conflict:return client.table(table).upsert(records,on_conflict=on_conflict).execute()
        return client.table(table).upsert(records).execute()

    response=_execute(operation)
    return response.data or []


def get_dataframe(table,filters=None,columns="*"):
    return pd.DataFrame(get_rows(table,filters,columns))


def exists(table,filters):
    return get_one(table,filters,"id") is not None


def encode_bytea(data):
    if data is None:return None
    if isinstance(data,(bytes,bytearray)):return "\\x"+bytes(data).hex()
    return data


def decode_bytea(data):
    if data is None:return None
    if isinstance(data,bytes):return data

    if isinstance(data,str):
        try:
            if data.startswith("\\x"):return bytes.fromhex(data[2:])
        except:pass

    return data