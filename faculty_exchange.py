import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class facultyExchange:
    def __init__(self):
        self.db=ActivityDatabase("faculty_exchanges")
        self.exchange_types=["National","International"]

    def calculateCredits(self,exchange_type):
        if exchange_type=="National":return 2
        if exchange_type=="International":return 5
        return 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("exchange_faculty_name,designation,employer,type,number_of_days,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No Faculty Exchange entries are available for editing.")
                return

            config={"exchange_faculty_name":"Exchange Faculty Name","designation":"Designation","employer":"Employer","type":st.column_config.SelectboxColumn("Type",options=self.exchange_types,required=True),"number_of_days":st.column_config.NumberColumn("Number Of Days",min_value=1,step=1,required=True),"proof_url":"Proof URL","description":"Description","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="faculty_exchange_editor")

            if st.toggle("Update",key="faculty_exchange_update"):
                edited_df["number_of_days"]=pd.to_numeric(edited_df["number_of_days"],errors="coerce").fillna(0).astype(int)

                if (edited_df["number_of_days"]<=0).any():
                    st.warning("Number Of Days must be greater than 0.")
                    return

                edited_df["awarded_credits"]=edited_df["type"].apply(self.calculateCredits)

                if self.db.replace_pending(edited_df):st.success("Faculty Exchange Entries Updated Successfully.")
                else:st.warning("Faculty Exchange Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("exchange_faculty_name,designation,employer,type,number_of_days,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Faculty Exchange entries found.")
                return

            st.subheader("Faculty Exchanges")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["exchange_faculty_name"]))
                    st.write(f"**Designation:** {row['designation']}")
                    st.write(f"**Employer:** {row['employer']}")
                    st.write(f"**Type:** {row['type']}")
                    st.write(f"**Number Of Days:** {row['number_of_days']}")
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
                st.subheader("Faculty Exchange Entry")
                exchange_faculty_name=st.text_input("Exchange Faculty Name")
                designation=st.text_input("Designation")
                employer=st.text_input("Employer")
                exchange_type=st.pills("Type",self.exchange_types,selection_mode="single")
                number_of_days=st.number_input("Number Of Days",min_value=1,step=1)
                proof_url=st.text_input("Proof URL")
                description=st.text_area("Description")

                if st.toggle("Check",key="faculty_exchange_check"):
                    if not exchange_faculty_name:st.warning("Please enter Exchange Faculty Name.")
                    elif not designation:st.warning("Please enter Designation.")
                    elif not employer:st.warning("Please enter Employer.")
                    elif not exchange_type:st.warning("Please select Type.")
                    elif number_of_days<=0:st.warning("Please enter valid Number Of Days.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    elif not description:st.warning("Please enter Description.")
                    else:proceed=True;st.success("Faculty Exchange details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(exchange_type)
                    st.subheader("Faculty Exchange Details")
                    st.write(f"**Exchange Faculty Name:** {exchange_faculty_name}")
                    st.write(f"**Designation:** {designation}")
                    st.write(f"**Employer:** {employer}")
                    st.write(f"**Type:** {exchange_type}")
                    st.write(f"**Number Of Days:** {number_of_days}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="faculty_exchange_add"):
                        df=pd.DataFrame([{"exchange_faculty_name":exchange_faculty_name,"designation":designation,"employer":employer,"type":exchange_type,"number_of_days":int(number_of_days),"proof_url":proof_url,"description":description,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Faculty Exchange Added Successfully.")
                        else:st.warning("Faculty Exchange Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()