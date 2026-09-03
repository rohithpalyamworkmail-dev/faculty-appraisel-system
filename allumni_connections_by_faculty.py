import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase
from database import get_rows

class alumni:
    def __init__(self):
        self.db=ActivityDatabase("alumni_connection_by_faculties")
        self.types=["Guest Lecture/Mock Interview","Industry Oriented Training","Startups/MoU/Centre of Excellence"]

    def createTable(self):
        return True

    def getBatches(self):
        try:
            rows=get_rows("alumni",{"department":st.session_state["department"]},"student_batch")
            batches=list({str(row["student_batch"]).strip() for row in rows if row.get("student_batch")})
            return sorted(batches,key=lambda x:int(x.split("-")[0]) if x.split("-")[0].isdigit() else 0)
        except Exception as e:
            st.error(f"Batch Fetch Error: {e}")
            return []

    def getStudents(self,selected_batches=None):
        try:
            if not selected_batches:return []

            alumni_rows=get_rows("alumni",{"department":st.session_state["department"]},"student_roll_number,student_batch")
            alumni_rows=[row for row in alumni_rows if row.get("student_batch") in selected_batches]

            if not alumni_rows:return []

            student_rows=get_rows("students",{"department":st.session_state["department"]},"student_name,student_roll_number")
            student_names={str(row.get("student_roll_number")):row.get("student_name") for row in student_rows}

            result=[]
            for row in alumni_rows:
                roll=str(row.get("student_roll_number",""))
                name=student_names.get(roll)
                result.append(f"{name}-{roll}" if name else roll)

            return list(dict.fromkeys(result))
        except Exception as e:
            st.error(f"Alumni Fetch Error: {e}")
            return []

    def calculateCredits(self,activity_type,selected_batches):
        batches=self.getBatches()
        recent_batches=batches[-2:] if len(batches)>=2 else batches
        current=any(batch in recent_batches for batch in selected_batches)
        current_credits={"Guest Lecture/Mock Interview":0.5,"Industry Oriented Training":1.5,"Startups/MoU/Centre of Excellence":2}
        previous_credits={"Guest Lecture/Mock Interview":0.25,"Industry Oriented Training":1,"Startups/MoU/Centre of Excellence":1}
        return current_credits.get(activity_type,0) if current else previous_credits.get(activity_type,0)

    def duplicateEntryCheck(self,activity_type,batch,students,title,description,proof_url):
        try:
            rows=self.db.rows("type,batch,student_name_roll_numbers,title,description,proof_url",{"type":activity_type})

            for row in rows:
                if row.get("batch")==batch and row.get("student_name_roll_numbers")==students and row.get("title")==title and row.get("description")==description and row.get("proof_url")==proof_url:return True

            return False
        except Exception as e:
            st.error(f"Duplicate Entry Check Error: {e}")
            return False

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def _to_list(self,value):
        if isinstance(value,list):return value
        if isinstance(value,tuple):return list(value)
        if value is None:return []
        try:
            if pd.isna(value):return []
        except:pass
        return [item.strip() for item in str(value).split(",") if item.strip()]

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("type,batch,student_name_roll_numbers,title,description,proof_url,credits")

            if df.empty:
                st.info("No Alumni Connection entries are available for editing.")
                return

            batches=self.getBatches()
            all_students=self.getStudents(batches)

            df["batch"]=df["batch"].apply(self._to_list)
            df["student_name_roll_numbers"]=df["student_name_roll_numbers"].apply(self._to_list)

            config={"type":st.column_config.SelectboxColumn("Type",options=self.types,required=True),"batch":st.column_config.MultiselectColumn("Batches",options=batches,required=True),"student_name_roll_numbers":st.column_config.MultiselectColumn("Alumni",options=all_students,required=True),"title":st.column_config.TextColumn("Title",required=True),"description":st.column_config.TextColumn("Description",required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"credits":st.column_config.NumberColumn("Credits")}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["credits"],column_config=config,key="alumni_connection_editor")

            if st.toggle("Update",key="alumni_connection_update"):
                rows=[]

                for _,row in edited_df.iterrows():
                    selected_batches=self._to_list(row["batch"])
                    selected_students=self._to_list(row["student_name_roll_numbers"])

                    if not selected_batches or not selected_students:
                        st.warning("Every entry must contain at least one Batch and one Alumni.")
                        return

                    rows.append({"type":row["type"],"batch":",".join(selected_batches),"student_name_roll_numbers":",".join(selected_students),"title":row["title"],"credits":self.calculateCredits(row["type"],selected_batches),"description":row["description"],"proof_url":row["proof_url"]})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Alumni Connection Entries Updated Successfully.")
                else:st.warning("Alumni Connection Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("type,batch,student_name_roll_numbers,title,credits,description,proof_url,hod_approval,admin_approval")

            if df.empty:
                st.info("No Alumni Connection Entries Found.")
                return

            st.subheader("Alumni Connection")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["title"]),divider=True,text_alignment="center")
                    st.write(f"**Type:** {row['type']}")
                    st.write(f"**Batches:** {row['batch']}")
                    st.write(f"**Alumni:** {row['student_name_roll_numbers']}")
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
            col1,col2=st.columns([1,1],border=True,gap="small")
            proceed=False

            with col1:
                st.subheader("Alumni Connection Entry")
                batches=self.getBatches()

                if not batches:
                    st.warning("No Alumni Batches Are Available.")
                    return

                selected_batches=st.pills("Select Batches",batches,selection_mode="multi",key="alumni_connection_batches")
                selected_students=[]

                if selected_batches:
                    student_options=self.getStudents(selected_batches)
                    selected_students=st.multiselect("Select Alumni",student_options,key="alumni_connection_students")

                activity_type=st.pills("Select Type",self.types,selection_mode="single",key="alumni_connection_type")
                title=st.text_input("Title",key="alumni_connection_title")
                description=st.text_area("Description",key="alumni_connection_description")
                proof_url=st.text_input("Proof URL",key="alumni_connection_proof")

                if st.toggle("Check",key="alumni_connection_check"):
                    if not selected_batches:st.warning("Please Select At Least One Batch.")
                    elif not selected_students:st.warning("Please Select At Least One Alumni.")
                    elif not activity_type:st.warning("Please Select Activity Type.")
                    elif not title:st.warning("Please Enter Title.")
                    elif not description:st.warning("Please Enter Description.")
                    elif not proof_url:st.warning("Please Enter Proof URL.")
                    else:proceed=True;st.success("Alumni Connection Details Verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(activity_type,selected_batches)
                    batches_string=",".join(selected_batches)
                    students_string=",".join(selected_students)

                    st.subheader("Alumni Connection Details")
                    st.write(f"**Type:** {activity_type}")
                    st.write(f"**Title:** {title}")
                    st.write(f"**Batches:** {batches_string}")
                    st.write(f"**Alumni:** {students_string}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="alumni_connection_add"):
                        if self.duplicateEntryCheck(activity_type,batches_string,students_string,title,description,proof_url):
                            st.warning("Record Already Exists.")
                        else:
                            df=pd.DataFrame([{"type":activity_type,"batch":batches_string,"student_name_roll_numbers":students_string,"title":title,"credits":credits,"description":description,"proof_url":proof_url}])

                            if self.insertDocuments(df):st.success("Alumni Connection Entry Added Successfully.")
                            else:st.warning("Alumni Connection Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()