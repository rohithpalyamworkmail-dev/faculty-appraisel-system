import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class studentSeminarWorkshopConference:
    def __init__(self):
        self.db=ActivityDatabase("seminar_workshop_conference_symposium_by_students")

    def calculateCredits(self,students,participation_type,result,prize_position):
        count=len(students)
        if participation_type=="National":
            if result=="Prize Winning":return count*{1:2,2:1,3:0.5}.get(prize_position,0)
            return round(count*0.1,3)
        if participation_type=="International":
            if result=="Prize Winning":return count*{1:3,2:2,3:1}.get(prize_position,0)
            return count*0.2
        return 0

    def getStudents(self,batch=None):
        df=st.session_state.get("mentees_list",pd.DataFrame())
        if df.empty:return []
        if batch is not None:df=df[df["student_batch"].astype(str)==str(batch)]
        return [f"{row['student_name']}-{row['student_roll_number']}" for _,row in df.iterrows()]

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns="name_roll_number,batch,participated_in,result,participation_type,team_name,proof_url,prize_position,awarded_credits"
            df=self.db.editable_dataframe(columns)
            if df.empty:
                st.info("No Seminar/Workshop/Conference entries are available for editing.")
                return

            mentees=st.session_state.get("mentees_list",pd.DataFrame())
            batches=mentees["student_batch"].dropna().astype(str).unique().tolist() if not mentees.empty else []
            students=self.getStudents()
            df["name_roll_number"]=df["name_roll_number"].fillna("").apply(lambda x:[i.strip() for i in str(x).split(",") if i.strip()])
            df["prize_position"]=df.apply(lambda r:0 if r["result"]=="Participation" else int(r["prize_position"] or 0),axis=1)

            config={"name_roll_number":st.column_config.MultiselectColumn("Students",options=students,required=True),"batch":st.column_config.SelectboxColumn("Batch",options=batches,required=True),"participated_in":st.column_config.SelectboxColumn("Participated In",options=["seminar","workshop","symposium","conference"],required=True),"result":st.column_config.SelectboxColumn("Result",options=["Participation","Prize Winning"],required=True),"participation_type":st.column_config.SelectboxColumn("Participation Type",options=["National","International"],required=True),"team_name":"Team Name","proof_url":"Proof URL","prize_position":st.column_config.SelectboxColumn("Prize Position",options=[0,1,2,3],required=True),"awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits","batch"],column_config=config,key="student_seminar_editor")

            if st.toggle("Update",key="student_seminar_update"):
                rows=[]
                for _,row in edited_df.iterrows():
                    students=row["name_roll_number"] if isinstance(row["name_roll_number"],list) else [x.strip() for x in str(row["name_roll_number"]).split(",") if x.strip()]
                    result=row["result"];position=0 if result=="Participation" else int(row["prize_position"] or 0)
                    credits=self.calculateCredits(students,row["participation_type"],result,position)
                    rows.append({"name_roll_number":",".join(students),"batch":row["batch"],"participated_in":row["participated_in"],"result":result,"participation_type":row["participation_type"],"team_name":row["team_name"],"proof_url":row["proof_url"],"prize_position":position,"awarded_credits":credits})

                if self.db.replace_pending(pd.DataFrame(rows)):st.success("Seminar/Workshop/Conference Updated Successfully.")
                else:st.warning("Update Failed.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="name_roll_number,batch,participated_in,result,participation_type,team_name,proof_url,prize_position,awarded_credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)
            if df.empty:
                st.info("No Seminar/Workshop/Conference entries found.")
                return

            st.subheader("Student Seminar / Workshop / Conference")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["participated_in"]).title())
                    st.write(f"**Students:** {row['name_roll_number']}")
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Result:** {row['result']}")
                    st.write(f"**Participation Type:** {row['participation_type']}")
                    if row["result"]=="Prize Winning":st.write(f"**Prize Position:** {row['prize_position']}")
                    st.write(f"**Team Name:** {row['team_name']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")
                    col1,col2,col3=st.columns(3)
                    with col1:st.write(f"**Awarded Credits:** {row['awarded_credits']}")
                    with col2:st.write(f"**HoD Approval:** {row['hod_approval']}")
                    with col3:st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        st.subheader("Student Seminar / Workshop / Conference")
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            proceed=False

            with col1:
                mentees=st.session_state.get("mentees_list",pd.DataFrame())
                if mentees.empty:
                    st.warning("No mentees are assigned to this faculty.")
                    return

                batches=mentees["student_batch"].dropna().astype(str).unique().tolist()
                selected_batch=st.pills("Select Batch",batches,selection_mode="single")
                selected_students=st.multiselect("Select Students",self.getStudents(selected_batch)) if selected_batch else []
                result=st.pills("Result",["Participation","Prize Winning"],selection_mode="single")
                prize_position=st.selectbox("Prize Position",[1,2,3]) if result=="Prize Winning" else 0
                participated_in=st.pills("Participated In",["seminar","workshop","symposium","conference"],selection_mode="single")
                participation_type=st.pills("Participation Type",["National","International"],selection_mode="single")
                team_name=st.text_input("Team Name")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="student_seminar_check"):
                    if not selected_batch:st.warning("Please select a Batch.")
                    elif not selected_students:st.warning("Please select at least one Student.")
                    elif not result:st.warning("Please select the Result.")
                    elif not participated_in:st.warning("Please select what the students participated in.")
                    elif not participation_type:st.warning("Please select Participation Type.")
                    elif not team_name:st.warning("Please enter the Team Name.")
                    elif not proof_url:st.warning("Please enter the Proof URL.")
                    else:proceed=True;st.success("Details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(selected_students,participation_type,result,prize_position)
                    st.subheader("Entry Details")
                    st.write(f"**Students:** {', '.join(selected_students)}")
                    st.write(f"**Participated In:** {participated_in}")
                    st.write(f"**Result:** {result}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="student_seminar_add_entry"):
                        df=pd.DataFrame([{"name_roll_number":",".join(selected_students),"batch":selected_batch,"participated_in":participated_in,"result":result,"participation_type":participation_type,"team_name":team_name,"proof_url":proof_url,"prize_position":prize_position,"awarded_credits":credits}])
                        if self.insertDocuments(df):st.success("Entry Added Successfully.")
                        else:st.warning("Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()