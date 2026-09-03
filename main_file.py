import streamlit as st
from streamlit_option_menu import option_menu
from viewClasses import faculty,student,subjects,settings
from faculty_profiles import viewProfiles

st.set_page_config(page_title="Academic Analytics Dashboard",layout="wide")

with st.sidebar:
    selected_menu=option_menu(
        "NAVIGATION",
        ["Students","Faculty","Subjects","Faculty Profile"],
        icons=["people-fill","person-badge-fill","journal-bookmark-fill","person-bounding-box"],
        menu_icon="menu-button-wide-fill",
        default_index=0
    )

if selected_menu=="Students":
    col1,col2=st.columns([1,2],border=True,gap="medium")
    student(col1,col2).mainLayout()

elif selected_menu=="Faculty":
    col1,col2=st.columns([1,2],border=True,gap="medium")
    faculty(col1,col2).mainLayout()

elif selected_menu=="Subjects":
    col1,col2=st.columns([1,2],border=True,gap="medium")
    subjects(col1,col2).mainLayout()

elif selected_menu=="Faculty Profile":
    profile_option=st.radio("Faculty Profile",["Approvals / Denials","View Profiles"],horizontal=True,key="faculty_profile_navigation")

    if profile_option=="Approvals / Denials":
        col1,col2=st.columns([1,3],border=True,gap="medium")
        settings(col1,col2).main_layout()
    else:
        viewProfiles().main_layout()