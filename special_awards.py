import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class specialAwards:
    def __init__(self):
        self.db=ActivityDatabase("special_awards")

    def insertDocuments(self,df):
        df=df.copy();df["awarded_credits"]=2
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("award_name,award_received_from,issuer_name,description,proof_url,awarded_credits")
            if df.empty:
                st.info("No Special Award entries are available for editing.")
                return

            config={"award_name":"Award Name","award_received_from":st.column_config.SelectboxColumn("Award Received From",options=["Institute","Company","Societies","Organization"],required=True),"issuer_name":"Issuer Name","description":"Description","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="special_awards_editor")

            if st.toggle("Update",key="special_awards_update"):
                edited_df["awarded_credits"]=2
                if self.db.replace_pending(edited_df):st.success("Special Awards Updated Successfully.")
                else:st.warning("Special Awards Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("award_name,award_received_from,issuer_name,description,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No Special Awards Found.")
                return

            st.subheader("Special Awards")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["award_name"]))
                    st.write(f"**Award Received From:** {row['award_received_from']}")
                    st.write(f"**Issuer Name:** {row['issuer_name']}")
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
                st.subheader("Special Award Entry")
                award_name=st.text_input("Award Name")
                award_received_from=st.pills("Award Received From",["Institute","Company","Societies","Organization"],selection_mode="single")
                issuer_name=st.text_input("Issuer Name")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="special_awards_check"):
                    if not award_name:st.warning("Please enter Award Name.")
                    elif not award_received_from:st.warning("Please select Award Received From.")
                    elif not issuer_name:st.warning("Please enter Issuer Name.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Award details verified.")

            with col2:
                if proceed:
                    st.subheader("Award Details")
                    st.write(f"**Award:** {award_name}")
                    st.write(f"**Received From:** {award_received_from}")
                    st.write(f"**Issuer:** {issuer_name}")
                    st.info("Awarded Credits: 2")

                    if st.toggle("Add Entry",key="special_awards_add"):
                        df=pd.DataFrame([{"award_name":award_name,"award_received_from":award_received_from,"issuer_name":issuer_name,"description":description,"proof_url":proof_url,"awarded_credits":2}])
                        if self.insertDocuments(df):st.success("Special Award Added Successfully.")
                        else:st.warning("Special Award Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()