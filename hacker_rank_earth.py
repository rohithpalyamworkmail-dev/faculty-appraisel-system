import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class hackerRankEarth:
    def __init__(self):
        self.db=ActivityDatabase("coding_data")

    def calculateCredits(self,number_of_problems_solved,coding_type):
        if coding_type=="computing":
            if 50<=number_of_problems_solved<100:return 1
            if 100<=number_of_problems_solved<=150:return 2
        if coding_type=="non computing":
            if 50<=number_of_problems_solved<100:return 2
            if 100<=number_of_problems_solved<=150:return 3
        return 0

    def createTable(self,connection=None):
        return True

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def getStudents(self,batch=None):
        df=st.session_state.get("mentees_list",pd.DataFrame())
        if df.empty:return []
        if batch is not None:df=df[df["student_batch"].astype(str)==str(batch)]
        return [f"{row['student_name']}-{row['student_roll_number']}" for _,row in df.iterrows()]

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("batch,student_name_roll_number,platform,number_of_problems_solved,type,credits")
            if df.empty:
                st.info("No HackerRank/HackerEarth entries are available for editing.")
                return

            students=self.getStudents()
            config={"batch":"Batch","student_name_roll_number":st.column_config.SelectboxColumn("Student",options=students,required=True),"platform":st.column_config.SelectboxColumn("Platform",options=["HackerRank","HackerEarth"],required=True),"number_of_problems_solved":st.column_config.NumberColumn("Problems Solved",min_value=0,step=1,required=True),"type":st.column_config.SelectboxColumn("Type",options=["computing","non computing"],required=True),"credits":"Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["batch","credits"],column_config=config,key="coding_data_editor")

            if st.toggle("Update",key="coding_data_update"):
                rows=[]
                for _,row in edited_df.iterrows():
                    problems=int(row["number_of_problems_solved"])
                    rows.append({"batch":row["batch"],"student_name_roll_number":row["student_name_roll_number"],"platform":row["platform"],"number_of_problems_solved":problems,"type":row["type"],"credits":self.calculateCredits(problems,row["type"])})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Coding Data Updated Successfully.")
                else:st.warning("Coding Data Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("faculty_name,batch,student_name_roll_number,platform,number_of_problems_solved,type,credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No HackerRank/HackerEarth entries found.")
                return

            st.subheader("HackerRank / HackerEarth")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["student_name_roll_number"]))
                    st.write(f"**Faculty Name:** {row['faculty_name']}")
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Platform:** {row['platform']}")
                    st.write(f"**Problems Solved:** {row['number_of_problems_solved']}")
                    st.write(f"**Type:** {row['type']}")
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
                st.subheader("HackerRank / HackerEarth Entry")
                mentees=st.session_state.get("mentees_list",pd.DataFrame())

                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                student_options=self.getStudents(selected_batch) if selected_batch else []
                student=st.selectbox("Select Student",student_options) if student_options else ""
                platform=st.pills("Platform",["HackerRank","HackerEarth"],selection_mode="single")
                number_of_problems_solved=st.number_input("Number Of Problems Solved",min_value=0,step=1)
                coding_type=st.pills("Type",["computing","non computing"],selection_mode="single")

                if st.toggle("Check",key="coding_data_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not student:st.warning("Please select a Student.")
                    elif not platform:st.warning("Please select a Platform.")
                    elif number_of_problems_solved<=0:st.warning("Please enter Number Of Problems Solved.")
                    elif not coding_type:st.warning("Please select Type.")
                    else:proceed=True;st.success("Coding details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(number_of_problems_solved,coding_type)
                    st.subheader("Coding Details")
                    st.write(f"**Faculty Name:** {st.session_state['faculty_name']}")
                    st.write(f"**Student:** {student}")
                    st.write(f"**Batch:** {selected_batch}")
                    st.write(f"**Platform:** {platform}")
                    st.write(f"**Problems Solved:** {number_of_problems_solved}")
                    st.write(f"**Type:** {coding_type}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="coding_data_add"):
                        df=pd.DataFrame([{"batch":selected_batch,"student_name_roll_number":student,"platform":platform,"number_of_problems_solved":number_of_problems_solved,"type":coding_type,"credits":credits}])
                        if self.insertDocuments(df):st.success("Coding Data Added Successfully.")
                        else:st.warning("Coding Data Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()