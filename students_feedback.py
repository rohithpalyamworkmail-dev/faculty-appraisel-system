import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class studentsFeedback:
    def __init__(self):
        self.db=ActivityDatabase("feedback")

    def calculateCredits(self,score):
        if score>=90:return 4
        if score>=80:return 3
        if score>=70:return 2
        return 0

    def checkDocument(self,semester,subject_type,subject):
        try:
            df=st.session_state.get("handling_subjects",pd.DataFrame())
            if df.empty:return False
            result=df[(df["subject_semister"]==semester)&(df["subject_type"]==subject_type)&(df["subject_name"]==subject)]
            return not result.empty
        except Exception as e:
            st.error(f"Subject Validation Error: {e}")
            return False

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns="subject_name,subject_semester,subject_type,feed_back_score,awarded_credits"
            df=self.db.editable_dataframe(columns)

            if df.empty:
                st.info("No student feedback entries are available for editing.")
                return

            config={"subject_name":"Subject","subject_semester":"Semester","subject_type":"Subject Type","feed_back_score":st.column_config.NumberColumn("Feedback Score",min_value=0,max_value=100,step=1),"awarded_credits":"Awarded Credits"}
            disabled=["subject_name","subject_semester","subject_type","awarded_credits"]
            edited_df=st.data_editor(df,num_rows="fixed",use_container_width=True,hide_index=True,disabled=disabled,column_config=config,key="students_feedback_editor")

            if st.toggle("Update",key="students_feedback_update"):
                edited_df["awarded_credits"]=edited_df["feed_back_score"].apply(self.calculateCredits)
                edited_df=edited_df[["subject_name","subject_semester","subject_type","feed_back_score","awarded_credits"]]
                if self.db.replace_pending(edited_df):st.success("Student Feedback Updated Successfully.")
                else:st.warning("Student Feedback Could Not Be Updated.")
        except Exception as e:
            st.error(f"Feedback Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="subject_name,subject_semester,subject_type,feed_back_score,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)

            if df.empty:
                st.info("No Student Feedback Found.")
                return

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["subject_name"]),divider=True,text_alignment="center")
                    col1,col2,col3=st.columns(3)

                    with col1:
                        st.write(f"**Semester:** {row['subject_semester']}")
                        st.write(f"**Subject Type:** {row['subject_type']}")

                    with col2:
                        st.write(f"**Feedback Score:** {row['feed_back_score']}")
                        st.write(f"**Awarded Credits:** {row['awarded_credits']}")

                    with col3:
                        st.write(f"**HoD Approval:** {row['hod_approval']}")
                        st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"Feedback View Error: {e}")

    def main_layout(self):
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            subject_type,subject,proceed=None,None,False
            subjects_df=st.session_state.get("handling_subjects",pd.DataFrame())

            with col1:
                st.subheader("Student Feedback Entry")
                semester=st.slider("Select Semester",min_value=1,max_value=8,value=1,step=1)

                if subjects_df.empty:
                    st.warning("No subjects are assigned to this faculty.")
                else:
                    semester_df=subjects_df[subjects_df["subject_semister"]==semester]

                    if semester_df.empty:
                        st.info("You do not handle any subject in this semester.")
                    else:
                        subject_type=st.pills("Select Subject Type",semester_df["subject_type"].dropna().unique().tolist(),selection_mode="single")

                        if subject_type:
                            subject_df=semester_df[semester_df["subject_type"]==subject_type]
                            subject=st.pills("Select Subject",subject_df["subject_name"].dropna().unique().tolist(),selection_mode="single")

                            if st.toggle("Check",key="students_feedback_check"):
                                if not subject:st.warning("Please select a subject.")
                                else:
                                    proceed=self.checkDocument(semester,subject_type,subject)
                                    if proceed:st.success("Subject assignment verified.")
                                    else:st.error("You are not assigned to this subject.")

            with col2:
                if proceed:
                    st.subheader("Feedback Details")
                    feed_back_score=st.number_input("Enter Feedback Score",min_value=0,max_value=100,value=0,step=1)
                    awarded_credits=self.calculateCredits(feed_back_score)
                    st.info(f"Awarded Credits: {awarded_credits}")

                    if st.toggle("Add Entry",key="students_feedback_add_entry"):
                        df=pd.DataFrame([{"subject_name":subject,"subject_semester":semester,"subject_type":subject_type,"feed_back_score":feed_back_score,"awarded_credits":awarded_credits}])
                        if self.insertDocuments(df):st.success("Student Feedback Added Successfully.")
                        else:st.warning("Student Feedback Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()