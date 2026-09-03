import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class phdGuidance:
    def __init__(self):
        self.db=ActivityDatabase("phd_guidance")
        self.research_types=["Supervisor (Applicable In The Year Of Registration)","Scholar Registration","Scholar Completion","DC Member/Viva Voce Examiner"]

    def calculateCredits(self,research_type,external=False,internal_full_time=False,part_time=False,full_time=False):
        if research_type=="Supervisor (Applicable In The Year Of Registration)":return 3
        if research_type=="Scholar Registration":return 2 if external else 3
        if research_type=="Scholar Completion":return 4 if part_time else 5
        if research_type=="DC Member/Viva Voce Examiner":return 1
        return 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("research_type,external,internal_full_time,part_time,full_time,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No Ph.D Guidance entries are available for editing.")
                return

            for column in ["external","internal_full_time","part_time","full_time"]:df[column]=df[column].fillna(0).astype(bool)

            config={"research_type":st.column_config.SelectboxColumn("Research Type",options=self.research_types,required=True),"external":st.column_config.CheckboxColumn("External"),"internal_full_time":st.column_config.CheckboxColumn("Internal & Full Time"),"part_time":st.column_config.CheckboxColumn("Part Time"),"full_time":st.column_config.CheckboxColumn("Full Time"),"description":"Description","proof_url":st.column_config.LinkColumn("Proof URL"),"awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="phd_guidance_editor")

            if st.toggle("Update",key="phd_guidance_update"):
                rows=[]

                for _,row in edited_df.iterrows():
                    research_type=row["research_type"]
                    external=bool(row["external"]) if research_type=="Scholar Registration" else False
                    internal_full_time=bool(row["internal_full_time"]) if research_type=="Scholar Registration" else False
                    part_time=bool(row["part_time"]) if research_type=="Scholar Completion" else False
                    full_time=bool(row["full_time"]) if research_type=="Scholar Completion" else False

                    if research_type=="Scholar Registration":
                        if external:internal_full_time=False
                        elif internal_full_time:external=False

                    if research_type=="Scholar Completion":
                        if part_time:full_time=False
                        elif full_time:part_time=False

                    credits=self.calculateCredits(research_type,external,internal_full_time,part_time,full_time)
                    rows.append({"research_type":research_type,"proof_url":row["proof_url"],"description":row["description"],"external":int(external),"internal_full_time":int(internal_full_time),"part_time":int(part_time),"full_time":int(full_time),"awarded_credits":credits})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Ph.D Guidance Entries Updated Successfully.")
                else:st.warning("Ph.D Guidance Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("research_type,external,internal_full_time,part_time,full_time,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Ph.D Guidance entries found.")
                return

            st.subheader("Ph.D Guidance")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["research_type"]))

                    if row["research_type"]=="Scholar Registration":st.write(f"**Scholar Type:** {'External' if bool(row['external']) else 'Internal & Full Time'}")
                    if row["research_type"]=="Scholar Completion":st.write(f"**Scholar Type:** {'Part Time' if bool(row['part_time']) else 'Full Time'}")

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
            col1,col2=st.columns([1,1],border=True,gap="small")
            proceed=False

            with col1:
                st.subheader("Ph.D Guidance Entry")
                research_type=st.pills("Research Type",self.research_types,selection_mode="single",width="stretch")
                external=False;internal_full_time=False;part_time=False;full_time=False

                if research_type=="Scholar Registration":
                    registration_type=st.pills("Scholar Registration Type",["External","Internal & Full Time"],selection_mode="single")
                    external=registration_type=="External"
                    internal_full_time=registration_type=="Internal & Full Time"

                if research_type=="Scholar Completion":
                    completion_type=st.pills("Scholar Completion Type",["Part Time","Full Time"],selection_mode="single")
                    part_time=completion_type=="Part Time"
                    full_time=completion_type=="Full Time"

                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="phd_guidance_check"):
                    if not research_type:st.warning("Please select Research Type.")
                    elif research_type=="Scholar Registration" and not (external or internal_full_time):st.warning("Please select Scholar Registration Type.")
                    elif research_type=="Scholar Completion" and not (part_time or full_time):st.warning("Please select Scholar Completion Type.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Ph.D Guidance details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(research_type,external,internal_full_time,part_time,full_time)
                    st.subheader("Ph.D Guidance Details")
                    st.write(f"**Research Type:** {research_type}")

                    if research_type=="Scholar Registration":st.write(f"**Scholar Type:** {'External' if external else 'Internal & Full Time'}")
                    if research_type=="Scholar Completion":st.write(f"**Scholar Type:** {'Part Time' if part_time else 'Full Time'}")

                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="phd_guidance_add"):
                        df=pd.DataFrame([{"research_type":research_type,"proof_url":proof_url,"description":description,"external":int(external),"internal_full_time":int(internal_full_time),"part_time":int(part_time),"full_time":int(full_time),"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Ph.D Guidance Entry Added Successfully.")
                        else:st.warning("Ph.D Guidance Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()