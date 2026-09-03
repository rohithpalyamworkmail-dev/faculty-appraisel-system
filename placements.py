import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class placements:
    def __init__(self):
        self.db=ActivityDatabase("placements")

    def calculateCredits(self,students,package):
        count=len(students)
        if package>=7:return count*3
        if package>=5:return count*2
        if package>=4:return count*1.5
        if package>=3:return count
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
            columns="company,package,student_names_roll_numbers,batch,proof_url,description,awarded_credits"
            df=self.db.editable_dataframe(columns)
            if df.empty:
                st.info("No Placement entries are available for editing.")
                return

            students=self.getStudents()
            df["student_names_roll_numbers"]=df["student_names_roll_numbers"].fillna("").apply(lambda x:[i.strip() for i in str(x).split(",") if i.strip()])

            config={"company":"Company","package":st.column_config.NumberColumn("Package (LPA)",min_value=0.0,step=0.1,required=True),"student_names_roll_numbers":st.column_config.MultiselectColumn("Students",options=students,required=True),"batch":"Batch","proof_url":"Proof URL","description":"Description","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["batch","awarded_credits"],column_config=config,key="placements_editor")

            if st.toggle("Update",key="placements_update"):
                rows=[]
                for _,row in edited_df.iterrows():
                    selected=row["student_names_roll_numbers"] if isinstance(row["student_names_roll_numbers"],list) else [x.strip() for x in str(row["student_names_roll_numbers"]).split(",") if x.strip()]
                    package=float(row["package"])
                    rows.append({"company":row["company"],"package":package,"student_names_roll_numbers":",".join(selected),"batch":row["batch"],"proof_url":row["proof_url"],"description":row["description"],"awarded_credits":self.calculateCredits(selected,package)})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Placement Entries Updated Successfully.")
                else:st.warning("Placement Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="company,package,student_names_roll_numbers,batch,proof_url,description,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)
            if df.empty:
                st.info("No Placement entries found.")
                return

            st.subheader("Placements")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["company"]))
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Students:** {row['student_names_roll_numbers']}")
                    st.write(f"**Package:** {row['package']} LPA")
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
                st.subheader("Placement Entry")
                mentees=st.session_state.get("mentees_list",pd.DataFrame())

                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                selected_students=st.multiselect("Select Students",self.getStudents(selected_batch)) if selected_batch else []
                company=st.text_input("Company")
                package=st.number_input("Package (LPA)",min_value=0.0,step=0.1)
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="placements_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not selected_students:st.warning("Please select at least one Student.")
                    elif not company:st.warning("Please enter Company Name.")
                    elif package<=0:st.warning("Please enter a valid Package.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Placement details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(selected_students,package)
                    st.subheader("Placement Details")
                    st.write(f"**Company:** {company}")
                    st.write(f"**Package:** {package} LPA")
                    st.write(f"**Students:** {', '.join(selected_students)}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="placements_add"):
                        df=pd.DataFrame([{"company":company,"package":package,"student_names_roll_numbers":",".join(selected_students),"batch":selected_batch,"proof_url":proof_url,"description":description,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("Placement Entry Added Successfully.")
                        else:st.warning("Placement Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()