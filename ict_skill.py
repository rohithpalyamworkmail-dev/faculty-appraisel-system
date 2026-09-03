import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class ictSkillRack:
    def __init__(self):
        self.db=ActivityDatabase("ict_skill_rack")

    def calculateCredits(self,target):
        if target==">90%":return 2
        if target=="80 to 89.99%":return 1.5
        if target=="70 to 79.99%":return 1
        return 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("ict_skill_rack_target,proof_url,awarded_credits")
            if df.empty:
                st.info("No ICT / Skill Rack entries are available for editing.")
                return

            config={"ict_skill_rack_target":st.column_config.SelectboxColumn("ICT / Skill Rack Target",options=[">90%","80 to 89.99%","70 to 79.99%"],required=True),"proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="ict_skill_rack_editor")

            if st.toggle("Update",key="ict_skill_rack_update"):
                edited_df["awarded_credits"]=edited_df["ict_skill_rack_target"].apply(self.calculateCredits)
                if self.db.replace_pending(edited_df):st.success("ICT / Skill Rack Entries Updated Successfully.")
                else:st.warning("ICT / Skill Rack Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("ict_skill_rack_target,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No ICT / Skill Rack entries found.")
                return

            st.subheader("ICT / Skill Rack Target")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["ict_skill_rack_target"]))
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
                st.subheader("ICT / Skill Rack Target")
                target=st.pills("Select ICT / Skill Rack Target",[">90%","80 to 89.99%","70 to 79.99%"],selection_mode="single")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="ict_skill_rack_check"):
                    if not target:st.warning("Please select ICT / Skill Rack Target.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(target)
                    st.subheader("ICT / Skill Rack Details")
                    st.write(f"**Target:** {target}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="ict_skill_rack_add"):
                        df=pd.DataFrame([{"ict_skill_rack_target":target,"proof_url":proof_url,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("ICT / Skill Rack Entry Added Successfully.")
                        else:st.warning("ICT / Skill Rack Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()