import pandas as pd
import streamlit as st
from database import get_one,get_rows,decode_bytea

class facultyLogin:
    def do_login(self,department,faculty_id,faculty_password):
        if not department or not faculty_id or not faculty_password:
            st.error("Please enter Department, Faculty ID and Faculty Password.")
            return False

        try:
            faculty_id=str(faculty_id).strip()
            result=get_one("faculty",{"department":department,"faculty_id":faculty_id,"faculty_password":faculty_password})

            if not result:
                st.session_state["login"]=False
                st.error("Invalid Faculty ID or Password.")
                return False

            faculty_name=result.get("faculty_name","")
            is_hod=str(result.get("is_hod","")).strip().upper()
            is_principal=str(result.get("is_principal","")).strip().upper()
            is_admin=str(result.get("is_admin","")).strip().upper()

            if is_admin=="TRUE":
                hod_approval,admin_approval="NOT APPLICABLE","NOT APPLICABLE"
            elif is_hod=="TRUE" or is_principal=="TRUE":
                hod_approval,admin_approval="NOT APPLICABLE","UN KNOWN"
            else:
                hod_approval,admin_approval="UN KNOWN","UN KNOWN"

            st.session_state["login"]=True
            st.session_state["faculty_name"]=faculty_name
            st.session_state["faculty_id"]=faculty_id
            st.session_state["department"]=department
            st.session_state["hod_approval"]=hod_approval
            st.session_state["admin_approval"]=admin_approval

            image=get_one("faculty_images",{"department":department,"faculty_id":faculty_id},"faculty_image")
            st.session_state["Faculty Image"]=decode_bytea(image.get("faculty_image")) if image else None

            subjects=get_rows("subjects",{"department":department},"subject_name,subject_code,subject_semister,subject_type,subject_credits,alloted_faculty_ids,alloted_sections")
            handling_subjects=[]

            for row in subjects:
                if not row.get("alloted_faculty_ids"):continue

                faculty_ids=[x.strip() for x in str(row.get("alloted_faculty_ids","")).split(",") if x.strip()]
                sections=[x.strip() for x in str(row.get("alloted_sections","")).split(",") if x.strip()]

                if faculty_id not in faculty_ids:continue

                faculty_sections=[sections[i] for i,fid in enumerate(faculty_ids) if fid==faculty_id and i<len(sections)]

                handling_subjects.append({
                    "subject_name":row.get("subject_name"),
                    "subject_code":row.get("subject_code"),
                    "subject_semister":row.get("subject_semister"),
                    "subject_type":row.get("subject_type"),
                    "subject_credits":row.get("subject_credits"),
                    "alloted_section":", ".join(faculty_sections)
                })

            st.session_state["handling_subjects"]=pd.DataFrame(
                handling_subjects,
                columns=["subject_name","subject_code","subject_semister","subject_type","subject_credits","alloted_section"]
            )

            mentees=get_rows("students",{"department":department,"student_mentor_id":faculty_id},"student_name,stuent_batch,student_roll_number,student_regulation")

            st.session_state["mentees_list"]=pd.DataFrame(
                [{
                    "student_name":row.get("student_name"),
                    "student_batch":row.get("stuent_batch"),
                    "student_roll_number":row.get("student_roll_number"),
                    "student_regulation":row.get("student_regulation")
                } for row in mentees],
                columns=["student_name","student_batch","student_roll_number","student_regulation"]
            )

            return True

        except Exception as e:
            st.session_state["login"]=False
            st.error(f"Login Error: {e}")
            return False