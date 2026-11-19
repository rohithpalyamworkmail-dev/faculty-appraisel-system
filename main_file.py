import streamlit as st
from streamlit_option_menu import option_menu
from viewClasses import faculty, student, subjects, settings
from faculty_profiles import viewProfiles
import global_fields
from database import get_one

st.set_page_config(page_title="Academic Analytics Dashboard", layout="wide")

# Initialize session state
for key, value in {
    "show_login_dialog": True,
    "settings_login": False,
    "settings_faculty_name": "",
    "settings_faculty_id": "",
    "settings_department": "",
    "settings_designation": "",
    "settings_is_hod": "No",
    "settings_is_principal": "No",
    "settings_is_admin": "No",
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

def _truth(value):
    return str(value or "").strip().lower() in {"yes", "true", "1", "y"}

@st.dialog("Administrative Login")
def login_dialog():
    st.subheader("Administrative Login")
    selected_department = st.selectbox("Select Department", global_fields.department, key="dialog_dept_select")
    role_type = st.selectbox("Select Role Type", ["HoD", "Admin", "Principal"], key="dialog_role_type")
    faculty_id = st.text_input("Faculty ID", key="dialog_faculty_id")
    faculty_password = st.text_input("Password (Optional)", type="password", key="dialog_password")
    
    if st.button("Login", type="primary", use_container_width=True, key="dialog_login_btn"):
        if not selected_department or not faculty_id:
            st.warning("Please enter Department and Faculty ID.")
            return
        try:
            result = get_one("faculty", {"department": selected_department, "faculty_id": str(faculty_id).strip()}, "faculty_name,faculty_department,faculty_id,is_hod,is_principal,is_admin")
            if not result:
                st.error("Invalid Faculty ID for the selected department.")
                return
            
            has_role = False
            if role_type == "HoD" and _truth(result.get("is_hod")): has_role = True
            elif role_type == "Admin" and _truth(result.get("is_admin")): has_role = True
            elif role_type == "Principal" and _truth(result.get("is_principal")): has_role = True
            
            if not has_role:
                st.error(f"This Faculty ID does not have {role_type} privileges.")
                return

            st.session_state.update({
                "settings_login": True,
                "settings_faculty_name": result.get("faculty_name", ""),
                "settings_faculty_id": str(result.get("faculty_id", "")),
                "settings_department": selected_department,
                "settings_designation": role_type,
                "settings_is_hod": "Yes" if role_type == "HoD" else "No",
                "settings_is_principal": "Yes" if role_type == "Principal" else "No",
                "settings_is_admin": "Yes" if role_type == "Admin" else "No",
                "show_login_dialog": False,
            })
            st.success("Login Successful.")
            st.rerun()
        except Exception as e:
            st.error(f"Login Error: {e}")

# Check login state before rendering anything else
if not st.session_state.get("settings_login"):
    if st.session_state.get("show_login_dialog"):
        login_dialog()
    st.stop()  # Stops execution so no content is displayed until logged in

# --- MAIN UI (Runs only if logged in) ---

# Override department variable based on role
if st.session_state.get("settings_is_hod") == "Yes":
    # HoD gets only their department
    global_fields.department = [st.session_state["settings_department"]]
else:
    # Admin & Principal get all departments
    pass

with st.sidebar:
    selected_menu = option_menu(
        "NAVIGATION", 
        ["Students", "Faculty", "Subjects", "Faculty Profile"], 
        icons=["people-fill", "person-badge-fill", "journal-bookmark-fill", "person-bounding-box"], 
        menu_icon="menu-button-wide-fill", 
        default_index=3 # Default to Faculty Profile since they just logged in
    )
    st.divider()
    st.success(f"Logged in as {st.session_state['settings_faculty_name']}\n({st.session_state['settings_designation']})")
    if st.button("Logout", use_container_width=True, key="sidebar_logout"):
        st.session_state.update({
            "settings_login": False, 
            "show_login_dialog": True,
            "settings_faculty_name": "", 
            "settings_faculty_id": "",
            "settings_department": "", 
            "settings_designation": "",
            "settings_is_hod": "No", 
            "settings_is_principal": "No", 
            "settings_is_admin": "No"
        })
        st.rerun()

# Render Views
if selected_menu == "Students":
    col1, col2 = st.columns([1, 2], border=True, gap="medium")
    student(col1, col2, global_fields.department).mainLayout()
elif selected_menu == "Faculty":
    col1, col2 = st.columns([1, 2], border=True, gap="medium")
    faculty(col1, col2, global_fields.department).mainLayout()
elif selected_menu == "Subjects":
    col1, col2 = st.columns([1, 2], border=True, gap="medium")
    subjects(col1, col2, global_fields.department).mainLayout()
elif selected_menu == "Faculty Profile":
    profile_option = st.radio("Faculty Profile", ["Approvals / Denials", "View Profiles"], horizontal=True, key="faculty_profile_navigation")
    if profile_option == "Approvals / Denials":
        col1, col2 = st.columns([1, 3], border=True, gap="medium")
        settings(col1, col2).main_layout()
    else:
        viewProfiles().main_layout()
