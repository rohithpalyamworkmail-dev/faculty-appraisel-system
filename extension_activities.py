import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class extensionActivities:
    def __init__(self):
        self.db=ActivityDatabase("extension_activities")

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("activity_name,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No Extension Activity entries are available for editing.")
                return

            config={"activity_name":st.column_config.TextColumn("Activity Name",required=True),"description":st.column_config.TextColumn("Description",required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"awarded_credits":st.column_config.NumberColumn("Awarded Credits")}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="extension_activities_editor")

            if st.toggle("Update",key="extension_activities_update"):
                edited_df["awarded_credits"]=2

                if self.db.replace_pending(edited_df):st.success("Extension Activities Updated Successfully.")
                else:st.warning("Extension Activities Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("activity_name,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Extension Activities found.")
                return

            st.subheader("Extension Activities")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["activity_name"]))
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
                st.subheader("Extension Activity Entry")
                activity_name=st.text_input("Activity Name")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="extension_activities_check"):
                    if not activity_name:st.warning("Please enter Activity Name.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Extension Activity details verified.")

            with col2:
                if proceed:
                    st.subheader("Extension Activity Details")
                    st.write(f"**Activity Name:** {activity_name}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 2")

                    if st.toggle("Add Entry",key="extension_activities_add"):
                        df=pd.DataFrame([{"activity_name":activity_name,"description":description,"proof_url":proof_url,"awarded_credits":2}])

                        if self.insertDocuments(df):st.success("Extension Activity Added Successfully.")
                        else:st.warning("Extension Activity Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()