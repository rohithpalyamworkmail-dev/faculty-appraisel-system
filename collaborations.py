import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class collaborations:
    def __init__(self):
        self.db=ActivityDatabase("collaborations_industry_institute")
        self.colloboration_types=["CoE","MoU"]
        self.colloboration_with_types=["Institues","Industry"]

    def calculateCredits(self,colloboration_type,funding):
        if colloboration_type=="CoE":return 5 if funding else 1
        if colloboration_type=="MoU":return 1
        return 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("colloboration_type,colloboration_name,description,proof_url,funding,colloboration_with,organization_name,awarded_credits")

            if df.empty:
                st.info("No Collaboration entries are available for editing.")
                return

            df["funding"]=df["funding"].fillna(0).astype(bool)

            config={"colloboration_type":st.column_config.SelectboxColumn("Collaboration Type",options=self.colloboration_types,required=True),"colloboration_name":"Collaboration Name","description":"Description","proof_url":st.column_config.LinkColumn("Proof URL"),"funding":st.column_config.CheckboxColumn("Got Funding"),"colloboration_with":st.column_config.SelectboxColumn("Collaboration With",options=self.colloboration_with_types,required=True),"organization_name":"Organization Name","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="collaborations_editor")

            if st.toggle("Update",key="collaborations_update"):
                rows=[]

                for _,row in edited_df.iterrows():
                    colloboration_type=row["colloboration_type"]
                    funding=False if colloboration_type=="MoU" else bool(row["funding"])
                    credits=self.calculateCredits(colloboration_type,funding)

                    rows.append({"colloboration_type":colloboration_type,"colloboration_name":row["colloboration_name"],"description":row["description"],"proof_url":row["proof_url"],"funding":int(funding),"colloboration_with":row["colloboration_with"],"organization_name":row["organization_name"],"awarded_credits":credits})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Collaboration Entries Updated Successfully.")
                else:st.warning("Collaboration Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("colloboration_type,colloboration_name,description,proof_url,funding,colloboration_with,organization_name,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Collaboration entries found.")
                return

            st.subheader("Industry / Institute Collaborations")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["colloboration_name"]))
                    st.write(f"**Collaboration Type:** {row['colloboration_type']}")
                    st.write(f"**Collaboration With:** {row['colloboration_with']}")
                    st.write(f"**Organization Name:** {row['organization_name']}")
                    st.write(f"**Funding:** {'Yes' if bool(row['funding']) else 'No'}")
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
                st.subheader("Industry / Institute Collaboration")
                colloboration_type=st.pills("Collaboration Type",self.colloboration_types,selection_mode="single")
                st.write("CoE Stands For 'Center Of Excellence'")
                colloboration_name=st.text_input("Collaboration Name")
                colloboration_with=st.pills("Collaboration With",self.colloboration_with_types,selection_mode="single")
                organization_name=st.text_input("Organization Name")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")
                funding=False

                if colloboration_type=="CoE":funding=st.checkbox("Got Funding")

                if colloboration_type=="MoU":
                    funding=False
                    st.info("Funding is automatically set to 0 for MoU.")

                if st.toggle("Check",key="collaborations_check"):
                    if not colloboration_type:st.warning("Please select Collaboration Type.")
                    elif not colloboration_name:st.warning("Please enter Collaboration Name.")
                    elif not colloboration_with:st.warning("Please select Collaboration With.")
                    elif not organization_name:st.warning("Please enter Organization Name.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Collaboration details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(colloboration_type,funding)
                    st.subheader("Collaboration Details")
                    st.write(f"**Collaboration Type:** {colloboration_type}")
                    st.write(f"**Collaboration Name:** {colloboration_name}")
                    st.write(f"**Collaboration With:** {colloboration_with}")
                    st.write(f"**Organization Name:** {organization_name}")
                    st.write(f"**Funding:** {'Yes' if funding else 'No'}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="collaborations_add"):
                        df=pd.DataFrame([{"colloboration_type":colloboration_type,"colloboration_name":colloboration_name,"description":description,"proof_url":proof_url,"funding":int(funding),"colloboration_with":colloboration_with,"organization_name":organization_name,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Collaboration Added Successfully.")
                        else:st.warning("Collaboration Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()