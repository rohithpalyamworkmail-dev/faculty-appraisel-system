import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class eventsOrganizations:
    def __init__(self):
        self.db=ActivityDatabase("event_organizations")

    def calculateCredits(self,number_of_days):
        return number_of_days*0.5

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("event_name,organized_with,number_of_days,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No Event Organization entries are available for editing.")
                return

            config={"event_name":st.column_config.TextColumn("Event Name",required=True),"organized_with":st.column_config.TextColumn("Organized With",required=True),"number_of_days":st.column_config.NumberColumn("Number Of Days",min_value=1,step=1,required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"description":st.column_config.TextColumn("Description",required=True),"awarded_credits":st.column_config.NumberColumn("Awarded Credits")}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="event_organizations_editor")

            if st.toggle("Update",key="event_organizations_update"):
                edited_df["number_of_days"]=pd.to_numeric(edited_df["number_of_days"],errors="coerce").fillna(0).astype(int)

                if (edited_df["number_of_days"]<=0).any():
                    st.warning("Number Of Days must be greater than 0.")
                    return

                edited_df["awarded_credits"]=edited_df["number_of_days"].apply(self.calculateCredits)

                if self.db.replace_pending(edited_df):st.success("Event Organization Entries Updated Successfully.")
                else:st.warning("Event Organization Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("event_name,organized_with,number_of_days,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Event Organization entries found.")
                return

            st.subheader("Event Organizations")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["event_name"]))
                    st.write(f"**Organized With:** {row['organized_with']}")
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
                st.subheader("Event Organization Entry")
                event_name=st.text_input("Event Name")
                organized_with=st.text_input("Organized With")
                number_of_days=st.number_input("Number Of Days",min_value=1,step=1)
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="event_organizations_check"):
                    if not event_name:st.warning("Please enter Event Name.")
                    elif not organized_with:st.warning("Please enter Organized With.")
                    elif number_of_days<=0:st.warning("Please enter valid Number Of Days.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Event organization details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(number_of_days)

                    st.subheader("Event Organization Details")
                    st.write(f"**Event Name:** {event_name}")
                    st.write(f"**Organized With:** {organized_with}")
                    st.write(f"**Number Of Days:** {number_of_days}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="event_organizations_add"):
                        df=pd.DataFrame([{"event_name":event_name,"organized_with":organized_with,"number_of_days":int(number_of_days),"proof_url":proof_url,"description":description,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Event Organization Added Successfully.")
                        else:st.warning("Event Organization Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()