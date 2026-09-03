import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class arrangingOnCampusRecruitments:
    def __init__(self):
        self.db=ActivityDatabase("on_campus_recruitments_by_faculty")

    def createTable(self):
        return True

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns="company_name,academic_year,number_of_students_placed,highest_package,average_package,approval_of_principal,approval_of_placement_cell,is_admin_approved,proof_url,credits"
            df=self.db.editable_dataframe(columns)

            if df.empty:
                st.info("No On-Campus Recruitment entries are available for editing.")
                return

            df["approval_of_principal"]=df["approval_of_principal"].fillna(0).astype(bool)
            df["approval_of_placement_cell"]=df["approval_of_placement_cell"].fillna(0).astype(bool)
            df["is_admin_approved"]=df["is_admin_approved"].fillna("no").astype(str).str.lower().eq("yes")

            config={"company_name":"Company Name","academic_year":"Academic Year","number_of_students_placed":st.column_config.NumberColumn("Students Placed",min_value=0,step=1,required=True),"highest_package":st.column_config.NumberColumn("Highest Package",min_value=0.0,step=0.1,required=True),"average_package":st.column_config.NumberColumn("Average Package",min_value=0.0,step=0.1,required=True),"approval_of_principal":st.column_config.CheckboxColumn("Principal Approval"),"approval_of_placement_cell":st.column_config.CheckboxColumn("Placement Cell Approval"),"is_admin_approved":st.column_config.CheckboxColumn("Admin Approved"),"proof_url":"Proof URL","credits":"Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["credits"],column_config=config,key="on_campus_recruitments_editor")

            if st.toggle("Update",key="on_campus_recruitments_update"):
                rows=[]

                for _,row in edited_df.iterrows():
                    highest=float(row["highest_package"])
                    average=float(row["average_package"])

                    if average>highest:
                        st.warning(f"Average Package cannot be greater than Highest Package for {row['company_name']}.")
                        return

                    rows.append({"company_name":row["company_name"],"academic_year":row["academic_year"],"number_of_students_placed":int(row["number_of_students_placed"]),"highest_package":highest,"average_package":average,"approval_of_principal":int(bool(row["approval_of_principal"])),"approval_of_placement_cell":int(bool(row["approval_of_placement_cell"])),"is_admin_approved":"yes" if bool(row["is_admin_approved"]) else "no","proof_url":row["proof_url"],"credits":3})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("On-Campus Recruitment Entries Updated Successfully.")
                else:st.warning("On-Campus Recruitment Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="company_name,academic_year,number_of_students_placed,highest_package,average_package,approval_of_principal,approval_of_placement_cell,is_admin_approved,proof_url,credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)

            if df.empty:
                st.info("No On-Campus Recruitment entries found.")
                return

            st.subheader("On-Campus Recruitments")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["company_name"]),divider=True)
                    st.write(f"**Academic Year:** {row['academic_year']}")
                    st.write(f"**Students Placed:** {row['number_of_students_placed']}")
                    st.write(f"**Highest Package:** {row['highest_package']} LPA")
                    st.write(f"**Average Package:** {row['average_package']} LPA")
                    st.write(f"**Principal Approval:** {'Yes' if bool(row['approval_of_principal']) else 'No'}")
                    st.write(f"**Placement Cell Approval:** {'Yes' if bool(row['approval_of_placement_cell']) else 'No'}")
                    st.write(f"**Admin Approved:** {'Yes' if str(row['is_admin_approved']).lower()=='yes' else 'No'}")
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
                st.subheader("Arrange On-Campus Recruitment")
                company_name=st.text_input("Company Name")
                academic_year=st.text_input("Academic Year",placeholder="2026-2027")
                number_of_students_placed=st.number_input("Number Of Students Placed",min_value=0,step=1)
                highest_package=st.number_input("Highest Package (LPA)",min_value=0.0,step=0.1)
                average_package=st.number_input("Average Package (LPA)",min_value=0.0,step=0.1)
                approval_of_principal=st.checkbox("Approval Of Principal")
                approval_of_placement_cell=st.checkbox("Approval Of Placement Cell")
                is_admin_approved=st.checkbox("Is Admin Approved")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="on_campus_recruitments_check"):
                    if not company_name:st.warning("Please enter Company Name.")
                    elif not academic_year:st.warning("Please enter Academic Year.")
                    elif number_of_students_placed<=0:st.warning("Please enter Number Of Students Placed.")
                    elif highest_package<=0:st.warning("Please enter Highest Package.")
                    elif average_package<=0:st.warning("Please enter Average Package.")
                    elif average_package>highest_package:st.warning("Average Package cannot be greater than Highest Package.")
                    elif not approval_of_principal:st.warning("Principal approval is required.")
                    elif not approval_of_placement_cell:st.warning("Placement Cell approval is required.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Recruitment details verified.")

            with col2:
                if proceed:
                    st.subheader("Recruitment Details")
                    st.write(f"**Company:** {company_name}")
                    st.write(f"**Academic Year:** {academic_year}")
                    st.write(f"**Students Placed:** {number_of_students_placed}")
                    st.write(f"**Highest Package:** {highest_package} LPA")
                    st.write(f"**Average Package:** {average_package} LPA")
                    st.write(f"**Principal Approval:** {'Yes' if approval_of_principal else 'No'}")
                    st.write(f"**Placement Cell Approval:** {'Yes' if approval_of_placement_cell else 'No'}")
                    st.write(f"**Admin Approved:** {'Yes' if is_admin_approved else 'No'}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 3")

                    if st.toggle("Add Entry",key="on_campus_recruitments_add"):
                        df=pd.DataFrame([{"credits":3,"company_name":company_name,"academic_year":academic_year,"number_of_students_placed":int(number_of_students_placed),"highest_package":highest_package,"average_package":average_package,"approval_of_principal":int(approval_of_principal),"approval_of_placement_cell":int(approval_of_placement_cell),"is_admin_approved":"yes" if is_admin_approved else "no","proof_url":proof_url}])

                        if self.insertDocuments(df):st.success("On-Campus Recruitment Added Successfully.")
                        else:st.warning("On-Campus Recruitment Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()