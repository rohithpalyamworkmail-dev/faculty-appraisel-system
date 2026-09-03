import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class onlineCertifications:
    def __init__(self):
        self.db=ActivityDatabase("online_certifications")

    def calculateCredits(self,certification_type):
        return 2 if certification_type in ["NPTEL","MNC"] else 1

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("certification_name,certification_type,certification_company,description,duration,proof_url,awarded_credits")
            if df.empty:
                st.info("No online certification entries are available for editing.")
                return

            config={"certification_name":"Certification Name","certification_type":st.column_config.SelectboxColumn("Certification Type",options=["NPTEL","MNC","Other"],required=True),"certification_company":"Company","description":"Description","duration":st.column_config.NumberColumn("Duration",min_value=1,step=1),"proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="online_certification_editor")

            if st.toggle("Update",key="online_certification_update"):
                edited_df["certification_company"]=edited_df.apply(lambda r:"IITs" if r["certification_type"]=="NPTEL" else r["certification_company"],axis=1)
                edited_df["awarded_credits"]=edited_df["certification_type"].apply(self.calculateCredits)
                if self.db.replace_pending(edited_df):st.success("Online Certifications Updated Successfully.")
                else:st.warning("Online Certifications Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("certification_name,certification_type,certification_company,description,duration,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No online certifications found.")
                return

            st.subheader("Online Certifications")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["certification_name"]))
                    st.write(f"**Type:** {row['certification_type']}")
                    st.write(f"**Company:** {row['certification_company']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Duration:** {row['duration']}")
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
                st.subheader("Online Certification")
                certification_type=st.pills("Certification Type",["NPTEL","MNC","Other"],selection_mode="single")
                company="IITs" if certification_type=="NPTEL" else ""
                if certification_type in ["MNC","Other"]:company=st.text_input("Company")
                description=st.text_area("Description")
                certification_name=st.text_input("Certification Name")
                duration=st.number_input("Duration",min_value=0,step=1)
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="online_certification_check"):
                    if not certification_type:st.warning("Please select Certification Type.")
                    elif certification_type in ["MNC","Other"] and not company:st.warning("Please enter the Company.")
                    elif not certification_name:st.warning("Please enter Certification Name.")
                    elif not description:st.warning("Please enter Description.")
                    elif duration<=0:st.warning("Please enter a valid Duration.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Certification details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(certification_type)
                    st.subheader("Certification Details")
                    st.write(f"**Certification:** {certification_name}")
                    st.write(f"**Type:** {certification_type}")
                    st.write(f"**Company:** {company}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="online_certification_add"):
                        df=pd.DataFrame([{"certification_name":certification_name,"certification_type":certification_type,"certification_company":company,"description":description,"duration":duration,"proof_url":proof_url,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("Online Certification Added Successfully.")
                        else:st.warning("Online Certification Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()