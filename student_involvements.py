import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class studentInvolvement:
    def __init__(self):
        self.db=ActivityDatabase("student_involvements_in_startups")

    def calculateCredits(self,students):
        return len(students)*1.5

    def getStudents(self,batch=None):
        df=st.session_state.get("mentees_list",pd.DataFrame())
        if df.empty:return []
        if batch is not None:df=df[df["student_batch"].astype(str)==str(batch)]
        return [f"{row['student_name']}-{row['student_roll_number']}" for _,row in df.iterrows()]

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns="batch,student_name_roll_number,team_name,description,startup_enterpernurship_name,proof_url,awarded_credits"
            df=self.db.editable_dataframe(columns)
            if df.empty:
                st.info("No Student Involvement entries are available for editing.")
                return

            students=self.getStudents()
            df["student_name_roll_number"]=df["student_name_roll_number"].fillna("").apply(lambda x:[i.strip() for i in str(x).split(",") if i.strip()])
            config={"batch":"Batch","student_name_roll_number":st.column_config.MultiselectColumn("Students",options=students,required=True),"team_name":"Team Name","description":"Description","startup_enterpernurship_name":"Startup / Entrepreneurship Name","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["batch","awarded_credits"],column_config=config,key="student_involvement_editor")

            if st.toggle("Update",key="student_involvement_update"):
                rows=[]
                for _,row in edited_df.iterrows():
                    selected=row["student_name_roll_number"] if isinstance(row["student_name_roll_number"],list) else [x.strip() for x in str(row["student_name_roll_number"]).split(",") if x.strip()]
                    rows.append({"batch":row["batch"],"student_name_roll_number":",".join(selected),"team_name":row["team_name"],"description":row["description"],"startup_enterpernurship_name":row["startup_enterpernurship_name"],"proof_url":row["proof_url"],"awarded_credits":self.calculateCredits(selected)})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Student Involvement Updated Successfully.")
                else:st.warning("Student Involvement Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="batch,student_name_roll_number,team_name,description,startup_enterpernurship_name,proof_url,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)
            if df.empty:
                st.info("No Student Involvement entries found.")
                return

            st.subheader("Student Involvement In Startups / Entrepreneurship")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["startup_enterpernurship_name"]))
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Students:** {row['student_name_roll_number']}")
                    st.write(f"**Team Name:** {row['team_name']}")
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
                st.subheader("Student Involvement In Startups / Entrepreneurship")
                mentees=st.session_state.get("mentees_list",pd.DataFrame())

                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                selected_students=st.multiselect("Select Students",self.getStudents(selected_batch)) if selected_batch else []
                team_name=st.text_input("Team Name")
                startup_name=st.text_input("Startup / Entrepreneurship Name")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="student_involvement_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not selected_students:st.warning("Please select at least one Student.")
                    elif not team_name:st.warning("Please enter Team Name.")
                    elif not startup_name:st.warning("Please enter Startup / Entrepreneurship Name.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(selected_students)
                    st.subheader("Entry Details")
                    st.write(f"**Startup / Entrepreneurship:** {startup_name}")
                    st.write(f"**Team Name:** {team_name}")
                    st.write(f"**Students:** {', '.join(selected_students)}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="student_involvement_add"):
                        df=pd.DataFrame([{"batch":selected_batch,"student_name_roll_number":",".join(selected_students),"team_name":team_name,"description":description,"startup_enterpernurship_name":startup_name,"proof_url":proof_url,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("Student Involvement Added Successfully.")
                        else:st.warning("Student Involvement Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()