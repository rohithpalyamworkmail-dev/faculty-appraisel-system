import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class valueAddedCourses:
    def __init__(self):
        self.db=ActivityDatabase("value_added_courses")
        self.course_types=["Organized","Conducted"]

    def calculateCredits(self,course_type):
        return 1 if course_type=="Organized" else 2 if course_type=="Conducted" else 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("course_name,number_of_days,number_of_students,type,description,proof_url,awarded_credits")

            if df.empty:
                st.info("No Value Added Course entries are available for editing.")
                return

            config={"course_name":"Course Name","number_of_days":st.column_config.NumberColumn("Number Of Days",min_value=5,step=1,required=True),"number_of_students":st.column_config.NumberColumn("Number Of Students",min_value=25,step=1,required=True),"type":st.column_config.SelectboxColumn("Type",options=self.course_types,required=True),"description":"Description","proof_url":st.column_config.LinkColumn("Proof URL"),"awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="value_added_courses_editor")

            if st.toggle("Update",key="value_added_courses_update"):
                edited_df["number_of_days"]=pd.to_numeric(edited_df["number_of_days"],errors="coerce").fillna(0).astype(int)
                edited_df["number_of_students"]=pd.to_numeric(edited_df["number_of_students"],errors="coerce").fillna(0).astype(int)

                if (edited_df["number_of_days"]<5).any():
                    st.warning("Number Of Days must be at least 5.")
                    return

                if (edited_df["number_of_students"]<25).any():
                    st.warning("Number Of Students must be at least 25.")
                    return

                edited_df["awarded_credits"]=edited_df["type"].apply(self.calculateCredits)

                if self.db.replace_pending(edited_df):st.success("Value Added Course Entries Updated Successfully.")
                else:st.warning("Value Added Course Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("course_name,number_of_days,number_of_students,type,description,proof_url,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Value Added Course entries found.")
                return

            st.subheader("Value Added Courses")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["course_name"]))
                    st.write(f"**Type:** {row['type']}")
                    st.write(f"**Number Of Days:** {row['number_of_days']}")
                    st.write(f"**Number Of Students:** {row['number_of_students']}")
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
                st.subheader("Value Added Course Entry")
                course_name=st.text_input("Course Name")
                number_of_days=st.number_input("Number Of Days",min_value=5,step=1)
                number_of_students=st.number_input("Number Of Students",min_value=25,step=1)
                course_type=st.pills("Type",self.course_types,selection_mode="single")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="value_added_courses_check"):
                    if not course_name:st.warning("Please enter Course Name.")
                    elif number_of_days<5:st.warning("Number Of Days must be at least 5.")
                    elif number_of_students<25:st.warning("Number Of Students must be at least 25.")
                    elif not course_type:st.warning("Please select Type.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Value Added Course details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(course_type)
                    st.subheader("Value Added Course Details")
                    st.write(f"**Course Name:** {course_name}")
                    st.write(f"**Type:** {course_type}")
                    st.write(f"**Number Of Days:** {number_of_days}")
                    st.write(f"**Number Of Students:** {number_of_students}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="value_added_courses_add"):
                        df=pd.DataFrame([{"course_name":course_name,"number_of_days":int(number_of_days),"number_of_students":int(number_of_students),"type":course_type,"description":description,"proof_url":proof_url,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Value Added Course Added Successfully.")
                        else:st.warning("Value Added Course Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()