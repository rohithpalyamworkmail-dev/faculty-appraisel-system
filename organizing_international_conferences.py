import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class organizingInternationalConference:
    def __init__(self):
        self.db=ActivityDatabase("organizing_international_conference")
        self.entry_partners=["IEEE","Springer","Elsevier","Other"]
        self.editor_partners=["IEEE","Springer","Elsevier"]

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("conference_name,partner,scopused_in_index,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No International Conference entries are available for editing.")
                return

            df["scopused_in_index"]=df["scopused_in_index"].fillna(0).astype(bool)

            config={"conference_name":"Conference Name","partner":st.column_config.SelectboxColumn("Partner",options=self.editor_partners,required=True),"scopused_in_index":st.column_config.CheckboxColumn("Scopus Indexed"),"description":"Description","proof_url":st.column_config.LinkColumn("Proof URL"),"awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="organizing_international_conference_editor")

            if st.toggle("Update",key="organizing_international_conference_update"):
                edited_df["scopused_in_index"]=edited_df["scopused_in_index"].fillna(False).astype(bool).astype(int)
                edited_df["awarded_credits"]=5

                if self.db.replace_pending(edited_df):st.success("International Conference Entries Updated Successfully.")
                else:st.warning("International Conference Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("conference_name,partner,scopused_in_index,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No International Conference entries found.")
                return

            st.subheader("Organizing International Conference")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["conference_name"]))
                    st.write(f"**Partner:** {row['partner']}")
                    st.write(f"**Scopus Indexed:** {'Yes' if bool(row['scopused_in_index']) else 'No'}")
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
                st.subheader("Organizing International Conference")
                conference_name=st.text_input("Conference Name")
                partner=st.pills("Partner",self.entry_partners,selection_mode="single")
                scopused_in_index=st.checkbox("Scopus Indexed")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="organizing_international_conference_check"):
                    if not conference_name:st.warning("Please enter Conference Name.")
                    elif not partner:st.warning("Please select Partner.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Conference details verified.")

            with col2:
                if proceed:
                    st.subheader("Conference Details")
                    st.write(f"**Conference Name:** {conference_name}")
                    st.write(f"**Partner:** {partner}")
                    st.write(f"**Scopus Indexed:** {'Yes' if scopused_in_index else 'No'}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 5")

                    if st.toggle("Add Entry",key="organizing_international_conference_add"):
                        df=pd.DataFrame([{"conference_name":conference_name,"partner":partner,"scopused_in_index":int(scopused_in_index),"description":description,"proof_url":proof_url,"awarded_credits":5}])

                        if self.insertDocuments(df):st.success("International Conference Added Successfully.")
                        else:st.warning("International Conference Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()