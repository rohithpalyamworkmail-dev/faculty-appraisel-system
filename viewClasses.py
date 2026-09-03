import pandas as pd
import plotly.express as px
import streamlit as st
from io import BytesIO
from global_fields import department,tables
from faculty_config import categories
from streamlit_extras.metric_cards import style_metric_cards
from database import get_rows,get_one,insert_row,update_rows,decode_bytea


def _frame(table,department_name,columns="*",filters=None,order_by=None,descending=False):
    final={"department":department_name}
    if filters:final.update(filters)
    try:
        df=pd.DataFrame(get_rows(table,final,columns,order_by,descending))
        if not df.empty:df=df.drop(columns=[c for c in ["id","department"] if c in df.columns],errors="ignore")
        return df
    except Exception as e:
        st.error(f"Data Fetch Error ({table}): {e}")
        return pd.DataFrame()


def _num(df,*columns):
    work=df.copy()
    for column in columns:
        if column in work.columns:work[column]=pd.to_numeric(work[column],errors="coerce")
    return work


def _truth(value):
    return str(value or "").strip().lower() in {"yes","true","1","y"}


def _metric(label,value):
    st.metric(label,value);style_metric_cards()


def _display(df):
    st.dataframe(df,use_container_width=True,hide_index=True)


class student:
    def __init__(self,col1,col2):
        self.col1=col1;self.col2=col2

    def _get_data(self,db_name):
        return _num(_frame("students",db_name),"student_age")

    def mainLayout(self):
        with self.col1:
            st.subheader("Student Control Panel")
            db_selected=st.selectbox("Select Department",department,key="student_dept_select")
            insight_options=["1. Total Student Count","2. Students by State","3. Students by District","4. Students by Batch","5. Students by Regulation","6. Gender Ratio","7. Gender Breakdown per Batch","8. Gender Ratio per State","9. Mentorship Load","10. Students Without Mentors","11. Age Distribution","12. Average Age per Batch","13. Out-of-State Students","14. Batch & Regulation Alignment","15. Top Districts","16. Underage / Overage Outliers","17. Duplicate Name Identification","18. Mentor Distribution per Batch","19. Students Managed by a Specific Mentor","20. District Concentration in Batches","21. Roll Number Sequence Verification","22. Students per State and Gender","23. Mentorship Imbalance","24. District Representation Ratio","25. Single-Student Districts","26. Oldest & Youngest Students","27. Students with Blank Addresses","28. Batch Growth Rate","29. Female Representation in Out-of-State Cohorts","30. Male Representation in Out-of-State Cohorts","31. Mentor-to-Student Ratio","32. Top 10 Most Common Last Names","33. State-wise Batch Intake","34. Active Regulations Count","35. Batch Concentration Index","36. Students per Regulation and Gender","37. District Diversity Index","38. State Diversity Index","39. Students in Home District","40. Students in Adjacent States","41. Age vs. Regulation Matrix","42. Mentors Handling Multiple Batches","43. Mentors Restrictive to Single Batch","44. Roll Number Format Anomalies","45. Address Pattern Search","46. Student Volume per Mentor per State","47. Cohort Diversity per Mentor","48. Regulation Cohort Volume","49. Students Missing District/State","50. Complete Student Profile Dataframe"]
            selected_insight=st.radio("Select Student Insight",insight_options,key="student_insight_radio")
        with self.col2:
            if not db_selected:st.warning("Please select a department database.");return
            self.render_insight(db_selected,selected_insight)

    def render_insight(self,db,option):
        df=self._get_data(db);opt=option.split(".")[0]
        if df.empty:st.info("No student records are available.");return
        if opt=="1":
            _metric("Total Registered Students",len(df));_display(df.head(50))
        elif opt=="2":
            states=sorted(df["student_state"].dropna().astype(str).unique().tolist());state=st.selectbox("Select State",states);out=df[df["student_state"].astype(str)==str(state)];_metric(f"Students in {state}",len(out));_display(out)
        elif opt=="3":
            out=df.groupby(["student_state","student_district"],dropna=False).size().reset_index(name="Count");_metric("Total District Clusters",len(out));_display(out);st.plotly_chart(px.bar(out,x="student_district",y="Count",color="student_state",title="District Distribution"),use_container_width=True)
        elif opt=="4":
            out=df.groupby("stuent_batch",dropna=False).size().reset_index(name="Count");_metric("Total Batches",len(out));_display(out);st.plotly_chart(px.pie(out,values="Count",names="stuent_batch",title="Batch Breakdown"),use_container_width=True)
        elif opt=="5":
            out=df.groupby("student_regulation",dropna=False).size().reset_index(name="Count");_metric("Active Regulations",len(out));_display(out);st.plotly_chart(px.bar(out,x="student_regulation",y="Count",color="student_regulation",title="Students per Regulation"),use_container_width=True)
        elif opt=="6":
            out=df.groupby("student_gender",dropna=False).size().reset_index(name="Count");_metric("Gender Categories",len(out));_display(out);st.plotly_chart(px.pie(out,values="Count",names="student_gender",title="Overall Gender Ratio",hole=.4),use_container_width=True)
        elif opt=="7":
            out=df.groupby(["stuent_batch","student_gender"],dropna=False).size().reset_index(name="Count");_display(out);st.plotly_chart(px.bar(out,x="stuent_batch",y="Count",color="student_gender",barmode="group",title="Gender Distribution per Batch"),use_container_width=True)
        elif opt=="8":
            out=df.groupby(["student_state","student_gender"],dropna=False).size().reset_index(name="Count");_display(out);st.plotly_chart(px.bar(out,x="student_state",y="Count",color="student_gender",title="State vs Gender Distribution"),use_container_width=True)
        elif opt=="9":
            out=df.groupby("student_mentor_id",dropna=False).size().reset_index(name="Mentees_Count");_metric("Active Mentors",len(out));_display(out);st.plotly_chart(px.bar(out,x="student_mentor_id",y="Mentees_Count",title="Mentees Count per Mentor ID"),use_container_width=True)
        elif opt=="10":
            out=df[df["student_mentor_id"].isna()|(df["student_mentor_id"].astype(str).str.strip()=="")];_metric("Unassigned Students",len(out));_display(out)
        elif opt=="11":
            out=df.groupby("student_age",dropna=False).size().reset_index(name="Count");_display(out);st.plotly_chart(px.bar(out,x="student_age",y="Count",title="Age Profile Distribution"),use_container_width=True)
        elif opt=="12":
            out=df.groupby("stuent_batch",dropna=False)["student_age"].mean().reset_index(name="Average_Age");_display(out);st.plotly_chart(px.line(out,x="stuent_batch",y="Average_Age",markers=True,title="Batch Mean Age Trend"),use_container_width=True)
        elif opt=="13":
            home=st.text_input("Enter Home State","Andhra Pradesh");out=df[df["student_state"].astype(str)!=home];_metric("Out-of-State Cohort Count",len(out));_display(out)
        elif opt=="14":
            out=df[["stuent_batch","student_regulation"]].drop_duplicates().reset_index(drop=True);_metric("Unique Mappings",len(out));_display(out)
        elif opt=="15":
            out=df.groupby("student_district",dropna=False).size().reset_index(name="Count").sort_values("Count",ascending=False).head(5);_display(out);st.plotly_chart(px.bar(out,x="student_district",y="Count",color="student_district",title="Top 5 Sourcing Districts"),use_container_width=True)
        elif opt=="16":
            out=df[(df["student_age"]<17)|(df["student_age"]>25)];_metric("Age Outliers Found",len(out));_display(out)
        elif opt=="17":
            out=df.groupby("student_name",dropna=False).size().reset_index(name="Occurrence");out=out[out["Occurrence"]>1];_metric("Duplicate Names Flagged",len(out));_display(out)
        elif opt=="18":
            out=df.groupby("stuent_batch",dropna=False)["student_mentor_id"].nunique(dropna=True).reset_index(name="Mentor_Count");_display(out)
        elif opt=="19":
            mentor=st.text_input("Enter Faculty Mentor ID","FAC001");out=df[df["student_mentor_id"].astype(str)==mentor];_metric(f"Assigned Mentees ({mentor})",len(out));_display(out)
        elif opt=="20":
            out=df.groupby(["stuent_batch","student_district"],dropna=False).size().reset_index(name="Student_Count");_display(out)
        elif opt=="21":
            _display(df[["student_roll_number","student_name","stuent_batch"]].sort_values("student_roll_number"))
        elif opt=="22":
            out=df.groupby(["student_state","student_gender"],dropna=False).size().reset_index(name="Count");_display(out.pivot(index="student_state",columns="student_gender",values="Count").fillna(0))
        elif opt=="23":
            out=df.groupby("student_mentor_id",dropna=False).size().reset_index(name="Count");out=out[out["Count"]!=10];_metric("Mentors Diverging from Standard Load (10)",len(out));_display(out)
        elif opt=="24":
            out=df.groupby("student_state",dropna=False)["student_district"].nunique(dropna=True).reset_index(name="Districts_Represented");_display(out)
        elif opt=="25":
            counts=df.groupby("student_district",dropna=False).size();districts=counts[counts==1].index;out=df[df["student_district"].isin(districts)][["student_district","student_state"]];_metric("Districts with Single Enrolment",len(out));_display(out)
        elif opt=="26":
            max_age=df["student_age"].max();min_age=df["student_age"].min();st.subheader("Oldest Students");_display(df[df["student_age"]==max_age]);st.subheader("Youngest Students");_display(df[df["student_age"]==min_age])
        elif opt=="27":
            out=df[df["student_adress"].isna()|(df["student_adress"].astype(str).str.strip()=="")];_metric("Missing Address Logs",len(out));_display(out)
        elif opt=="28":
            out=df.groupby("stuent_batch",dropna=False).size().reset_index(name="Intake").sort_values("stuent_batch");out["Growth_Rate_%"]=out["Intake"].pct_change()*100;_display(out)
        elif opt in {"29","30"}:
            label="Female" if opt=="29" else "Male";prompt="Home State Verification" if opt=="29" else "Home State Baseline";home=st.text_input(prompt,"Andhra Pradesh");out=df[(df["student_state"].astype(str)!=home)&(df["student_gender"].astype(str)==label)];_metric(f"Out-of-State {label} Students",len(out));_display(out)
        elif opt=="31":
            mentors=df["student_mentor_id"].dropna().astype(str);mentors=mentors[mentors.str.strip()!=""].nunique();_metric("Average Mentees per Mentor",round(len(df)/mentors,2) if mentors else 0)
        elif opt=="32":
            names=df["student_name"].fillna("").astype(str);out=names.apply(lambda x:x.split()[-1] if len(x.split())>1 else x).value_counts().reset_index().head(10);out.columns=["Surname","Count"];_display(out);st.plotly_chart(px.bar(out,x="Surname",y="Count",title="Top 10 Surnames Profile"),use_container_width=True)
        elif opt=="33":
            _display(df.groupby(["student_state","stuent_batch"],dropna=False).size().reset_index(name="Count"))
        elif opt=="34":
            _metric("Active Academic Standards",df["student_regulation"].nunique(dropna=True))
        elif opt=="35":
            out=df.groupby("stuent_batch",dropna=False).size().reset_index(name="Count");out["Percentage"]=out["Count"]*100/len(df);_display(out[["stuent_batch","Percentage"]])
        elif opt=="36":
            _display(df.groupby(["student_regulation","student_gender"],dropna=False).size().reset_index(name="Count"))
        elif opt=="37":
            _metric("Unique Districts Represented",df["student_district"].nunique(dropna=True))
        elif opt=="38":
            _metric("Unique States Represented",df["student_state"].nunique(dropna=True))
        elif opt=="39":
            home=st.text_input("Specify Local Home District","Chittoor");out=df[df["student_district"].astype(str)==home];_metric(f"Students from {home}",len(out));_display(out)
        elif opt=="40":
            states=st.multiselect("Select Neighboring States",["Tamil Nadu","Karnataka","Telangana","Odisha","Kerala"],default=["Tamil Nadu","Karnataka"]);out=df[df["student_state"].isin(states)] if states else df.iloc[0:0];_metric("Neighboring State Enrolments",len(out));_display(out)
        elif opt=="41":
            _display(df.groupby("student_regulation",dropna=False)["student_age"].mean().reset_index(name="Avg_Age"))
        elif opt=="42":
            out=df.groupby("student_mentor_id",dropna=False)["stuent_batch"].nunique(dropna=True).reset_index(name="Batch_Count");out=out[out["Batch_Count"]>1];_metric("Multi-Batch Mentors",len(out));_display(out)
        elif opt=="43":
            grouped=df.groupby("student_mentor_id",dropna=False)["stuent_batch"].agg([("Batch_Count","nunique"),("Single_Batch","max")]).reset_index();out=grouped[grouped["Batch_Count"]==1][["student_mentor_id","Single_Batch"]];_metric("Single-Batch Mentors",len(out));_display(out)
        elif opt=="44":
            out=df[df["student_roll_number"].astype(str).str.len()!=10];_metric("Roll Format Anomalies Detected",len(out));_display(out)
        elif opt=="45":
            term=st.text_input("Enter Search Keyword in Address","Street");out=df[df["student_adress"].fillna("").astype(str).str.contains(term,case=False,regex=False)];_metric(f"Matches for '{term}'",len(out));_display(out)
        elif opt=="46":
            _display(df.groupby(["student_mentor_id","student_state"],dropna=False).size().reset_index(name="Count"))
        elif opt=="47":
            _display(df.groupby("student_mentor_id",dropna=False)["student_state"].nunique(dropna=True).reset_index(name="State_Diversity"))
        elif opt=="48":
            _display(df.groupby("student_regulation",dropna=False).size().reset_index(name="Total_Enrolment"))
        elif opt=="49":
            out=df[df["student_district"].isna()|(df["student_district"].fillna("").astype(str).str.strip()=="")|df["student_state"].isna()|(df["student_state"].fillna("").astype(str).str.strip()=="")];_metric("Incomplete Geographic Metadata",len(out));_display(out)
        elif opt=="50":
            states=sorted(df["student_state"].dropna().astype(str).unique().tolist());batches=sorted(df["stuent_batch"].dropna().astype(str).unique().tolist());sel_state=st.selectbox("Filter State",["All"]+states);sel_batch=st.selectbox("Filter Batch",["All"]+batches);out=df.copy();out=out if sel_state=="All" else out[out["student_state"].astype(str)==sel_state];out=out if sel_batch=="All" else out[out["stuent_batch"].astype(str)==sel_batch];_metric("Filtered Records Count",len(out));_display(out)


class faculty:
    def __init__(self,col1,col2):
        self.col1=col1;self.col2=col2

    def _get_data(self,db_name):
        return _num(_frame("faculty",db_name),"faculty_salary","faculty_overall_experience","faculty_experience_mtiet")

    def mainLayout(self):
        with self.col1:
            st.subheader("Faculty Control Panel")
            db_selected=st.selectbox("Select Department",department,key="faculty_dept_select")
            insight_options=["1. Total Faculty Count","2. Faculty per Department","3. Faculty by Permanent State","4. Faculty by Current State","5. Relocated Faculty","6. Local Residence Faculty","7. District Relocation Count","8. Total Payroll / Salary Outlay","9. Average Salary per Department","10. Highest Paid Faculty","11. Salary Ranges","12. Average Overall Experience","13. Average Institution Experience","14. Prior External Experience","15. Faculty Joined Fresh","16. Seniority Ranking","17. Institutional Loyalty Ranking","18. HOD Identification","19. HOD Identification per Department","20. Controller of Examinations","21. Principal Details","22. Admin Role Holders","23. Faculty with Multiple Admin Roles","24. Pure Teaching Faculty","25. Salary vs. Experience Correlation","26. Departmental Experience Index","27. Departmental Retention Rate","28. Faculty per Permanent District","29. Faculty per Current District","30. High-Salary Low-Experience Outliers","31. Low-Salary High-Experience Outliers","32. Departmental Headcount Comparison","33. Faculty Count by Native Region","34. Faculty Influx from Target State","35. Departmental Payroll Share","36. Minimum & Maximum Salary per Department","37. Experience Gap","38. Password Security Audit","39. Admin Ratio","40. Department Heads Salary Comparison","41. Faculty Commute Distance Proxy","42. Departmental Administrative Density","43. Most Experienced HOD","44. Highest Paid Non-Admin Faculty","45. Faculty Retention Metric","46. District Diversity per Department","47. State Diversity per Department","48. Faculty Count with Zero Prior Experience","49. Duplicate Faculty Names","50. Complete Faculty Master Directory"]
            selected_insight=st.radio("Select Faculty Insight",insight_options,key="faculty_insight_radio")
        with self.col2:
            if not db_selected:st.warning("Please select a department database.");return
            self.render_insight(db_selected,selected_insight)

    def render_insight(self,db,option):
        df=self._get_data(db);opt=option.split(".")[0]
        if df.empty:st.info("No faculty records are available.");return
        role=lambda c:df[c].apply(_truth) if c in df.columns else pd.Series(False,index=df.index)
        if opt=="1":_metric("Total Faculty Members",len(df));_display(df.head(50))
        elif opt=="2":
            out=df.groupby("faculty_department",dropna=False).size().reset_index(name="Count");_metric("Total Departments",len(out));_display(out);st.plotly_chart(px.bar(out,x="faculty_department",y="Count",color="faculty_department",title="Faculty Distribution across Departments"),use_container_width=True)
        elif opt=="3":
            out=df.groupby("faculty_permanent_state",dropna=False).size().reset_index(name="Count");_metric("Native States Represented",len(out));_display(out);st.plotly_chart(px.pie(out,values="Count",names="faculty_permanent_state",title="Permanent State Breakdown"),use_container_width=True)
        elif opt=="4":
            out=df.groupby("faculty_current_state",dropna=False).size().reset_index(name="Count");_metric("Current Residence States",len(out));_display(out);st.plotly_chart(px.pie(out,values="Count",names="faculty_current_state",title="Current Residence State Distribution"),use_container_width=True)
        elif opt=="5":out=df[df["faculty_permanent_state"].astype(str)!=df["faculty_current_state"].astype(str)];_metric("Inter-State Relocated Faculty",len(out));_display(out)
        elif opt=="6":out=df[df["faculty_permanent_state"].astype(str)==df["faculty_current_state"].astype(str)];_metric("Local State Resident Faculty",len(out));_display(out)
        elif opt=="7":out=df[df["faculty_permanent_district"].astype(str)!=df["faculty_current_district"].astype(str)];_metric("Inter-District Relocated Faculty",len(out));_display(out)
        elif opt=="8":_metric("Total Monthly Payroll",f"₹ {df['faculty_salary'].fillna(0).sum():,.2f}")
        elif opt=="9":
            out=df.groupby("faculty_department",dropna=False)["faculty_salary"].mean().reset_index(name="Avg_Salary");_display(out);st.plotly_chart(px.bar(out,x="faculty_department",y="Avg_Salary",title="Average Salary per Department"),use_container_width=True)
        elif opt=="10":
            out=df[["faculty_name","faculty_department","faculty_salary"]].sort_values("faculty_salary",ascending=False).head(10);_display(out);st.plotly_chart(px.bar(out,x="faculty_name",y="faculty_salary",color="faculty_department",title="Top 10 Highest Paid Faculty Members"),use_container_width=True)
        elif opt=="11":
            slab=pd.cut(df["faculty_salary"],bins=[0,50000,100000,150000,200000,500000],labels=["<50k","50k-100k","100k-150k","150k-200k",">200k"]);out=slab.value_counts().reset_index();out.columns=["Salary_Slab","Count"];_display(out);st.plotly_chart(px.pie(out,values="Count",names="Salary_Slab",title="Faculty Salary Slabs"),use_container_width=True)
        elif opt=="12":_metric("Average Overall Experience (Years)",round(df["faculty_overall_experience"].mean(),2) if df["faculty_overall_experience"].notna().any() else 0)
        elif opt=="13":_metric("Average Tenure at Institution (Years)",round(df["faculty_experience_mtiet"].mean(),2) if df["faculty_experience_mtiet"].notna().any() else 0)
        elif opt=="14":out=df.copy();out["Prior_Exp"]=out["faculty_overall_experience"]-out["faculty_experience_mtiet"];out=out[out["Prior_Exp"]>0];_metric("Faculty with External Work Experience",len(out));_display(out)
        elif opt=="15":out=df[df["faculty_overall_experience"]==df["faculty_experience_mtiet"]];_metric("Fresh Hires (Zero External Exp)",len(out));_display(out)
        elif opt=="16":
            out=df[["faculty_name","faculty_department","faculty_overall_experience"]].sort_values("faculty_overall_experience",ascending=False).head(10);_display(out);st.plotly_chart(px.bar(out,x="faculty_name",y="faculty_overall_experience",color="faculty_department",title="Top 10 Most Senior Faculty (Overall)"),use_container_width=True)
        elif opt=="17":
            out=df[["faculty_name","faculty_department","faculty_experience_mtiet"]].sort_values("faculty_experience_mtiet",ascending=False).head(10);_display(out);st.plotly_chart(px.bar(out,x="faculty_name",y="faculty_experience_mtiet",color="faculty_department",title="Top 10 Longest Serving Faculty Members"),use_container_width=True)
        elif opt=="18":out=df[role("is_hod")];_metric("Total HODs",len(out));_display(out)
        elif opt=="19":_display(df.loc[role("is_hod"),["faculty_department","faculty_name","faculty_id"]])
        elif opt=="20":out=df[role("is_controller")];_metric("Controller of Examinations Count",len(out));_display(out)
        elif opt=="21":out=df[role("is_principal")];_metric("Principal Record Identified",len(out));_display(out)
        elif opt=="22":out=df[role("is_admin")];_metric("Admin Privilege Holders",len(out));_display(out)
        elif opt in {"23","24"}:
            work=df.copy();cols=["is_controller","is_hod","is_principal","is_admin"]
            for c in cols:work[c]=work[c].apply(_truth)
            work["role_count"]=work[cols].sum(axis=1);out=work[work["role_count"]>1] if opt=="23" else work[work["role_count"]==0];_metric("Faculty with Multiple Leadership Roles" if opt=="23" else "Pure Teaching Faculty",len(out));_display(out)
        elif opt=="25":
            out=df[["faculty_name","faculty_salary","faculty_overall_experience","faculty_department"]];_display(out);st.plotly_chart(px.scatter(out,x="faculty_overall_experience",y="faculty_salary",color="faculty_department",hover_data=["faculty_name"],title="Salary vs Overall Experience Scatter Plot"),use_container_width=True)
        elif opt=="26":_display(df.groupby("faculty_department",dropna=False).agg(Mean_Overall_Exp=("faculty_overall_experience","mean"),Mean_Inst_Exp=("faculty_experience_mtiet","mean")).reset_index())
        elif opt=="27":
            work=df.copy();work["Ratio"]=work["faculty_experience_mtiet"]/work["faculty_overall_experience"].replace(0,pd.NA);_display(work.groupby("faculty_department",dropna=False)["Ratio"].mean().mul(100).reset_index(name="Retention_Ratio"))
        elif opt=="28":_display(df.groupby("faculty_permanent_district",dropna=False).size().reset_index(name="Count").sort_values("Count",ascending=False))
        elif opt=="29":_display(df.groupby("faculty_current_district",dropna=False).size().reset_index(name="Count").sort_values("Count",ascending=False))
        elif opt=="30":out=df[(df["faculty_salary"]>80000)&(df["faculty_overall_experience"]<3)];_metric("High-Salary Low-Exp Outliers",len(out));_display(out)
        elif opt=="31":out=df[(df["faculty_salary"]<40000)&(df["faculty_overall_experience"]>10)];_metric("Low-Salary High-Exp Outliers",len(out));_display(out)
        elif opt=="32":_display(df.groupby("faculty_department",dropna=False).size().reset_index(name="Headcount").sort_values("Headcount",ascending=False))
        elif opt=="33":
            south={"Andhra Pradesh","Telangana","Tamil Nadu","Karnataka","Kerala"};out=df["faculty_permanent_state"].apply(lambda x:"South" if x in south else "Non-South").value_counts().reset_index();out.columns=["Region","Count"];_display(out)
        elif opt=="34":state=st.text_input("Enter Target Permanent State","Telangana");out=df[df["faculty_permanent_state"].astype(str)==state];_metric(f"Faculty from {state}",len(out));_display(out)
        elif opt=="35":
            out=df.groupby("faculty_department",dropna=False)["faculty_salary"].sum().reset_index();total=out["faculty_salary"].sum();out["Payroll_Share"]=out["faculty_salary"]*100/total if total else 0;_display(out[["faculty_department","Payroll_Share"]])
        elif opt=="36":_display(df.groupby("faculty_department",dropna=False)["faculty_salary"].agg(Min_Salary="min",Max_Salary="max").reset_index())
        elif opt=="37":
            work=df.copy();work["External"]=work["faculty_overall_experience"]-work["faculty_experience_mtiet"];_display(work.groupby("faculty_department",dropna=False)["External"].mean().reset_index(name="Avg_External_Exp"))
        elif opt=="38":
            pwd=df["faculty_password"].fillna("").astype(str);out=df[(pwd.str.len()<6)|pwd.isin(["123456","password","admin"])];_metric("Weak Password Flagged",len(out));_display(out)
        elif opt=="39":_metric("Admin Percentage (%)",f"{round(role('is_admin').sum()*100/len(df),2) if len(df) else 0}%")
        elif opt=="40":_display(df.loc[role("is_hod"),["faculty_name","faculty_department","faculty_salary"]])
        elif opt=="41":home=st.text_input("Institute Home District","Chittoor");out=df[df["faculty_current_district"].astype(str)!=home];_metric("Out-of-District Commuters",len(out));_display(out)
        elif opt=="42":
            mask=role("is_admin")|role("is_hod")|role("is_controller");_display(df[mask].groupby("faculty_department",dropna=False).size().reset_index(name="Admin_Role_Holders"))
        elif opt=="43":_display(df[role("is_hod")].sort_values("faculty_overall_experience",ascending=False).head(1))
        elif opt=="44":out=df[~role("is_admin")&~role("is_hod")].sort_values("faculty_salary",ascending=False).head(10);_display(out)
        elif opt=="45":out=df[df["faculty_experience_mtiet"]>=5];_metric("Faculty Served >= 5 Years",len(out));_display(out)
        elif opt=="46":_display(df.groupby("faculty_department",dropna=False)["faculty_permanent_district"].nunique(dropna=True).reset_index(name="District_Diversity"))
        elif opt=="47":_display(df.groupby("faculty_department",dropna=False)["faculty_permanent_state"].nunique(dropna=True).reset_index(name="State_Diversity"))
        elif opt=="48":out=df[(df["faculty_overall_experience"]-df["faculty_experience_mtiet"])==0];_metric("Direct Campus Hires",len(out));_display(out)
        elif opt=="49":out=df.groupby("faculty_name",dropna=False).size().reset_index(name="Count");out=out[out["Count"]>1];_metric("Duplicate Faculty Names Flagged",len(out));_display(out)
        elif opt=="50":
            depts=sorted(df["faculty_department"].dropna().astype(str).unique().tolist());states=sorted(df["faculty_permanent_state"].dropna().astype(str).unique().tolist());sel_dept=st.selectbox("Filter Department",["All"]+depts);sel_state=st.selectbox("Filter Native State",["All"]+states);out=df.copy();out=out if sel_dept=="All" else out[out["faculty_department"].astype(str)==sel_dept];out=out if sel_state=="All" else out[out["faculty_permanent_state"].astype(str)==sel_state];_metric("Filtered Records Count",len(out));_display(out)


class subjects:
    def __init__(self,col1,col2):
        self.col1=col1;self.col2=col2

    def _get_data(self,db_name):
        return _num(_frame("subjects",db_name),"subject_semister","subject_credits")

    def mainLayout(self):
        with self.col1:
            st.subheader("Subjects Control Panel")
            db_selected=st.selectbox("Select Department",department,key="subjects_dept_select")
            insight_options=["1. Total Subject Count","2. Subjects per Semester","3. Subjects by Type","4. Credit Distribution","5. Average Credits per Semester","6. High-Credit Subjects","7. Low-Credit Subjects","8. Unallocated Subjects","9. Multi-Faculty Subjects","10. Single-Faculty Subjects","11. Subjects per Section","12. Theory vs. Lab Ratio per Semester","13. Faculty Teaching Load","14. Overloaded Faculty","15. Total Credits per Semester","16. Subject Count by Type and Semester","17. Core vs. Elective Breakdown","18. Most Heavily Allocated Faculty","19. Sections Covered per Subject","20. Subjects with Unassigned Sections","21. Semester Workload Balance","22. Duplicate Subject Names/Codes","23. Lab / Practical Course Count","24. Theory Course Count","25. Average Credit Value by Subject Type","26. Semester 1 & 2 Foundation Load","27. Final Year Project / Seminar Load","28. Faculty Cross-Semester Allocation","29. Subject Code Prefix Grouping","30. Subjects Allocation Matrix","31. Multi-Section Subjects Count","32. Single-Section Niche Courses","33. Faculty Allocation Density","34. Total Teaching Hours Proxy","35. Semester Credit Outliers","36. Subjects per Section Matrix","37. Elective Course Ratio","38. Unassigned Lab Courses","39. Shared Faculty across Sections","40. Subject Name Length Audit","41. Total Subjects in Odd Semesters","42. Total Subjects in Even Semesters","43. Max Credits Semester","44. Min Credits Semester","45. Faculty Workload Distribution by Subject Type","46. High-Credit Lab Courses","47. Low-Credit Theory Courses","48. Subjects Managed by Department Heads","49. Subjects Managed by Adjunct/Guest Faculty","50. Complete Curriculum Catalog"]
            selected_insight=st.radio("Select Curriculum Insight",insight_options,key="subjects_insight_radio")
        with self.col2:
            if not db_selected:st.warning("Please select a department database.");return
            self.render_insight(db_selected,selected_insight)

    def render_insight(self,db,option):
        df=self._get_data(db);opt=option.split(".")[0]
        if df.empty:st.info("No subject records are available.");return
        faculty_lists=df["alloted_faculty_ids"].fillna("").astype(str).apply(lambda x:[i.strip() for i in x.split(",") if i.strip()])
        section_lists=df["alloted_sections"].fillna("").astype(str).apply(lambda x:[i.strip() for i in x.split(",") if i.strip()])
        subject_type=df["subject_type"].fillna("").astype(str).str.lower()
        if opt=="1":_metric("Total Subject/Course Count",len(df));_display(df.head(50))
        elif opt=="2":
            out=df.groupby("subject_semister",dropna=False).size().reset_index(name="Count").sort_values("subject_semister");_display(out);st.plotly_chart(px.bar(out,x="subject_semister",y="Count",title="Course Offerings per Semester",color="subject_semister"),use_container_width=True)
        elif opt=="3":
            out=df.groupby("subject_type",dropna=False).size().reset_index(name="Count");_metric("Distinct Subject Types",len(out));_display(out);st.plotly_chart(px.pie(out,values="Count",names="subject_type",title="Theory vs Practical vs Elective Distribution"),use_container_width=True)
        elif opt=="4":_metric("Total Curriculum Credits",df["subject_credits"].fillna(0).sum())
        elif opt=="5":
            out=df.groupby("subject_semister",dropna=False)["subject_credits"].mean().reset_index(name="Avg_Credits").sort_values("subject_semister");_display(out);st.plotly_chart(px.line(out,x="subject_semister",y="Avg_Credits",markers=True,title="Semester-wise Average Credits"),use_container_width=True)
        elif opt=="6":out=df[df["subject_credits"]>=4];_metric("High-Credit Subjects (>= 4)",len(out));_display(out)
        elif opt=="7":out=df[df["subject_credits"]<=2];_metric("Low-Credit / Audit Subjects (<= 2)",len(out));_display(out)
        elif opt=="8":out=df[faculty_lists.apply(len)==0];_metric("Unstaffed Subjects",len(out));_display(out)
        elif opt=="9":out=df[faculty_lists.apply(len)>1];_metric("Multi-Faculty Tagged Courses",len(out));_display(out)
        elif opt=="10":out=df[faculty_lists.apply(len)==1];_metric("Exclusively Handled Subjects",len(out));_display(out)
        elif opt=="11":
            out=pd.DataFrame({"Sections_List":section_lists}).explode("Sections_List");out=out[out["Sections_List"].fillna("")!=""]["Sections_List"].value_counts().reset_index();out.columns=["Section","Subject_Count"];_display(out);st.plotly_chart(px.bar(out,x="Section",y="Subject_Count",title="Subjects Offered per Section"),use_container_width=True)
        elif opt=="12":
            out=df.groupby(["subject_semister","subject_type"],dropna=False).size().reset_index(name="Count");_display(out);st.plotly_chart(px.bar(out,x="subject_semister",y="Count",color="subject_type",title="Theory/Lab Distribution per Sem",barmode="stack"),use_container_width=True)
        elif opt in {"13","14","18"}:
            out=pd.DataFrame({"Faculties":faculty_lists}).explode("Faculties");out=out[out["Faculties"].fillna("")!=""]["Faculties"].value_counts().reset_index();out.columns=["Faculty_ID","Assigned_Subjects" if opt=="13" else "Subject_Count" if opt=="14" else "Assignments"]
            if opt=="14":threshold=st.number_input("Overload Threshold (Subjects)",min_value=1,value=3);out=out[out["Subject_Count"]>threshold];_metric(f"Faculty Handling > {threshold} Subjects",len(out))
            if opt=="18":out=out.head(10);st.subheader("Top 10 Busiest Faculty IDs")
            _display(out)
        elif opt=="15":
            out=df.groupby("subject_semister",dropna=False)["subject_credits"].sum().reset_index(name="Semester_Credits").sort_values("subject_semister");_display(out);st.plotly_chart(px.bar(out,x="subject_semister",y="Semester_Credits",title="Cumulative Credit Load per Semester",text_auto=True),use_container_width=True)
        elif opt=="16":
            out=df.groupby(["subject_semister","subject_type"],dropna=False).size().reset_index(name="Count");_display(out.pivot(index="subject_semister",columns="subject_type",values="Count").fillna(0))
        elif opt=="17":_display(df.groupby("subject_type",dropna=False).size().reset_index(name="Count"))
        elif opt=="19":out=df[["subject_name","alloted_sections"]].copy();out["Section_Count"]=section_lists.apply(len);_display(out)
        elif opt=="20":out=df[section_lists.apply(len)==0];_metric("Courses Missing Section Mappings",len(out));_display(out)
        elif opt=="21":
            out=df.groupby("subject_semister",dropna=False)["subject_credits"].sum().reset_index(name="credits");out["Parity"]=out["subject_semister"].fillna(0).astype(int).apply(lambda x:"Odd (1,3,5,7)" if x%2 else "Even (2,4,6,8)");parity=out.groupby("Parity")["credits"].sum().reset_index();_display(parity);st.plotly_chart(px.pie(parity,values="credits",names="Parity",title="Odd vs Even Semester Credits"),use_container_width=True)
        elif opt=="22":out=df.groupby("subject_code",dropna=False).size().reset_index(name="Count");out=out[out["Count"]>1];_metric("Duplicate Course Codes",len(out));_display(out)
        elif opt=="23":out=df[subject_type.str.contains("lab|practical",regex=True)];_metric("Total Lab/Practical Modules",len(out));_display(out)
        elif opt=="24":out=df[subject_type.str.contains("theory",regex=False)];_metric("Total Theory Modules",len(out));_display(out)
        elif opt=="25":_display(df.groupby("subject_type",dropna=False)["subject_credits"].mean().reset_index(name="Avg_Credits"))
        elif opt=="26":out=df[df["subject_semister"].isin([1,2])];_metric("Foundation/First-Year Courses",len(out));_display(out)
        elif opt=="27":out=df[df["subject_semister"].isin([7,8])];_metric("Final Year/Senior Courses",len(out));_display(out)
        elif opt=="28":
            work=pd.DataFrame({"subject_semister":df["subject_semister"],"Faculties":faculty_lists}).explode("Faculties");out=work[work["Faculties"].fillna("")!=""].groupby("Faculties")["subject_semister"].nunique().reset_index(name="Unique_Semesters_Handled");_display(out[out["Unique_Semesters_Handled"]>1])
        elif opt=="29":out=df["subject_code"].fillna("").astype(str).apply(lambda x:"".join(c for c in x if c.isalpha())).value_counts().reset_index();out.columns=["Department_Prefix","Course_Count"];_display(out)
        elif opt=="30":_display(df[["subject_name","alloted_faculty_ids","alloted_sections"]])
        elif opt=="31":out=df[section_lists.apply(len)>1];_metric("Subjects Running Across Multiple Sections",len(out));_display(out)
        elif opt=="32":out=df[section_lists.apply(len)==1];_metric("Niche/Single-Section Courses",len(out));_display(out)
        elif opt=="33":_metric("Average Faculty Assigned per Subject",round(faculty_lists.apply(len).mean(),2))
        elif opt=="34":out=df[["subject_name","subject_credits"]].copy();out["Est_Total_Hours_per_Sem (Credits x 15)"]=out["subject_credits"]*15;_display(out)
        elif opt=="35":out=df.groupby("subject_semister",dropna=False)["subject_credits"].sum().reset_index(name="Total_Credits");out["Deviation_From_Mean"]=out["Total_Credits"]-out["Total_Credits"].mean();_display(out)
        elif opt=="36":
            work=pd.DataFrame({"subject_name":df["subject_name"],"Sections":section_lists}).explode("Sections");work=work[work["Sections"].fillna("")!=""];_display(work.groupby("Sections")["subject_name"].apply(list).reset_index())
        elif opt=="37":_metric("Curriculum Elective Percentage",f"{(subject_type.str.contains('elective',regex=False).sum()*100/len(df)) if len(df) else 0:.2f}%")
        elif opt=="38":out=df[subject_type.str.contains("lab|practical",regex=True)&(faculty_lists.apply(len)==0)];_metric("Unstaffed Labs",len(out));_display(out)
        elif opt=="39":out=df[(section_lists.apply(len)>1)&(faculty_lists.apply(len)==1)];_metric("Single Faculty Managing Multiple Sections",len(out));_display(out)
        elif opt=="40":out=df[["subject_code","subject_name"]].copy();out["Name_Length"]=out["subject_name"].fillna("").astype(str).str.len();_display(out.sort_values("Name_Length",ascending=False))
        elif opt=="41":out=df[df["subject_semister"].fillna(0).astype(int)%2!=0];_metric("Subjects in Odd Semesters",len(out));_display(out)
        elif opt=="42":out=df[df["subject_semister"].fillna(0).astype(int)%2==0];_metric("Subjects in Even Semesters",len(out));_display(out)
        elif opt in {"43","44"}:
            out=df.groupby("subject_semister",dropna=False)["subject_credits"].sum().reset_index(name="Total_Credits").sort_values("Total_Credits",ascending=opt=="44").head(1);_display(out)
        elif opt=="45":
            work=pd.DataFrame({"subject_type":df["subject_type"],"Faculties":faculty_lists}).explode("Faculties");work=work[work["Faculties"].fillna("")!=""];_display(work.groupby(["Faculties","subject_type"]).size().reset_index(name="Allocations"))
        elif opt=="46":out=df[subject_type.str.contains("lab|practical",regex=True)&(df["subject_credits"]>=3)];_metric("High-Credit Labs (>= 3)",len(out));_display(out)
        elif opt=="47":out=df[subject_type.str.contains("theory",regex=False)&(df["subject_credits"]<=2)];_metric("Short Theory Modules (<= 2 Credits)",len(out));_display(out)
        elif opt=="48":st.info("Cross-referencing faculty metadata required. Currently displaying a standard filter output.");_display(df[faculty_lists.apply(len)>0])
        elif opt=="49":out=df[df["alloted_faculty_ids"].fillna("").astype(str).str.contains("EXT|GST",case=False,regex=True)];_metric("Guest Faculty Allocated Courses",len(out));_display(out)
        elif opt=="50":out=df.sort_values(["subject_semister","subject_code","subject_credits"],ascending=[True,True,False]);_metric("Total Catalog Entries",len(out));_display(out)


class settings:
    def __init__(self,col1,col2):
        self.col1=col1;self.col2=col2
        self.table_map={"Academic Results":"academic_results","Students Feedback":"feedback","HoD Feedback":"hod_feedbacks","Project Guidence":"project_guidence","Innovations In Teaching Learning":"innovation_in_teaching","OBE Practice":"obe_practice","Product Development By Student":"product_development_by_student","Student Participation And Winning In Seminar, Workshop, Symposium, Conference, etc":"seminar_workshop_conference_symposium_by_students","Student Participation & Wining in project Competition & MNC Contest":"competetion_contest__by_students","Language Certification Courses":"language_certifications","Online Certification (min 1 week) courses":"online_certifications","Internship & In-plant Training (minimum 15 days)":"internships_inplant_training","Special Awards from Institute and Industry":"special_awards","Students Involvement in ENterpreneurship & Start-ups":"student_involvements_in_startups","Competitive Examinations":"competetive_examinations","Placement":"placements","Examination Results":"examination_results_faculty","Achievement of ICT and Skill Rack Target":"ict_skill_rack","Hacker Rank/Hacker Earth":"coding_data","Publication -Journals, Conferences & Book chapters":"publications_conferences_journals_book_chapters","Publication - Journals, Conferences & Book Chapters":"publications_conferences_journals_book_chapters","Patents & Copyrights":"patent_copy_rights","Consultancy, Funding & Grants":"consultancy_funding_grants","Citation Impact Of Published Work":"citation_impacts","Ph.D Guidance":"phd_guidance","Book Publication":"book_publications","Arranging On Campus Recruitment":"on_campus_recruitments_by_faculty","Guest Lectures Delivered (Per Day)":"guest_lectures","Online certification (min 4 week)":"online_certifications_4weeks","Online Certification (min 4 week)":"online_certifications_4weeks","Online Lecture Series / MOOC Course Developed":"mooc_courses_by_faculty","News Letter & Magazine (like electronics for you, etc.,)":"news_letters_and_magazines","News Letter & Magazine":"news_letters_and_magazines","Events Participations (NIRF Ranked Institutes Only)":"nirf_event_participations","Special Awards and Fellowship from Recognized Professional Bodies (During Assesment year)":"special_awards_fellowships","Special Awards and Fellowship from Recognized Professional Bodies":"special_awards_fellowships","Faculty Exchange (Min 1 week)":"faculty_exchanges","Extension Activities Organized":"extension_activities","Alumni Networking":"alumni_connection_by_faculties","Collaboration With Industry/Institute":"collaborations_industry_institute","Value Added Courses Conducted/Organized":"value_added_courses","Organizing International Conference Partnered with IEEE, Springer, ELsevier to be indexed in Scopus with ISBN":"organizing_international_conference","Event Organized (in collaboration with professional societies and accreditation/approval bodies or industry":"event_organizations","Memberships":"membership"}
        self.normalized_table_map={self.normalize_activity(k):v for k,v in self.table_map.items()}
        for key,value in {"settings_login":False,"settings_faculty_name":"","settings_faculty_id":"","settings_department":"","settings_designation":"","settings_is_hod":"No","settings_is_principal":"No","settings_is_admin":"No"}.items():
            if key not in st.session_state:st.session_state[key]=value

    def normalize_activity(self,value):
        return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())

    def mapped_table(self,activity):
        return self.table_map.get(activity) or self.normalized_table_map.get(self.normalize_activity(activity))

    def resolve_table(self,activity,connection=None,department_name=None):
        return self.mapped_table(activity)

    @property
    def current_department(self):
        return st.session_state.get("settings_department","")

    def get_status_summary(self,category,status):
        rows=[]
        for activity in categories.get(category,[]):
            table=self.resolve_table(activity);count=0
            if table:
                try:
                    data=get_rows(table,{"department":self.current_department},"hod_approval,admin_approval")
                    if status=="UN KNOWN":count=sum(1 for r in data if r.get("hod_approval")=="UN KNOWN" and r.get("admin_approval")=="UN KNOWN")
                    else:count=sum(1 for r in data if r.get("hod_approval")==status)
                except Exception:count=0
            rows.append({"Tables":activity,f"{status} Count":int(count)})
        return pd.DataFrame(rows)

    def get_records_by_status(self,table,status):
        try:
            rows=get_rows(table,{"department":self.current_department},"id,faculty_id,faculty_name,hod_approval,admin_approval",order_by="id",descending=True)
            if status=="UN KNOWN":rows=[r for r in rows if r.get("hod_approval")=="UN KNOWN" and r.get("admin_approval")=="UN KNOWN"]
            else:rows=[r for r in rows if r.get("hod_approval")==status]
            return pd.DataFrame([{"record_id":r.get("id"),"faculty_id":r.get("faculty_id"),"faculty_name":r.get("faculty_name")} for r in rows])
        except Exception as e:st.error(f"Unable to fetch {table} records: {e}");return pd.DataFrame()

    def get_record(self,table,record_id,department_name=None):
        try:
            row=get_one(table,{"department":department_name or self.current_department,"id":record_id})
            if not row:return {}
            result=dict(row);result["record_id"]=result.pop("id",record_id);result.pop("department",None);return result
        except Exception as e:st.error(f"Unable to fetch record: {e}");return {}

    def update_hod_status(self,table,record_id,new_status,current_status):
        try:
            row=get_one(table,{"department":self.current_department,"id":record_id},"id,hod_approval,admin_approval")
            if not row:return False
            if current_status=="UN KNOWN" and not (row.get("hod_approval")=="UN KNOWN" and row.get("admin_approval")=="UN KNOWN"):return False
            if current_status!="UN KNOWN" and row.get("hod_approval")!=current_status:return False
            update_rows(table,{"hod_approval":new_status},{"department":self.current_department,"id":record_id})
            return True
        except Exception as e:st.error(f"Update Error: {e}");return False

    def render_record_card(self,table,record_id,current_status,allow_deny=True):
        record=self.get_record(table,record_id)
        if not record:return
        with st.container(border=True):
            st.subheader(f"{record.get('faculty_name','Faculty')} - {record.get('faculty_id','')}",divider=True,text_alignment="center")
            data=[(k,v) for k,v in record.items() if k not in ["record_id","faculty_name","faculty_id"]]
            for i in range(0,len(data),3):
                cols=st.columns(3)
                for j,(key,value) in enumerate(data[i:i+3]):
                    with cols[j]:st.caption(key.replace("_"," ").title());st.write(value if value not in [None,""] else "—")
            if allow_deny:
                c1,c2=st.columns(2)
                with c1:approve=st.button("Approve",type="primary",width="stretch",key=f"hod_approve_{current_status}_{table}_{record_id}")
                with c2:deny=st.button("Deny",type="primary",width="stretch",key=f"hod_deny_{current_status}_{table}_{record_id}")
                if approve:
                    if self.update_hod_status(table,record_id,"APPROVED",current_status):st.success("Record Approved Successfully.");st.rerun()
                    else:st.warning("Record could not be approved.")
                if deny:
                    if self.update_hod_status(table,record_id,"DENIED",current_status):st.success("Record Denied Successfully.");st.rerun()
                    else:st.warning("Record could not be denied.")
            elif st.button("Accept Denial / Approve",type="primary",width="stretch",key=f"hod_reapprove_{table}_{record_id}"):
                if self.update_hod_status(table,record_id,"APPROVED","DENIED"):st.success("Denied Record Approved Successfully.");st.rerun()
                else:st.warning("Record could not be approved.")

    def render_status_tab(self,status):
        selected_category=st.selectbox("Select Category",list(categories.keys()),key=f"hod_{status}_category")
        if not selected_category:return
        summary=self.get_status_summary(selected_category,status);st.dataframe(summary,use_container_width=True,hide_index=True,column_config={"Tables":st.column_config.TextColumn("Tables"),f"{status} Count":st.column_config.NumberColumn(f"{status} Count")})
        selected_activity=st.selectbox("Select Table",categories[selected_category],key=f"hod_{status}_activity")
        if not selected_activity:return
        table=self.resolve_table(selected_activity)
        if not table:st.warning(f"No approval-ready database table exists for: {selected_activity}");return
        records_df=self.get_records_by_status(table,status)
        if records_df.empty:st.info("No matching records are available in this table.");return
        options={f"{row['faculty_name']} - {row['faculty_id']} - Record {row['record_id']}":int(row["record_id"]) for _,row in records_df.iterrows()};selected=st.selectbox("Select Faculty / Record",list(options.keys()),key=f"hod_{status}_record")
        if selected:self.render_record_card(table,options[selected],status,allow_deny=status=="UN KNOWN")

    def getFacultyList(self,department_name=None):
        try:return pd.DataFrame(get_rows("faculty",{"department":department_name or self.current_department},"faculty_name,faculty_id",order_by="faculty_name"))
        except Exception as e:st.error(f"Faculty Fetch Error: {e}");return pd.DataFrame()

    def getFacultyTableRows(self,table,faculty_id,department_name=None):
        dept=department_name or self.current_department
        aliases={"innovations_in_teaching_learning":"innovation_in_teaching","news_letters_magazines":"news_letters_and_magazines","alumini_networking":"alumni_connection_by_faculties"}
        table=aliases.get(table,table)
        try:
            if table=="faculty_images":return pd.DataFrame()
            if table=="students":return _frame("students",dept,filters={"student_mentor_id":str(faculty_id)})
            if table=="subjects":
                df=_frame("subjects",dept)
                if df.empty:return df
                return df[df["alloted_faculty_ids"].fillna("").apply(lambda x:str(faculty_id).strip() in [i.strip() for i in str(x).split(",")])]
            return _frame(table,dept,filters={"faculty_id":str(faculty_id)})
        except:return pd.DataFrame()

    def cleanFacultyDataFrame(self,df):
        if df.empty:return df
        hidden=["id","department","faculty_id","faculty_name","hod_approval","admin_approval","faculty_password"]
        return df.drop(columns=[c for c in hidden if c in df.columns],errors="ignore")

    def saveHodFeedback(self,faculty_id,faculty_name,score,description):
        try:
            existing=get_one("hod_feedbacks",{"department":self.current_department,"faculty_id":str(faculty_id)},"id")
            data={"faculty_name":faculty_name,"awarded_credits":int(score),"hod_approval":"NOT APPLICABLE","admin_approval":"UN KNOWN","reason":description}
            if existing:update_rows("hod_feedbacks",data,{"department":self.current_department,"id":existing["id"]})
            else:insert_row("hod_feedbacks",{"department":self.current_department,"faculty_id":str(faculty_id),**data})
            return True
        except Exception as e:st.error(f"Feedback Error: {e}");return False

    def _faculty_image(self,department_name,faculty_id):
        try:
            row=get_one("faculty_images",{"department":department_name,"faculty_id":str(faculty_id)},"faculty_image")
            return decode_bytea(row.get("faculty_image")) if row and row.get("faculty_image") else None
        except:return None

    def viewFaculty(self,department_name,faculty_id,faculty_name):
        try:
            image=self._faculty_image(department_name,faculty_id)
            if image:
                try:st.image(BytesIO(image),caption=f"{faculty_name} - {faculty_id}",width="stretch")
                except:st.warning("Unable to display faculty image.")
            else:st.info(f"No Faculty Image Available - {faculty_name} ({faculty_id})")
            st.subheader(f"{faculty_name} - {faculty_id}",divider=True,text_alignment="center")
            for table in tables:
                if table=="faculty_images":continue
                st.subheader(table.replace("_"," ").title(),divider=True);df=self.getFacultyTableRows(table,faculty_id,department_name)
                if df.empty:st.info("No Records Present.");continue
                display_df=self.cleanFacultyDataFrame(df)
                if display_df.empty:st.info("No Displayable Records Present.");continue
                _display(display_df)
            st.subheader("HoD Feedback",divider=True);existing=get_one("hod_feedbacks",{"department":department_name,"faculty_id":str(faculty_id)},"awarded_credits,reason")
            score=st.number_input("Give Score",min_value=0,max_value=100,value=int(existing.get("awarded_credits",0) or 0) if existing else 0,step=1,key=f"hod_feedback_score_{faculty_id}");description=st.text_area("Description",value=str(existing.get("reason","") or "") if existing else "",key=f"hod_feedback_description_{faculty_id}")
            if st.button("Add Feedback",type="primary",width="stretch",key=f"add_hod_feedback_{faculty_id}"):
                if self.saveHodFeedback(faculty_id,faculty_name,score,description):st.success("HoD Feedback Saved Successfully.");st.rerun()
                else:st.warning("Unable To Save HoD Feedback.")
            if st.button("Download Faculty Profile PDF",width="stretch",key=f"download_faculty_pdf_{faculty_id}"):self.downloadFacultyPdf(department_name,faculty_id,faculty_name)
        except Exception as e:st.error(f"Faculty Profile Error: {e}")

    def downloadFacultyPdf(self,department_name,faculty_id,faculty_name):
        st.info("Use Faculty Profile → View Profiles to download the complete appraisal PDF.")

    def main_layout(self):
        with self.col1:option=st.radio("Admin Settings",["Login","HoD","Admin","Principal"],key="admin_settings_navigation")
        if option=="Login":self.login()
        elif option=="HoD":
            if not st.session_state["settings_login"]:
                with self.col2:st.warning("Please login first.")
            elif st.session_state["settings_is_hod"]=="Yes":self.hod_settings()
            else:
                with self.col2:st.error("HoD privileges are required.")
        elif option=="Admin":
            if not st.session_state["settings_login"]:
                with self.col2:st.warning("Please login first.")
            elif st.session_state["settings_is_admin"]=="Yes":self.admin_settings()
            else:
                with self.col2:st.error("Admin privileges are required.")
        elif option=="Principal":
            if not st.session_state["settings_login"]:
                with self.col2:st.warning("Please login first.")
            elif st.session_state["settings_is_principal"]=="Yes":self.principal_settings()
            else:
                with self.col2:st.error("Principal privileges are required.")

    def login(self):
        with self.col2:
            st.subheader("Administrative Login");selected_department=st.selectbox("Select Department",department,key="settings_department_selection");faculty_id=st.text_input("Faculty ID",key="settings_faculty_id_input");faculty_password=st.text_input("Password",type="password",key="settings_faculty_password");login=st.toggle("Login",key="settings_login_toggle")
            if login:
                if not selected_department or not faculty_id or not faculty_password:st.warning("Please enter Department, Faculty ID and Password.");return
                try:
                    result=get_one("faculty",{"department":selected_department,"faculty_id":str(faculty_id).strip(),"faculty_password":faculty_password},"faculty_name,faculty_department,faculty_id,is_hod,is_principal,is_admin")
                    if not result:st.session_state["settings_login"]=False;st.error("Invalid Faculty ID or Password.");return
                    is_hod="Yes" if _truth(result.get("is_hod")) else "No";is_principal="Yes" if _truth(result.get("is_principal")) else "No";is_admin="Yes" if _truth(result.get("is_admin")) else "No";designation="Principal" if is_principal=="Yes" else "Admin" if is_admin=="Yes" else "HoD" if is_hod=="Yes" else "Faculty"
                    st.session_state.update({"settings_login":True,"settings_faculty_name":result.get("faculty_name",""),"settings_faculty_id":str(result.get("faculty_id","")),"settings_department":selected_department,"settings_designation":designation,"settings_is_hod":is_hod,"settings_is_principal":is_principal,"settings_is_admin":is_admin});st.success("Login Successful.");c1,c2,c3=st.columns(3);c1.metric("Faculty",result.get("faculty_name",""));c2.metric("Faculty ID",result.get("faculty_id",""));c3.metric("Designation",designation)
                except Exception as e:st.session_state["settings_login"]=False;st.error(f"Login Error: {e}")
            elif st.session_state["settings_login"]:st.success(f"Logged in as {st.session_state['settings_faculty_name']} ({st.session_state['settings_designation']})")

    def hod_settings(self):
        with self.col2:
            st.subheader("HoD Settings");tab_approvals,tab_denials,tab_feedback=st.tabs(["Approvals","Denials","Give Feedback"])
            with tab_approvals:self.render_status_tab("UN KNOWN")
            with tab_denials:self.render_status_tab("DENIED")
            with tab_feedback:
                faculty_df=self.getFacultyList()
                if faculty_df.empty:st.info("No faculty members are available.")
                else:
                    options={f"{row['faculty_name']} - {row['faculty_id']}":(row["faculty_id"],row["faculty_name"]) for _,row in faculty_df.iterrows()};selected=st.selectbox("Select Faculty",list(options.keys()),key="hod_feedback_faculty")
                    if selected:self.viewFaculty(self.current_department,*options[selected])

    def principal_settings(self):
        with self.col2:
            if st.session_state.get("settings_is_principal")!="Yes":st.error("Principal privileges are required.");return
            st.subheader("Principal Settings");selected_department=st.pills("Select Department",department,selection_mode="single",key="principal_department")
            if selected_department:
                faculty_df=self.getFacultyList(selected_department)
                if faculty_df.empty:st.info("No faculty members are available in this department.");return
                options={f"{row['faculty_name']} - {row['faculty_id']}":(row["faculty_id"],row["faculty_name"]) for _,row in faculty_df.iterrows()};selected=st.selectbox("Select Faculty",list(options.keys()),key="principal_faculty")
                if selected:self.view_by_principal(selected_department,*options[selected])

    def view_by_principal(self,department_name,faculty_id,faculty_name):
        try:
            image=self._faculty_image(department_name,faculty_id)
            if image:
                try:st.image(BytesIO(image),caption=f"{faculty_name} - {faculty_id}",width=220)
                except:st.warning("Unable to display faculty image.")
            else:st.info(f"No Faculty Image Available - {faculty_name} ({faculty_id})")
            st.subheader(f"{faculty_name} - {faculty_id}",divider=True,text_alignment="center")
            for table in tables:
                if table=="faculty_images":continue
                st.subheader(table.replace("_"," ").title(),divider=True);df=self.getFacultyTableRows(table,faculty_id,department_name)
                if df.empty:st.info("No Records Present.");continue
                display_df=self.cleanFacultyDataFrame(df)
                if display_df.empty:st.info("No Displayable Records Present.");continue
                _display(display_df)
            st.subheader("HoD Feedback",divider=True);feedback=pd.DataFrame(get_rows("hod_feedbacks",{"department":department_name,"faculty_id":str(faculty_id)},"awarded_credits,reason"))
            if feedback.empty:st.info("No HoD Feedback Present.")
            else:_display(feedback.rename(columns={"awarded_credits":"HoD Score","reason":"Reason"}))
            if st.button("Download Faculty Profile PDF",width="stretch",key=f"principal_download_{department_name}_{faculty_id}"):self.downloadFacultyPdf(department_name,faculty_id,faculty_name)
        except Exception as e:st.error(f"Faculty Profile Error: {e}")

    def get_admin_summary(self,department_name,category,mode):
        label={"hod_denied":"HoD Denied Count","hod_approved":"HoD Approved Count","admin_approved":"Admin Approved Count","admin_denied":"Admin Denied Count"}.get(mode,"Count");rows=[]
        for activity in categories.get(category,[]):
            table=self.resolve_table(activity);count=0
            if table:
                try:
                    data=get_rows(table,{"department":department_name},"hod_approval,admin_approval")
                    if mode=="hod_denied":count=sum(1 for r in data if r.get("hod_approval")=="DENIED" and r.get("admin_approval")=="UN KNOWN")
                    elif mode=="hod_approved":count=sum(1 for r in data if r.get("hod_approval")=="APPROVED" and r.get("admin_approval") in {"UN KNOWN","DENIED"})
                    elif mode=="admin_approved":count=sum(1 for r in data if r.get("admin_approval")=="APPROVED")
                    elif mode=="admin_denied":count=sum(1 for r in data if r.get("admin_approval")=="DENIED")
                except:count=0
            rows.append({"Tables":activity,label:count})
        return pd.DataFrame(rows)

    def get_admin_records(self,department_name,table,mode):
        try:
            rows=get_rows(table,{"department":department_name},"id,faculty_id,faculty_name,hod_approval,admin_approval",order_by="id",descending=True)
            if mode=="hod_denied":rows=[r for r in rows if r.get("hod_approval")=="DENIED" and r.get("admin_approval")=="UN KNOWN"]
            elif mode=="hod_approved":rows=[r for r in rows if r.get("hod_approval")=="APPROVED" and r.get("admin_approval") in {"UN KNOWN","DENIED"}]
            elif mode=="admin_approved":rows=[r for r in rows if r.get("admin_approval")=="APPROVED"]
            elif mode=="admin_denied":rows=[r for r in rows if r.get("admin_approval")=="DENIED"]
            else:return pd.DataFrame()
            return pd.DataFrame([{"record_id":r.get("id"),"faculty_id":r.get("faculty_id"),"faculty_name":r.get("faculty_name")} for r in rows])
        except Exception as e:st.error(f"Unable to fetch records: {e}");return pd.DataFrame()

    def get_admin_record(self,department_name,table,record_id):
        return self.get_record(table,record_id,department_name)

    def update_admin_status(self,department_name,table,record_id,status):
        try:
            if not get_one(table,{"department":department_name,"id":record_id},"id"):return False
            update_rows(table,{"admin_approval":status},{"department":department_name,"id":record_id});return True
        except Exception as e:st.error(f"Admin Update Error: {e}");return False

    def render_admin_record(self,department_name,table,record_id,key_prefix):
        record=self.get_admin_record(department_name,table,record_id)
        if not record:return
        with st.container(border=True):
            st.subheader(f"{record.get('faculty_name','Faculty')} - {record.get('faculty_id','')}",divider=True,text_alignment="center")
            data=[(k,v) for k,v in record.items() if k not in ["record_id","faculty_name","faculty_id"]]
            for i in range(0,len(data),3):
                cols=st.columns(3)
                for j,(key,value) in enumerate(data[i:i+3]):
                    with cols[j]:st.caption(key.replace("_"," ").title());st.write(value if value not in [None,""] else "—")
            c1,c2=st.columns(2)
            with c1:approve=st.button("Approve",type="primary",width="stretch",key=f"{key_prefix}_approve_{department_name}_{table}_{record_id}")
            with c2:deny=st.button("Deny",type="primary",width="stretch",key=f"{key_prefix}_deny_{department_name}_{table}_{record_id}")
            if approve:
                if self.update_admin_status(department_name,table,record_id,"APPROVED"):st.success("Record Approved Successfully.");st.rerun()
                else:st.warning("Record Could Not Be Approved.")
            if deny:
                if self.update_admin_status(department_name,table,record_id,"DENIED"):st.success("Record Denied Successfully.");st.rerun()
                else:st.warning("Record Could Not Be Denied.")

    def render_admin_activity(self,department_name,mode,key_prefix):
        selected_category=st.selectbox("Select Category",list(categories.keys()),key=f"{key_prefix}_category")
        if not selected_category:return
        st.dataframe(self.get_admin_summary(department_name,selected_category,mode),use_container_width=True,hide_index=True)
        selected_activity=st.selectbox("Select Table",categories[selected_category],key=f"{key_prefix}_table")
        if not selected_activity:return
        table=self.resolve_table(selected_activity)
        if not table:st.warning(f"No approval-ready database table exists for: {selected_activity}");return
        records=self.get_admin_records(department_name,table,mode)
        if records.empty:st.info("No Records Present.");return
        options={f"{row['faculty_name']} - {row['faculty_id']} - Record {row['record_id']}":int(row["record_id"]) for _,row in records.iterrows()};selected=st.selectbox("Select Faculty / Record",list(options.keys()),key=f"{key_prefix}_faculty")
        if selected:self.render_admin_record(department_name,table,options[selected],key_prefix)

    def admin_faculty_profile(self,department_name):
        faculty_df=self.getFacultyList(department_name)
        if faculty_df.empty:st.info("No faculty members are available in this department.");return
        options={f"{row['faculty_name']} - {row['faculty_id']}":(row["faculty_id"],row["faculty_name"]) for _,row in faculty_df.iterrows()};selected=st.selectbox("Select Faculty",list(options.keys()),key=f"admin_profile_faculty_{department_name}")
        if selected:self.view_by_principal(department_name,*options[selected])

    def admin_settings(self):
        with self.col2:
            if st.session_state.get("settings_is_admin")!="Yes":st.error("Admin privileges are required.");return
            st.subheader("Admin Settings");selected_department=st.pills("Select Department",department,selection_mode="single",key="admin_department")
            if not selected_department:return
            tab_approve,tab_deny,tab_view=st.tabs(["Approve","Deny","View"])
            with tab_approve:st.subheader("HoD Denied Records",divider=True);self.render_admin_activity(selected_department,"hod_denied",f"admin_approve_{selected_department}")
            with tab_deny:st.subheader("HoD Approved Records",divider=True);self.render_admin_activity(selected_department,"hod_approved",f"admin_deny_{selected_department}")
            with tab_view:
                view_option=st.pills("View",["Approvals","Denials","Faculty Profile"],selection_mode="single",key=f"admin_view_option_{selected_department}")
                if view_option=="Approvals":st.subheader("Admin Approved Records",divider=True);self.render_admin_activity(selected_department,"admin_approved",f"admin_view_approved_{selected_department}")
                elif view_option=="Denials":st.subheader("Admin Denied Records",divider=True);self.render_admin_activity(selected_department,"admin_denied",f"admin_view_denied_{selected_department}")
                elif view_option=="Faculty Profile":st.subheader("Faculty Profile",divider=True);self.admin_faculty_profile(selected_department)
