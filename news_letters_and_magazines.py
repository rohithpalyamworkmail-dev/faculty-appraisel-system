import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class newsLettersAndMagazine:
    def __init__(self):
        self.db=ActivityDatabase("news_letters_and_magazines")
        self.types=["News Letter","Magazine"]

    def createTable(self):
        return True

    def duplicateEntryCheck(self,publication_type,name,description,proof_url):
        try:
            rows=self.db.rows("type,name,description,proof_url",{"type":publication_type})
            return any(row.get("name")==name and row.get("description")==description and row.get("proof_url")==proof_url for row in rows)
        except Exception as e:
            st.error(f"Duplicate Entry Check Error: {e}")
            return False

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("type,name,description,proof_url,credits")

            if df.empty:
                st.info("No News Letter / Magazine entries are available for editing.")
                return

            config={"type":st.column_config.SelectboxColumn("Type",options=self.types,required=True),"name":st.column_config.TextColumn("Name",required=True),"description":st.column_config.TextColumn("Description",required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"credits":st.column_config.NumberColumn("Credits")}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["credits"],column_config=config,key="news_letters_and_magazines_editor")

            if st.toggle("Update",key="news_letters_and_magazines_update"):
                edited_df["credits"]=2

                if self.db.replace_pending(edited_df):st.success("News Letter / Magazine Entries Updated Successfully.")
                else:st.warning("News Letter / Magazine Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("type,name,description,proof_url,credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No News Letter / Magazine entries found.")
                return

            st.subheader("News Letters And Magazines")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["name"]),divider=True,text_alignment="center")
                    st.write(f"**Type:** {row['type']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")

                    col1,col2,col3=st.columns(3)
                    with col1:st.write(f"**Credits:** {row['credits']}")
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
                st.subheader("News Letter / Magazine Entry")
                publication_type=st.radio("Type",self.types,horizontal=True,index=None)
                name=st.text_input("Name")
                description=st.text_input("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="news_letters_and_magazines_check"):
                    if not publication_type:st.warning("Please select Type.")
                    elif not name:st.warning("Please enter Name.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Details verified.")

            with col2:
                if proceed:
                    st.subheader("Publication Details")
                    st.write(f"**Type:** {publication_type}")
                    st.write(f"**Name:** {name}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Credits: 2")

                    if st.toggle("Add Entry",key="news_letters_and_magazines_add"):
                        if self.duplicateEntryCheck(publication_type,name,description,proof_url):
                            st.warning("Record Already Exists.")
                        else:
                            df=pd.DataFrame([{"type":publication_type,"name":name,"description":description,"proof_url":proof_url,"credits":2}])

                            if self.insertDocuments(df):st.success("News Letter / Magazine Added Successfully.")
                            else:st.warning("News Letter / Magazine Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()