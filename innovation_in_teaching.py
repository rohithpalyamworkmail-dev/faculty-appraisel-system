import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class innovationInTeaching:
    def __init__(self):
        self.db=ActivityDatabase("innovation_in_teaching")

    def checkDocument(self,subject_type):
        try:
            df=st.session_state.get("handling_subjects",pd.DataFrame())
            if df.empty:return False
            return not df[df["subject_type"].astype(str).str.strip()==str(subject_type).strip()].empty
        except Exception as e:
            st.error(f"Subject Validation Error: {e}")
            return False

    def insertDocuments(self,df):
        df=df.copy();df["awarded_credits"]=2
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("subject_type,problems_faced,innovation,proof_url,awarded_credits")
            if df.empty:
                st.info("No Innovation In Teaching entries are available for editing.")
                return

            config={"subject_type":"Subject Type","problems_faced":"Problems Faced","innovation":"Innovation","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["subject_type","awarded_credits"],column_config=config,key="innovation_in_teaching_editor")

            if st.toggle("Update",key="innovation_in_teaching_update"):
                edited_df["awarded_credits"]=2
                if self.db.replace_pending(edited_df):st.success("Innovation In Teaching Updated Successfully.")
                else:st.warning("Innovation In Teaching Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("subject_type,problems_faced,innovation,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No Innovation In Teaching Found.")
                return

            st.subheader("Innovation In Teaching")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["subject_type"]))
                    col1,col2=st.columns(2)
                    with col1:
                        st.write("**Problems Faced**");st.write(row["problems_faced"])
                        st.write("**Innovation**");st.write(row["innovation"])
                    with col2:
                        st.write("**Proof URL**");st.write(row["proof_url"])
                        st.write(f"**Awarded Credits:** {row['awarded_credits']}")
                        st.write(f"**HoD Approval:** {row['hod_approval']}")
                        st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            subjects_df=st.session_state.get("handling_subjects",pd.DataFrame())
            subject_type=problems_faced=innovation=proof_url=None
            proceed=False

            with col1:
                if subjects_df.empty:
                    st.warning("No subjects are assigned to this faculty.")
                else:
                    subject_type=st.pills("Select Subject Type",subjects_df["subject_type"].dropna().unique().tolist(),selection_mode="single")
                    problems_faced=st.text_area("Problems Faced")
                    innovation=st.text_area("Innovation")
                    proof_url=st.text_input("Proof URL")

                    if st.toggle("Check",key="innovation_in_teaching_check"):
                        if not subject_type:st.warning("Please select a Subject Type.")
                        elif not problems_faced:st.warning("Please enter the Problems Faced.")
                        elif not innovation:st.warning("Please enter the Innovation.")
                        elif not proof_url:st.warning("Please enter the Proof URL.")
                        else:
                            proceed=self.checkDocument(subject_type)
                            if proceed:st.success("Subject Type assignment verified.")
                            else:st.error("You are not assigned to this Subject Type.")

            with col2:
                if proceed:
                    st.info("Awarded Credits: 2")
                    if st.toggle("Add Entry",key="innovation_in_teaching_add_entry"):
                        df=pd.DataFrame([{"subject_type":subject_type,"problems_faced":problems_faced,"innovation":innovation,"proof_url":proof_url,"awarded_credits":2}])
                        if self.insertDocuments(df):st.success("Innovation In Teaching Added Successfully.")
                        else:st.warning("Innovation In Teaching Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()