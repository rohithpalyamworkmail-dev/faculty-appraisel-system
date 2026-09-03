import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class citationImpacts:
    def __init__(self):
        self.db=ActivityDatabase("citation_impacts")

    def calculateCredits(self,number_of_citations):
        return number_of_citations*0.25

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("paper_name,number_of_citations,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No Citation Impact entries are available for editing.")
                return

            config={"paper_name":"Paper Name","number_of_citations":st.column_config.NumberColumn("Number Of Citations",min_value=0,step=1,required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"description":"Description","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="citation_impacts_editor")

            if st.toggle("Update",key="citation_impacts_update"):
                edited_df["number_of_citations"]=edited_df["number_of_citations"].fillna(0).astype(int)
                edited_df["awarded_credits"]=edited_df["number_of_citations"].apply(self.calculateCredits)

                if self.db.replace_pending(edited_df):st.success("Citation Impact Entries Updated Successfully.")
                else:st.warning("Citation Impact Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("paper_name,number_of_citations,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Citation Impact entries found.")
                return

            st.subheader("Citation Impact Of Published Work")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["paper_name"]))
                    st.write(f"**Number Of Citations:** {row['number_of_citations']}")
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
                st.subheader("Citation Impact Entry")
                paper_name=st.text_input("Paper Name")
                number_of_citations=st.number_input("Number Of Citations",min_value=0,step=1)
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="citation_impacts_check"):
                    if not paper_name:st.warning("Please enter Paper Name.")
                    elif number_of_citations<0:st.warning("Number Of Citations cannot be negative.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Citation details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(number_of_citations)
                    st.subheader("Citation Impact Details")
                    st.write(f"**Paper Name:** {paper_name}")
                    st.write(f"**Number Of Citations:** {number_of_citations}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="citation_impacts_add"):
                        df=pd.DataFrame([{"paper_name":paper_name,"number_of_citations":number_of_citations,"proof_url":proof_url,"description":description,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Citation Impact Added Successfully.")
                        else:st.warning("Citation Impact Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()