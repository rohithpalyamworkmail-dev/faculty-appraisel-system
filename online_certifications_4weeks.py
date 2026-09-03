import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class onlineCertifications4Weeks:
    def __init__(self):
        self.db=ActivityDatabase("online_certifications_4weeks")
        self.certificate_types=["NPTEL","Swayam","MNC","Other"]

    def calculateCredits(self,certificate_type):
        return 1 if certificate_type=="Other" else 2

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("certificate_type,certificate_name,duration,proof_url,awarded_credits")

            if df.empty:
                st.info("No Online Certification entries are available for editing.")
                return

            config={"certificate_type":st.column_config.SelectboxColumn("Certificate Type",options=self.certificate_types,required=True),"certificate_name":"Certificate Name","duration":st.column_config.NumberColumn("Duration (Weeks)",min_value=4,step=1,required=True),"proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="online_certifications_4weeks_editor")

            if st.toggle("Update",key="online_certifications_4weeks_update"):
                edited_df["duration"]=edited_df["duration"].fillna(4).astype(int)
                edited_df["awarded_credits"]=edited_df["certificate_type"].apply(self.calculateCredits)

                if self.db.replace_pending(edited_df):st.success("Online Certifications Updated Successfully.")
                else:st.warning("Online Certifications Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("certificate_type,certificate_name,duration,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Online Certifications found.")
                return

            st.subheader("Online Certifications - Minimum 4 Weeks")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["certificate_name"]))
                    st.write(f"**Certificate Type:** {row['certificate_type']}")
                    st.write(f"**Duration:** {row['duration']} Weeks")
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
                st.subheader("Online Certification - Minimum 4 Weeks")
                certificate_type=st.pills("Certificate Type",self.certificate_types,selection_mode="single")
                certificate_name=st.text_input("Certificate Name")
                duration=st.number_input("Duration (Weeks)",min_value=4,step=1)
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="online_certifications_4weeks_check"):
                    if not certificate_type:st.warning("Please select Certificate Type.")
                    elif not certificate_name:st.warning("Please enter Certificate Name.")
                    elif duration<4:st.warning("Duration must be minimum 4 weeks.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Certification details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(certificate_type)
                    st.subheader("Certification Details")
                    st.write(f"**Certificate Type:** {certificate_type}")
                    st.write(f"**Certificate Name:** {certificate_name}")
                    st.write(f"**Duration:** {duration} Weeks")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="online_certifications_4weeks_add"):
                        df=pd.DataFrame([{"certificate_type":certificate_type,"certificate_name":certificate_name,"duration":int(duration),"proof_url":proof_url,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Online Certification Added Successfully.")
                        else:st.warning("Online Certification Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()