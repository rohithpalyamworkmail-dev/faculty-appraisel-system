import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class memberships:
    def __init__(self):
        self.db=ActivityDatabase("membership")

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("membership_name,duration_in_years,issued_body_name,academic_year,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No Membership entries are available for editing.")
                return

            config={"membership_name":"Membership Name","duration_in_years":st.column_config.NumberColumn("Duration In Years",min_value=0.0,step=0.5,required=True),"issued_body_name":"Issued Body Name","academic_year":"Academic Year","description":"Description","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="membership_editor")

            if st.toggle("Update",key="membership_update"):
                edited_df["duration_in_years"]=pd.to_numeric(edited_df["duration_in_years"],errors="coerce").fillna(0)

                if (edited_df["duration_in_years"]<=0).any():
                    st.warning("Duration must be greater than 0.")
                    return

                edited_df["awarded_credits"]=1

                if self.db.replace_pending(edited_df):st.success("Membership Entries Updated Successfully.")
                else:st.warning("Membership Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("membership_name,duration_in_years,issued_body_name,academic_year,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Membership entries found.")
                return

            st.subheader("Memberships")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["membership_name"]))
                    st.write(f"**Duration:** {row['duration_in_years']} Years")
                    st.write(f"**Issued Body:** {row['issued_body_name']}")
                    st.write(f"**Academic Year:** {row['academic_year']}")
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
                st.subheader("Membership Entry")
                membership_name=st.text_input("Membership Name")
                duration_in_years=st.number_input("Duration In Years",min_value=0.0,step=0.5)
                issued_body_name=st.text_input("Issued Body Name")
                academic_year=st.text_input("Academic Year",placeholder="2026-2027")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="membership_check"):
                    if not membership_name:st.warning("Please enter Membership Name.")
                    elif duration_in_years<=0:st.warning("Please enter valid Duration.")
                    elif not issued_body_name:st.warning("Please enter Issued Body Name.")
                    elif not academic_year:st.warning("Please enter Academic Year.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Membership details verified.")

            with col2:
                if proceed:
                    st.subheader("Membership Details")
                    st.write(f"**Membership Name:** {membership_name}")
                    st.write(f"**Duration:** {duration_in_years} Years")
                    st.write(f"**Issued Body:** {issued_body_name}")
                    st.write(f"**Academic Year:** {academic_year}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 1")

                    if st.toggle("Add Entry",key="membership_add"):
                        df=pd.DataFrame([{"membership_name":membership_name,"duration_in_years":duration_in_years,"issued_body_name":issued_body_name,"academic_year":academic_year,"description":description,"proof_url":proof_url,"awarded_credits":1}])

                        if self.insertDocuments(df):st.success("Membership Added Successfully.")
                        else:st.warning("Membership Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()