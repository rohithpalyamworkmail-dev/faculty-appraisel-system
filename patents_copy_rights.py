import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class patentCopyRights:
    def __init__(self):
        self.db=ActivityDatabase("patent_copy_rights")

    def calculateCredits(self,patent_status):
        credits={"Patent Published":2,"Copy Right Granted":1,"Patent Granted With Institution Name":5,"Patent Granted Without Institution Name":4,"Design Patent Granted With Institution Name":3,"Design Patent Granted Without Institution Name":2,"Revenue Generated From Patent":1,"Revenue Generated From Design Patent":1}
        return credits.get(patent_status,0)

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("patent_name,patent_type,patent_status,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No Patent / Copyright entries are available for editing.")
                return

            patent_types=["Patent","Copy Right","Design Patent"]
            patent_statuses=["Patent Published","Copy Right Granted","Patent Granted With Institution Name","Patent Granted Without Institution Name","Design Patent Granted With Institution Name","Design Patent Granted Without Institution Name","Revenue Generated From Patent","Revenue Generated From Design Patent"]
            config={"patent_name":"Patent / Copyright Name","patent_type":st.column_config.SelectboxColumn("Patent Type",options=patent_types,required=True),"patent_status":st.column_config.SelectboxColumn("Patent Status",options=patent_statuses,required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"description":"Description","awarded_credits":"Awarded Credits"}

            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="patent_copy_rights_editor")

            if st.toggle("Update",key="patent_copy_rights_update"):
                edited_df["awarded_credits"]=edited_df["patent_status"].apply(self.calculateCredits)

                if self.db.replace_pending(edited_df):st.success("Patent / Copyright Entries Updated Successfully.")
                else:st.warning("Patent / Copyright Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("patent_name,patent_type,patent_status,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Patent / Copyright entries found.")
                return

            st.subheader("Patents & Copyrights")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["patent_name"]))
                    st.write(f"**Type:** {row['patent_type']}")
                    st.write(f"**Status:** {row['patent_status']}")
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
            col1,col2=st.columns([1,1],border=True,gap="small")
            proceed=False

            with col1:
                st.subheader("Patent / Copyright Entry")
                patent_type=st.pills("Patent Type",["Patent","Copy Right","Design Patent"],selection_mode="single")
                patent_name=st.text_input("Patent / Copyright Name")
                patent_status=st.pills("Patent Status",["Patent Published","Copy Right Granted","Patent Granted With Institution Name","Patent Granted Without Institution Name","Design Patent Granted With Institution Name","Design Patent Granted Without Institution Name","Revenue Generated From Patent","Revenue Generated From Design Patent"],selection_mode="single")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="patent_copy_rights_check"):
                    if not patent_type:st.warning("Please select Patent Type.")
                    elif not patent_name:st.warning("Please enter Patent / Copyright Name.")
                    elif not patent_status:st.warning("Please select Patent Status.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Patent / Copyright details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(patent_status)
                    st.subheader("Patent / Copyright Details")
                    st.write(f"**Name:** {patent_name}")
                    st.write(f"**Type:** {patent_type}")
                    st.write(f"**Status:** {patent_status}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="patent_copy_rights_add"):
                        df=pd.DataFrame([{"patent_name":patent_name,"patent_type":patent_type,"patent_status":patent_status,"proof_url":proof_url,"description":description,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Patent / Copyright Entry Added Successfully.")
                        else:st.warning("Patent / Copyright Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()