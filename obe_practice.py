import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class obePractice:
    def __init__(self):
        self.db=ActivityDatabase("obe_practice")

    def calculateCredits(self,practice_type):
        return {"CDP":1,"CAP":2,"CAR":3,"CQI":4,"Self-Initiative":5}.get(practice_type,0)

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("obe_practice_type,description,proof_url,awarded_credits")
            if df.empty:
                st.info("No OBE Practice entries are available for editing.")
                return

            config={"obe_practice_type":st.column_config.SelectboxColumn("OBE Practice Type",options=["CDP","CAP","CAR","CQI","Self-Initiative"],required=True),"description":"Description","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="obe_practice_editor")

            if st.toggle("Update",key="obe_practice_update"):
                edited_df["awarded_credits"]=edited_df["obe_practice_type"].apply(self.calculateCredits)
                if self.db.replace_pending(edited_df):st.success("OBE Practice Updated Successfully.")
                else:st.warning("OBE Practice Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("obe_practice_type,description,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No OBE Practice Found.")
                return

            st.subheader("OBE Practice")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["obe_practice_type"]))
                    col1,col2=st.columns(2)
                    with col1:
                        st.write("**Description**");st.write(row["description"])
                        st.write("**Proof URL**");st.write(row["proof_url"])
                    with col2:
                        st.write(f"**Awarded Credits:** {row['awarded_credits']}")
                        st.write(f"**HoD Approval:** {row['hod_approval']}")
                        st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            practice_type=description=proof_url=None
            proceed=False

            with col1:
                st.subheader("OBE Practice Entry")
                practice_type=st.pills("Select Practice Type",["CDP","CAP","CAR","CQI","Self-Initiative"],selection_mode="single")
                st.markdown("1. CDP - Course Delivery Plan\n2. CAP - Course Assessment Plan\n3. CAR - Course Assessment Report\n4. CQI - Continuous Quality Improvement")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="obe_practice_check"):
                    if not practice_type:st.warning("Please select a Practice Type.")
                    elif not description:st.warning("Please enter the Description.")
                    elif not proof_url:st.warning("Please enter the Proof URL.")
                    else:proceed=True;st.success("OBE Practice details verified.")

            with col2:
                if proceed:
                    awarded_credits=self.calculateCredits(practice_type)
                    st.subheader("OBE Practice Details")
                    st.info(f"Awarded Credits: {awarded_credits}")

                    if st.toggle("Add Entry",key="obe_practice_add_entry"):
                        df=pd.DataFrame([{"obe_practice_type":practice_type,"description":description,"proof_url":proof_url,"awarded_credits":awarded_credits}])
                        if self.insertDocuments(df):st.success("OBE Practice Added Successfully.")
                        else:st.warning("OBE Practice Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()