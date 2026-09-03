import streamlit as st
from supabase import create_client,Client


@st.cache_resource
def get_supabase()->Client:
    try:
        url=str(st.secrets["SUPABASE_URL"]).strip()
        key=str(st.secrets["SUPABASE_KEY"]).strip()

        if not url:
            raise ValueError("SUPABASE_URL is empty.")

        if not key:
            raise ValueError("SUPABASE_KEY is empty.")

        return create_client(url,key)

    except KeyError as e:
        raise RuntimeError(
            f"Missing Supabase secret: {e}"
        )


class SupabaseProxy:
    def __getattr__(self,name):
        client=get_supabase()
        return getattr(client,name)


supabase=SupabaseProxy()
