import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class eventParticipations:
    def __init__(self):
        self.db=ActivityDatabase("nirf_event_participations")
        self.event_types=["Normal","Industrial Training/Workshop/Seminar"]

    def calculateCredits(self,event_type,number_of_days):
        if event_type=="Normal":return number_of_days*0.25
        if event_type=="Industrial Training/Workshop/Seminar":return number_of_days*0.5
        return 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("event_name,event_type,number_of_days,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No Event Participation entries are available for editing.")
                return

            config={"event_name":"Event Name","event_type":st.column_config.SelectboxColumn("Event Type",options=self.event_types,required=True),"number_of_days":st.column_config.NumberColumn("Number Of Days",min_value=1,step=1,required=True),"description":"Description","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="nirf_event_participations_editor")

            if st.toggle("Update",key="nirf_event_participations_update"):
                edited_df["number_of_days"]=edited_df["number_of_days"].fillna(1).astype(int)
                edited_df["awarded_credits"]=edited_df.apply(lambda row:self.calculateCredits(row["event_type"],row["number_of_days"]),axis=1)

                if self.db.replace_pending(edited_df):st.success("Event Participation Entries Updated Successfully.")
                else:st.warning("Event Participation Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("event_name,event_type,number_of_days,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Event Participation entries found.")
                return

            st.subheader("Event Participations")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["event_name"]))
                    st.write(f"**Event Type:** {row['event_type']}")
                    st.write(f"**Number Of Days:** {row['number_of_days']}")
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
                st.subheader("Event Participation Entry")
                event_name=st.text_input("Event Name")
                event_type=st.pills("Event Type",self.event_types,selection_mode="single")
                number_of_days=st.number_input("Number Of Days",min_value=1,step=1)
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="nirf_event_participations_check"):
                    if not event_name:st.warning("Please enter Event Name.")
                    elif not event_type:st.warning("Please select Event Type.")
                    elif number_of_days<=0:st.warning("Please enter valid Number Of Days.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Event participation details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(event_type,number_of_days)
                    st.subheader("Event Participation Details")
                    st.write(f"**Event Name:** {event_name}")
                    st.write(f"**Event Type:** {event_type}")
                    st.write(f"**Number Of Days:** {number_of_days}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="nirf_event_participations_add"):
                        df=pd.DataFrame([{"event_name":event_name,"event_type":event_type,"number_of_days":int(number_of_days),"description":description,"proof_url":proof_url,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Event Participation Added Successfully.")
                        else:st.warning("Event Participation Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()