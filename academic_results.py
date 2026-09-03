import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class academicResults:
    def __init__(self):
        self.db=ActivityDatabase("academic_results")

    def calculateCredits(self,pass_percent):
        if pass_percent==100:return 10
        if pass_percent>=95:return 9
        if pass_percent>=90:return 8
        if pass_percent>=80:return 7
        if pass_percent>=70:return 5
        if pass_percent>=60:return 2
        return 0

    def checkDocument(self,semister,subject_type,subject,selected_sections):
        try:
            df=st.session_state.get("handling_subjects",pd.DataFrame())
            if df.empty:return False
            data=df[(df["subject_semister"]==semister)&(df["subject_type"]==subject_type)&(df["subject_name"]==subject)]
            if data.empty:return False
            selected={x.strip() for x in str(selected_sections).split(",") if x.strip()}
            for _,row in data.iterrows():
                available={x.strip() for x in str(row["alloted_section"]).split(",") if x.strip()}
                if selected.issubset(available):return True
            return False
        except Exception as e:
            st.error(f"Document Check Error: {e}")
            return False

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns="subject_name,subject_code,subject_semister,subject_sections,pass_percent,subject_credits,awarded_credits"
            df=self.db.editable_dataframe(columns)
            if df.empty:
                st.info("No academic result entries are available for editing.")
                return

            config={"subject_name":"Subject","subject_code":"Subject Code","subject_semister":"Semester","subject_sections":"Sections","pass_percent":st.column_config.NumberColumn("Pass Percent",min_value=0,max_value=100,step=0.1),"subject_credits":"Subject Credits","awarded_credits":"Awarded Credits"}
            disabled=["subject_name","subject_code","subject_credits","awarded_credits","subject_semister","subject_sections"]
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=disabled,column_config=config,key="academic_results_editor")

            if st.toggle("Update",key="academic_results_update"):
                edited_df["awarded_credits"]=edited_df["pass_percent"].apply(self.calculateCredits)
                edited_df=edited_df[["subject_name","subject_code","subject_semister","subject_sections","pass_percent","subject_credits","awarded_credits"]]
                if self.db.replace_pending(edited_df):st.success("Academic Results Updated Successfully.")
                else:st.warning("Academic Results Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="subject_name,subject_code,subject_semister,subject_sections,pass_percent,subject_credits,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)
            if df.empty:
                st.info("No Academic Results Found.")
                return

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["subject_name"]),divider=True,text_alignment="center")
                    col1,col2,col3=st.columns(3)
                    with col1:
                        st.write(f"**Subject Code:** {row['subject_code']}")
                        st.write(f"**Semester:** {row['subject_semister']}")
                        st.write(f"**Sections:** {row['subject_sections']}")
                    with col2:
                        st.write(f"**Subject Credits:** {row['subject_credits']}")
                        st.write(f"**Pass Percentage:** {row['pass_percent']}%")
                        st.write(f"**Awarded Credits:** {row['awarded_credits']}")
                    with col3:
                        st.write(f"**HoD Approval:** {row['hod_approval']}")
                        st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            subject_type,selected_sections,subject,proceed=None,"",None,False
            subjects_df=st.session_state.get("handling_subjects",pd.DataFrame())

            with col1:
                st.subheader("Academic Result Entry")
                semister=st.slider("Select Semister",min_value=1,max_value=8,value=1,step=1)

                if subjects_df.empty:
                    st.warning("No subjects are assigned to this faculty.")
                    return

                subject_types=subjects_df["subject_type"].dropna().unique().tolist()
                subject_type=st.pills("Select Subject Type",subject_types,selection_mode="single")

                if subject_type:
                    subject_df=subjects_df[(subjects_df["subject_semister"]==semister)&(subjects_df["subject_type"]==subject_type)]
                    selected_sections=st.pills("Select Sections",["A","B","C","D","E","F","G"],selection_mode="multi")
                    if selected_sections:selected_sections=",".join(selected_sections)
                    subject=st.pills("Select Subject",subject_df["subject_name"].dropna().unique().tolist(),selection_mode="single")

                    if st.toggle("Check",key="academic_results_check"):
                        if not selected_sections:st.warning("Please select at least one section.")
                        elif not subject:st.warning("Please select a subject.")
                        else:
                            proceed=self.checkDocument(semister,subject_type,subject,selected_sections)
                            if proceed:st.success("Subject assignment verified.")
                            else:st.error("Selected subject and sections are not assigned to you.")

            with col2:
                if subject_type and selected_sections and subject and proceed:
                    st.subheader("Result Details")
                    pass_percent=st.number_input("Enter Pass Percent",min_value=0.0,max_value=100.0,value=0.0,step=0.1)
                    awarded_credits=self.calculateCredits(pass_percent)
                    st.info(f"Awarded Credits: {awarded_credits}")

                    if st.toggle("Add Entry",key="academic_results_add_entry"):
                        subject_data=subjects_df[(subjects_df["subject_semister"]==semister)&(subjects_df["subject_type"]==subject_type)&(subjects_df["subject_name"]==subject)]
                        subject_code=subject_data.iloc[0]["subject_code"] if not subject_data.empty else ""
                        subject_credits=subject_data.iloc[0]["subject_credits"] if not subject_data.empty else 0
                        df=pd.DataFrame([{"subject_name":subject,"subject_code":subject_code,"subject_semister":semister,"subject_sections":selected_sections,"pass_percent":pass_percent,"subject_credits":subject_credits,"awarded_credits":awarded_credits}])
                        if self.insertDocuments(df):st.success("Academic Result Added Successfully.")
                        else:st.warning("Academic Result Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()