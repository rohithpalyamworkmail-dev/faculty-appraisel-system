import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class internshipsInplantTraining:
    def __init__(self):
        self.db=ActivityDatabase("internships_inplant_training")

    def calculateCredits(self,students,stipend_offered):
        return len(students)*(1 if stipend_offered else 0.25)

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
            columns="students_names_roll_numbers,batch,company_name,duration_days,stipend_offered,proof_url,awarded_credits"
            df=self.db.editable_dataframe(columns)
            if df.empty:
                st.info("No internship/in-plant training entries are available for editing.")
                return

            mentees=st.session_state.get("mentees_list",pd.DataFrame())
            students=self.getStudents()
            batches=mentees["student_batch"].dropna().astype(str).unique().tolist() if not mentees.empty else []
            df["students_names_roll_numbers"]=df["students_names_roll_numbers"].fillna("").apply(lambda x:[i.strip() for i in str(x).split(",") if i.strip()])
            df["stipend_offered"]=df["stipend_offered"].astype(bool)

            config={"students_names_roll_numbers":st.column_config.MultiselectColumn("Students",options=students,required=True),"batch":st.column_config.SelectboxColumn("Batch",options=batches,required=True),"company_name":"Company Name","duration_days":st.column_config.NumberColumn("Duration (Days)",min_value=1,step=1,required=True),"stipend_offered":st.column_config.CheckboxColumn("Stipend Offered"),"proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="internship_training_editor")

            if st.toggle("Update",key="internship_training_update"):
                rows=[]
                for _,row in edited_df.iterrows():
                    selected=row["students_names_roll_numbers"] if isinstance(row["students_names_roll_numbers"],list) else [x.strip() for x in str(row["students_names_roll_numbers"]).split(",") if x.strip()]
                    stipend=bool(row["stipend_offered"])
                    rows.append({"students_names_roll_numbers":",".join(selected),"batch":row["batch"],"company_name":row["company_name"],"duration_days":int(row["duration_days"]),"stipend_offered":int(stipend),"proof_url":row["proof_url"],"awarded_credits":self.calculateCredits(selected,stipend)})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Internship/In-Plant Training Updated Successfully.")
                else:st.warning("Update Failed.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="students_names_roll_numbers,batch,company_name,duration_days,stipend_offered,proof_url,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)
            if df.empty:
                st.info("No internship/in-plant training entries found.")
                return

            st.subheader("Internship / In-Plant Training")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["company_name"]))
                    st.write(f"**Students:** {row['students_names_roll_numbers']}")
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Duration:** {row['duration_days']} days")
                    st.write(f"**Stipend Offered:** {'Yes' if row['stipend_offered'] else 'No'}")
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
                st.subheader("Internship / In-Plant Training")
                mentees=st.session_state.get("mentees_list",pd.DataFrame())

                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                selected_students=st.multiselect("Select Students",self.getStudents(selected_batch)) if selected_batch else []
                company_name=st.text_input("Company Name")
                duration_days=st.number_input("Duration in Days",min_value=1,step=1)
                stipend_offered=st.checkbox("Stipend Offered")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="internship_training_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not selected_students:st.warning("Please select at least one Student.")
                    elif not company_name:st.warning("Please enter Company Name.")
                    elif duration_days<=0:st.warning("Please enter a valid Duration.")
                    elif not proof_url:st.warning("Please enter the Proof URL.")
                    else:proceed=True;st.success("Details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(selected_students,stipend_offered)
                    st.subheader("Training Details")
                    st.write(f"**Company:** {company_name}")
                    st.write(f"**Students:** {', '.join(selected_students)}")
                    st.write(f"**Duration:** {duration_days} days")
                    st.write(f"**Stipend Offered:** {'Yes' if stipend_offered else 'No'}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="internship_training_add"):
                        df=pd.DataFrame([{"students_names_roll_numbers":",".join(selected_students),"batch":selected_batch,"company_name":company_name,"duration_days":duration_days,"stipend_offered":int(stipend_offered),"proof_url":proof_url,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("Internship/In-Plant Training Added Successfully.")
                        else:st.warning("Internship/In-Plant Training Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()