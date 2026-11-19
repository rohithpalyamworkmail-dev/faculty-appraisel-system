import streamlit as st
from streamlit_option_menu import option_menu
from viewClasses import faculty, student, subjects, settings
from faculty_profiles import viewProfiles
from global_fields import department
from database import get_one

st.set_page_config(page_title="Academic Analytics Dashboard", layout="wide")

for key, value in {"show_login_dialog": False, "settings_login": False, "settings_faculty_name": "", "settings_faculty_id": "", "settings_department": "", "settings_designation": "", "settings_is_hod": "No", "settings_is_principal": "No", "settings_is_admin": "No"}.items():
    if key not in st.session_state:
        st.session_state[key] = value


def _truth(value):
    return str(value or "").strip().lower() in {"yes", "true", "1", "y"}


@st.dialog("Administrative Login")
def login_dialog():
    st.subheader("Administrative Login")
    selected_department = st.selectbox("Select Department", department, key="dialog_dept_select")
    faculty_id = st.text_input("Faculty ID", key="dialog_faculty_id")
    faculty_password = st.text_input("Password", type="password", key="dialog_password")
    if st.button("Login", type="primary", use_container_width=True, key="dialog_login_btn"):
        if not selected_department or not faculty_id or not faculty_password:
            st.warning("Please enter Department, Faculty ID and Password.")
            return
        try:
            result = get_one("faculty", {"department": selected_department, "faculty_id": str(faculty_id).strip(), "faculty_password": faculty_password}, "faculty_name,faculty_department,faculty_id,is_hod,is_principal,is_admin")
            if not result:
                st.session_state["settings_login"] = False
                st.error("Invalid Faculty ID or Password.")
                return
            is_hod = "Yes" if _truth(result.get("is_hod")) else "No"
            is_principal = "Yes" if _truth(result.get("is_principal")) else "No"
            is_admin = "Yes" if _truth(result.get("is_admin")) else "No"
            designation = "Principal" if is_principal == "Yes" else "Admin" if is_admin == "Yes" else "HoD" if is_hod == "Yes" else "Faculty"
            st.session_state.update({"settings_login": True, "settings_faculty_name": result.get("faculty_name", ""), "settings_faculty_id": str(result.get("faculty_id", "")), "settings_department": selected_department, "settings_designation": designation, "settings_is_hod": is_hod, "settings_is_principal": is_principal, "settings_is_admin": is_admin, "show_login_dialog": False})
            st.success("Login Successful.")
            st.rerun()
        except Exception as e:
            st.session_state["settings_login"] = False
            st.error(f"Login Error: {e}")


def get_filtered_departments():
    if not st.session_state.get("settings_login"):
        return department
    if st.session_state.get("settings_is_admin") == "Yes" or st.session_state.get("settings_is_principal") == "Yes":
        return department
    dept = st.session_state.get("settings_department", "")
    return [dept] if dept and dept in department else department


with st.sidebar:
    selected_menu = option_menu("NAVIGATION", ["Students", "Faculty", "Subjects", "Faculty Profile"], icons=["people-fill", "person-badge-fill", "journal-bookmark-fill", "person-bounding-box"], menu_icon="menu-button-wide-fill", default_index=0)
    st.divider()
    if st.session_state.get("settings_login"):
        st.success(f"Logged in as {st.session_state['settings_faculty_name']} ({st.session_state['settings_designation']})")
        if st.button("Logout", use_container_width=True, key="sidebar_logout"):
            st.session_state.update({"settings_login": False, "settings_faculty_name": "", "settings_faculty_id": "", "settings_department": "", "settings_designation": "", "settings_is_hod": "No", "settings_is_principal": "No", "settings_is_admin": "No"})
            st.rerun()
    else:
        if st.button("Login", use_container_width=True, key="sidebar_login"):
            st.session_state["show_login_dialog"] = True

if st.session_state.get("show_login_dialog") and not st.session_state.get("settings_login"):
    login_dialog()

if selected_menu == "Students":
    col1, col2 = st.columns([1, 2], border=True, gap="medium")
    student(col1, col2, get_filtered_departments()).mainLayout()
elif selected_menu == "Faculty":
    col1, col2 = st.columns([1, 2], border=True, gap="medium")
    faculty(col1, col2, get_filtered_departments()).mainLayout()
elif selected_menu == "Subjects":
    col1, col2 = st.columns([1, 2], border=True, gap="medium")
    subjects(col1, col2, get_filtered_departments()).mainLayout()
elif selected_menu == "Faculty Profile":
    profile_option = st.radio("Faculty Profile", ["Approvals / Denials", "View Profiles"], horizontal=True, key="faculty_profile_navigation")
    if profile_option == "Approvals / Denials":
        if not st.session_state.get("settings_login"):
            st.warning("Please login to access Approvals / Denials.")
            if st.button("Open Login", type="primary", key="profile_login_btn"):
                st.session_state["show_login_dialog"] = True
                st.rerun()
        else:
            col1, col2 = st.columns([1, 3], border=True, gap="medium")
            settings(col1, col2).main_layout()
    else:
        viewProfiles().main_layout()
