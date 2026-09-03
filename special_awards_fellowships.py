import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class specialAwardsFellowships:
    def __init__(self):
        self.db=ActivityDatabase("special_awards_fellowships")
        self.award_types=["Award","Fellowship"]

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("award_type,name,issued_institution,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No Special Award/Fellowship entries are available for editing.")
                return

            config={"award_type":st.column_config.SelectboxColumn("Award Type",options=self.award_types,required=True),"name":"Name","issued_institution":"Issued Institution","proof_url":"Proof URL","description":"Description","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="special_awards_fellowships_editor")

            if st.toggle("Update",key="special_awards_fellowships_update"):
                edited_df["awarded_credits"]=2

                if self.db.replace_pending(edited_df):st.success("Special Awards/Fellowships Updated Successfully.")
                else:st.warning("Special Awards/Fellowships Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("award_type,name,issued_institution,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Special Awards/Fellowships found.")
                return

            st.subheader("Special Awards & Fellowships")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["name"]))
                    st.write(f"**Type:** {row['award_type']}")
                    st.write(f"**Issued Institution:** {row['issued_institution']}")
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
                st.subheader("Special Award / Fellowship Entry")
                award_type=st.pills("Award Type",self.award_types,selection_mode="single")
                name=st.text_input("Name")
                issued_institution=st.text_input("Issued Institution")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="special_awards_fellowships_check"):
                    if not award_type:st.warning("Please select Award Type.")
                    elif not name:st.warning("Please enter Name.")
                    elif not issued_institution:st.warning("Please enter Issued Institution.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Award/Fellowship details verified.")

            with col2:
                if proceed:
                    st.subheader("Award / Fellowship Details")
                    st.write(f"**Type:** {award_type}")
                    st.write(f"**Name:** {name}")
                    st.write(f"**Issued Institution:** {issued_institution}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 2")

                    if st.toggle("Add Entry",key="special_awards_fellowships_add"):
                        df=pd.DataFrame([{"award_type":award_type,"name":name,"issued_institution":issued_institution,"proof_url":proof_url,"description":description,"awarded_credits":2}])

                        if self.insertDocuments(df):st.success("Special Award/Fellowship Added Successfully.")
                        else:st.warning("Special Award/Fellowship Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()