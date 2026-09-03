import pandas as pd
import streamlit as st
from database import get_rows

class examinationResults:
    def __init__(self):
        self.department=st.session_state["department"]
        self.faculty_id=st.session_state["faculty_id"]

    def getAcademicYears(self):
        try:
            rows=get_rows("examination_results_faculty",{"department":self.department},"academic_year",order_by="academic_year",descending=True)
            return list(dict.fromkeys(str(row["academic_year"]) for row in rows if row.get("academic_year") is not None))
        except Exception as e:
            st.error(f"Academic Year Fetch Error: {e}")
            return []

    def getFacultyResult(self,academic_year):
        try:
            rows=get_rows("examination_results_faculty",{"department":self.department,"faculty_id":self.faculty_id,"academic_year":academic_year},"faculty_id,faculty_name,awarded_credits,academic_year,quarter",order_by="quarter")
            return pd.DataFrame(rows)
        except Exception as e:
            st.error(f"Faculty Result Fetch Error: {e}")
            return pd.DataFrame()

    def getMenteeRollNumbers(self):
        try:
            rows=get_rows("students",{"department":self.department,"student_mentor_id":self.faculty_id},"student_roll_number")
            return [str(row["student_roll_number"]).strip() for row in rows if row.get("student_roll_number") is not None]
        except Exception as e:
            st.error(f"Mentee Fetch Error: {e}")
            return []

    def getStudentResults(self,academic_year):
        try:
            roll_numbers=self.getMenteeRollNumbers()
            if not roll_numbers:return pd.DataFrame()

            rows=get_rows("students_academic_details",{"department":self.department},"student_roll_numner,student_batch,student_department,regulation,status")
            df=pd.DataFrame(rows)
            if df.empty:return df

            df=df[df["student_roll_numner"].astype(str).isin(roll_numbers)]
            if "academic_year" in df.columns:df=df[df["academic_year"].astype(str)==str(academic_year)]
            df=df.drop(columns=["student_department"],errors="ignore")
            return df.reset_index(drop=True)
        except Exception as e:
            st.error(f"Student Results Fetch Error: {e}")
            return pd.DataFrame()

    def main_layout(self):
        academic_years=self.getAcademicYears()

        if not academic_years:
            st.info("No Examination Results Have Been Released Yet.")
            return

        col1,col2=st.columns([1,2],border=True,gap="small")

        with col1:
            st.subheader("Examination Results")
            selected_year=st.pills("Select Academic Year",academic_years,selection_mode="single",key="examination_results_year")

            if selected_year:
                faculty_result=self.getFacultyResult(selected_year)

                if faculty_result.empty:
                    st.info("No Examination Result Found For The Selected Academic Year.")
                else:
                    st.subheader("Faculty Result",divider=True)
                    for _,row in faculty_result.iterrows():
                        with st.container(border=True):
                            st.write(f"**Academic Year:** {row['academic_year']}")
                            st.write(f"**Quarter:** {row['quarter']}")
                            st.metric("Awarded Credits",row["awarded_credits"])

        with col2:
            if selected_year:
                faculty_result=self.getFacultyResult(selected_year)

                if not faculty_result.empty:
                    st.subheader(f"{st.session_state['faculty_name']} - {self.faculty_id}",divider=True,text_alignment="center")

                    if len(faculty_result)==1:
                        st.metric("Examination Result Credits",faculty_result.iloc[0]["awarded_credits"])
                    else:
                        metric_cols=st.columns(len(faculty_result))
                        for index,(_,row) in enumerate(faculty_result.iterrows()):
                            with metric_cols[index]:st.metric(str(row["quarter"]),row["awarded_credits"])

                    st.subheader("Mentees Examination Results",divider=True)
                    student_results=self.getStudentResults(selected_year)

                    if student_results.empty:st.info("No Examination Results Found For The Mentees.")
                    else:st.dataframe(student_results,use_container_width=True,hide_index=True)