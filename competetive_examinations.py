import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class competetiveExaminations:
    def __init__(self):
        self.db=ActivityDatabase("competetive_examinations")

    def calculateCredits(self,students,result):
        if result=="registered":return len(students)*0.2
        if result=="cleared":return len(students)*2
        return 0

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
            columns="exam_name,result,description,proof_url,student_name_roll_numbers,batch,awarded_credits"
            df=self.db.editable_dataframe(columns)
            if df.empty:
                st.info("No Competitive Examination entries are available for editing.")
                return

            students=self.getStudents()
            df["student_name_roll_numbers"]=df["student_name_roll_numbers"].fillna("").apply(lambda x:[i.strip() for i in str(x).split(",") if i.strip()])
            config={"exam_name":"Exam Name","result":st.column_config.SelectboxColumn("Result",options=["registered","cleared"],required=True),"description":"Description","proof_url":"Proof URL","student_name_roll_numbers":st.column_config.MultiselectColumn("Students",options=students,required=True),"batch":"Batch","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["batch","awarded_credits"],column_config=config,key="competitive_examinations_editor")

            if st.toggle("Update",key="competitive_examinations_update"):
                rows=[]
                for _,row in edited_df.iterrows():
                    selected=row["student_name_roll_numbers"] if isinstance(row["student_name_roll_numbers"],list) else [x.strip() for x in str(row["student_name_roll_numbers"]).split(",") if x.strip()]
                    rows.append({"exam_name":row["exam_name"],"result":row["result"],"description":row["description"],"proof_url":row["proof_url"],"student_name_roll_numbers":",".join(selected),"batch":row["batch"],"awarded_credits":self.calculateCredits(selected,row["result"])})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Competitive Examination Entries Updated Successfully.")
                else:st.warning("Competitive Examination Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="exam_name,result,description,proof_url,student_name_roll_numbers,batch,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)
            if df.empty:
                st.info("No Competitive Examination entries found.")
                return

            st.subheader("Competitive Examinations")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["exam_name"]))
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Students:** {row['student_name_roll_numbers']}")
                    st.write(f"**Result:** {str(row['result']).title()}")
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
                st.subheader("Competitive Examination Entry")
                mentees=st.session_state.get("mentees_list",pd.DataFrame())

                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                selected_students=st.multiselect("Select Students",self.getStudents(selected_batch)) if selected_batch else []
                exam_name=st.text_input("Exam Name")
                result=st.pills("Result",["registered","cleared"],selection_mode="single")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="competitive_examinations_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not selected_students:st.warning("Please select at least one Student.")
                    elif not exam_name:st.warning("Please enter Exam Name.")
                    elif not result:st.warning("Please select Result.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(selected_students,result)
                    st.subheader("Examination Details")
                    st.write(f"**Exam:** {exam_name}")
                    st.write(f"**Result:** {result.title()}")
                    st.write(f"**Students:** {', '.join(selected_students)}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="competitive_examinations_add"):
                        df=pd.DataFrame([{"exam_name":exam_name,"result":result,"description":description,"proof_url":proof_url,"student_name_roll_numbers":",".join(selected_students),"batch":selected_batch,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("Competitive Examination Entry Added Successfully.")
                        else:st.warning("Competitive Examination Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()