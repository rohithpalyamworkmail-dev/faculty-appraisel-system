import streamlit as st
from supabase import create_client,Client
from supabase.client import ClientOptions

@st.cache_resource
def get_supabase()->Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
        options=ClientOptions(
            postgrest_client_timeout=30,
            storage_client_timeout=30,
            schema="public",
            auto_refresh_token=False,
            persist_session=False
        )
    )