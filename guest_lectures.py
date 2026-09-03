import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class guestLectures:
    def __init__(self):
        self.db=ActivityDatabase("guest_lectures")
        self.institute_types=["NIRF Ranked","Only Engineering","Inter Dept"]

    def calculateCredits(self,institute_type,number_of_days):
        if institute_type=="NIRF Ranked":return number_of_days*1.5
        if institute_type=="Only Engineering":return number_of_days
        return number_of_days*0.5

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("institute_type,institution_name,number_of_days,topics_covered,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No Guest Lecture entries are available for editing.")
                return

            config={"institute_type":st.column_config.SelectboxColumn("Institute Type",options=self.institute_types,required=True),"institution_name":"Institution Name","number_of_days":st.column_config.NumberColumn("Number Of Days",min_value=1,step=1,required=True),"topics_covered":"Topics Covered","description":"Description","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="guest_lectures_editor")

            if st.toggle("Update",key="guest_lectures_update"):
                edited_df["number_of_days"]=edited_df["number_of_days"].fillna(1).astype(int)
                edited_df["awarded_credits"]=edited_df.apply(lambda row:self.calculateCredits(row["institute_type"],row["number_of_days"]),axis=1)

                if self.db.replace_pending(edited_df):st.success("Guest Lecture Entries Updated Successfully.")
                else:st.warning("Guest Lecture Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("institute_type,institution_name,number_of_days,topics_covered,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Guest Lecture entries found.")
                return

            st.subheader("Guest Lectures")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["institution_name"]))
                    st.write(f"**Institute Type:** {row['institute_type']}")
                    st.write(f"**Number Of Days:** {row['number_of_days']}")
                    st.write(f"**Topics Covered:** {row['topics_covered']}")
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
                st.subheader("Guest Lecture Entry")
                institute_type=st.pills("Institute Type",self.institute_types,selection_mode="single")
                institution_name=st.text_input("Institution Name")
                number_of_days=st.number_input("Number Of Days",min_value=1,step=1)
                topics_covered=st.text_area("Topics Covered")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="guest_lectures_check"):
                    if not institute_type:st.warning("Please select Institute Type.")
                    elif not institution_name:st.warning("Please enter Institution Name.")
                    elif number_of_days<=0:st.warning("Please enter valid Number Of Days.")
                    elif not topics_covered:st.warning("Please enter Topics Covered.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Guest Lecture details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(institute_type,number_of_days)
                    st.subheader("Guest Lecture Details")
                    st.write(f"**Institute Type:** {institute_type}")
                    st.write(f"**Institution Name:** {institution_name}")
                    st.write(f"**Number Of Days:** {number_of_days}")
                    st.write(f"**Topics Covered:** {topics_covered}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="guest_lectures_add"):
                        df=pd.DataFrame([{"institute_type":institute_type,"institution_name":institution_name,"number_of_days":int(number_of_days),"topics_covered":topics_covered,"description":description,"proof_url":proof_url,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Guest Lecture Entry Added Successfully.")
                        else:st.warning("Guest Lecture Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()