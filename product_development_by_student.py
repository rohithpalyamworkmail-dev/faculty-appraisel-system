import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class productDevelopmentByStudent:
    def __init__(self):
        self.db=ActivityDatabase("product_development_by_student")

    def getStudentOptions(self,batch=None):
        mentees=st.session_state.get("mentees_list",pd.DataFrame())
        if mentees.empty:return []
        if batch is not None:mentees=mentees[mentees["student_batch"].astype(str)==str(batch)]
        return [f"{row['student_name']}-{row['student_roll_number']}" for _,row in mentees.iterrows()]

    def insertDocuments(self,df):
        df=df.copy();df["awarded_credits"]=2
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("students_names_roll_numbers,team_name,product_name,product_description,proof_url,awarded_credits")
            if df.empty:
                st.info("No Product Development entries are available for editing.")
                return

            students=self.getStudentOptions()
            df["students_names_roll_numbers"]=df["students_names_roll_numbers"].fillna("").apply(lambda x:[i.strip() for i in str(x).split(",") if i.strip()])
            config={"students_names_roll_numbers":st.column_config.MultiselectColumn("Students",options=students,required=True),"team_name":"Team Name","product_name":"Product Name","product_description":"Product Description","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="product_development_editor")

            if st.toggle("Update",key="product_development_update"):
                edited_df["students_names_roll_numbers"]=edited_df["students_names_roll_numbers"].apply(lambda x:",".join(x) if isinstance(x,list) else str(x))
                edited_df["awarded_credits"]=2
                if self.db.replace_pending(edited_df):st.success("Product Development Updated Successfully.")
                else:st.warning("Product Development Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("students_names_roll_numbers,team_name,product_name,product_description,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No Product Development entries found.")
                return

            st.subheader("Product Development By Students")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["product_name"]))
                    st.write(f"**Students:** {row['students_names_roll_numbers']}")
                    st.write(f"**Team Name:** {row['team_name']}")
                    st.write(f"**Product Description:** {row['product_description']}")
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
                st.subheader("Product Development By Student")
                mentees=st.session_state.get("mentees_list",pd.DataFrame())
                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                selected_students=st.multiselect("Select Students",self.getStudentOptions(selected_batch)) if selected_batch else []
                team_name=st.text_input("Team Name")
                product_name=st.text_input("Product Name")
                product_description=st.text_area("Product Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="product_development_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not selected_students:st.warning("Please select at least one Student.")
                    elif not team_name:st.warning("Please enter the Team Name.")
                    elif not product_name:st.warning("Please enter the Product Name.")
                    elif not product_description:st.warning("Please enter the Product Description.")
                    elif not proof_url:st.warning("Please enter the Proof URL.")
                    else:proceed=True;st.success("Product Development details verified.")

            with col2:
                if proceed:
                    students=",".join(selected_students)
                    st.subheader("Product Development Details")
                    st.write(f"**Students:** {students}")
                    st.write(f"**Team Name:** {team_name}")
                    st.write(f"**Product Name:** {product_name}")
                    st.info("Awarded Credits: 2")

                    if st.toggle("Add Entry",key="product_development_add_entry"):
                        df=pd.DataFrame([{"students_names_roll_numbers":students,"team_name":team_name,"product_name":product_name,"product_description":product_description,"proof_url":proof_url,"awarded_credits":2}])
                        if self.insertDocuments(df):st.success("Product Development Added Successfully.")
                        else:st.warning("Product Development Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()