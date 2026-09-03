import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class moocCourses:
    def __init__(self):
        self.db=ActivityDatabase("mooc_courses_by_faculty")

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("course_name,duration,uploaded_in,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No MOOC Course entries are available for editing.")
                return

            config={"course_name":"Course Name","duration":"Duration","uploaded_in":"Uploaded In","proof_url":"Proof URL","description":"Description","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="mooc_courses_editor")

            if st.toggle("Update",key="mooc_courses_update"):
                edited_df["awarded_credits"]=5

                if self.db.replace_pending(edited_df):st.success("MOOC Course Entries Updated Successfully.")
                else:st.warning("MOOC Course Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("course_name,duration,uploaded_in,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No MOOC Course entries found.")
                return

            st.subheader("MOOC Courses")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["course_name"]))
                    st.write(f"**Duration:** {row['duration']}")
                    st.write(f"**Uploaded In:** {row['uploaded_in']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")

                    col1,col2,col3=st.columns(3)
                    with col1:st.write(f"**Awarded Credits:** {row['awarded_credits']}")
                    with col2:st.write(f"**HoD Approval:** {row['hod_approval']}")
                    with col3:st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            proceed=False

            with col1:
                st.subheader("MOOC Course Entry")
                course_name=st.text_input("Course Name")
                duration=st.text_input("Duration")
                uploaded_in=st.text_input("Uploaded In")
                proof_url=st.text_input("Proof URL")
                description=st.text_input("Description")

                if st.toggle("Check",key="mooc_courses_check"):
                    if not course_name:st.warning("Please enter Course Name.")
                    elif not duration:st.warning("Please enter Duration.")
                    elif not uploaded_in:st.warning("Please enter Uploaded In.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    elif not description:st.warning("Please enter Description.")
                    else:proceed=True;st.success("MOOC Course details verified.")

            with col2:
                if proceed:
                    st.subheader("MOOC Course Details")
                    st.write(f"**Course Name:** {course_name}")
                    st.write(f"**Duration:** {duration}")
                    st.write(f"**Uploaded In:** {uploaded_in}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 5")

                    if st.toggle("Add Entry",key="mooc_courses_add"):
                        df=pd.DataFrame([{"course_name":course_name,"duration":duration,"uploaded_in":uploaded_in,"proof_url":proof_url,"description":description,"awarded_credits":5}])

                        if self.insertDocuments(df):st.success("MOOC Course Added Successfully.")
                        else:st.warning("MOOC Course Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()