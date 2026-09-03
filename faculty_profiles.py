from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from streamlit_extras.metric_cards import style_metric_cards
from global_fields import department
from database import get_rows,get_one,decode_bytea

class viewProfiles:
    def __init__(self):
        self.base_dir=Path(__file__).resolve().parent
        self.data_dir=(self.base_dir.parent/"data").resolve()
        self.institute_banner=self.data_dir/"image.png"
        self.category_caps={"Academic Activities":40.0,"Research And Development":40.0,"Academic Extensions":20.0}
        self.categories={
            "Academic Activities":[("Academic Results","academic_results"),("Students Feedback","feedback"),("HoD Feedback","hod_feedbacks"),("Project Guidence","project_guidence"),("Innovations In Teaching Learning","innovation_in_teaching"),("OBE Practice","obe_practice"),("Product Development By Student","product_development_by_student"),("Student Participation And Winning In Seminar, Workshop, Symposium, Conference, etc","seminar_workshop_conference_symposium_by_students"),("Student Participation & Wining in project Competition & MNC Contest","competetion_contest__by_students"),("Language Certification Courses","language_certifications"),("Online Certification (min 1 week) courses","online_certifications"),("Internship & In-plant Training (minimum 15 days)","internships_inplant_training"),("Special Awards from Institute and Industry","special_awards"),("Students Involvement in Entrepreneurship & Start-ups","student_involvements_in_startups"),("Competitive Examinations","competetive_examinations"),("Placement","placements"),("Examination Results","examination_results_faculty"),("Achievement of ICT and Skill Rack Target","ict_skill_rack"),("Hacker Rank/Hacker Earth","coding_data")],
            "Research And Development":[("Publication - Journals, Conferences & Book Chapters","publications_conferences_journals_book_chapters"),("Patents & Copyrights","patent_copy_rights"),("Consultancy, Funding & Grants","consultancy_funding_grants"),("Citation Impact Of Published Work","citation_impacts"),("Ph.D Guidance","phd_guidance"),("Book Publication","book_publications")],
            "Academic Extensions":[("Arranging On Campus Recruitment","on_campus_recruitments_by_faculty"),("Guest Lectures Delivered (Per Day)","guest_lectures"),("Online Certification (min 4 week)","online_certifications_4weeks"),("Online Lecture Series / MOOC Course Developed","mooc_courses_by_faculty"),("News Letter & Magazine","news_letters_and_magazines"),("Events Participations (NIRF Ranked Institutes Only)","nirf_event_participations"),("Special Awards and Fellowship from Recognized Professional Bodies","special_awards_fellowships"),("Faculty Exchange (Min 1 week)","faculty_exchanges"),("Extension Activities Organized","extension_activities"),("Alumni Networking","alumni_connection_by_faculties"),("Collaboration With Industry/Institute","collaborations_industry_institute"),("Value Added Courses Conducted/Organized","value_added_courses"),("Organizing International Conference","organizing_international_conference"),("Event Organized","event_organizations"),("Memberships","membership")]
        }
        self.all_scoring_tables=[]
        for activities in self.categories.values():
            for _,table in activities:
                if table not in self.all_scoring_tables:self.all_scoring_tables.append(table)
        self.score_config=self.loadScoreConfig()

    def defaultScoreConfig(self):
        rows=[("examination_results_faculty",2,0,0),("academic_results",10,0,0),("feedback",4,0,0),("hod_feedbacks",5,0,0),("project_guidence",2,0,0),("obe_practice",5,0,0),("product_development_by_student",15,0,0),("seminar_workshop_conference_symposium_by_students",15,0,0),("competetion_contest__by_students",15,0,0),("language_certifications",5,0,0),("online_certifications",5,0,0),("internships_inplant_training",15,0,0),("special_awards",15,0,0),("student_involvements_in_startups",15,0,0),("competetive_examinations",4,0,0),("placements",15,0,0),("ict_skill_rack",2,0,0),("coding_data",15,0,0),("publications_conferences_journals_book_chapters",20,12,8),("patent_copy_rights",10,0,0),("consultancy_funding_grants",27,4,0),("citation_impacts",4,0,0),("phd_guidance",15,2,0),("book_publications",15,0,0),("on_campus_recruitments_by_faculty",9,0,0),("guest_lectures",3,0,0),("online_certifications_4weeks",4,0,0),("mooc_courses_by_faculty",5,0,0),("news_letters_and_magazines",4,0,0),("nirf_event_participations",4,0,0),("faculty_exchanges",5,0,0),("extension_activities",4,0,0),("alumni_connection_by_faculties",3,0,0),("collaborations_industry_institute",5,0,0),("value_added_courses",2,0,0),("organizing_international_conference",5,0,0),("event_organizations",5,0,0),("innovation_in_teaching",4,0,0),("membership",2,0,0),("special_awards_fellowships",4,0,0)]
        return {t:{"score":float(s),"min_score_professor":float(p),"min_score_for_non_phd_holders":float(n)} for t,s,p,n in rows}

    def normalizeConfigFrame(self,df):
        if df is None or df.empty or "table_name" not in df.columns or "score" not in df.columns:return {}
        prof=next((c for c in ["min_score_professor","min_score_for_professors","min_score_for_preofessors","min_score_for_professor"] if c in df.columns),None)
        nonphd=next((c for c in ["min_score_for_non_phd_holders","min_score_non_phd_holders","min_score_for_non_phd_holder"] if c in df.columns),None)
        work=pd.DataFrame({"table_name":df["table_name"].fillna("").astype(str).str.strip(),"score":pd.to_numeric(df["score"],errors="coerce").fillna(0.0),"min_score_professor":pd.to_numeric(df[prof],errors="coerce").fillna(0.0) if prof else 0.0,"min_score_for_non_phd_holders":pd.to_numeric(df[nonphd],errors="coerce").fillna(0.0) if nonphd else 0.0})
        names=work["table_name"].str.lower().tolist();special=[i for i,n in enumerate(names) if n=="special_awards"]
        if "special_awards_fellowships" not in names and len(special)>1:work.loc[work.index[special[1]],"table_name"]="special_awards_fellowships"
        work["key"]=work["table_name"].str.lower();work=work[work["key"]!=""].drop_duplicates("key",keep="first")
        return {r["key"]:{"score":float(r["score"]),"min_score_professor":float(r["min_score_professor"]),"min_score_for_non_phd_holders":float(r["min_score_for_non_phd_holders"])} for _,r in work.iterrows()}

    def loadScoreConfig(self):
        defaults=self.defaultScoreConfig()
        try:
            rows=get_rows("max_scores_for_fs",columns="table_name,score,min_score_professor,min_score_for_non_phd_holders")
            loaded=self.normalizeConfigFrame(pd.DataFrame(rows))
            if loaded:defaults.update(loaded);return defaults
        except Exception as e:
            st.warning(f"Supabase Score Configuration Error: {e}")

        candidates=[self.data_dir/"faculty_score_config.csv",self.data_dir/"2026-08-30T14-58_export.csv",self.base_dir/"faculty_score_config.csv",self.base_dir/"2026-08-30T14-58_export.csv"]

        for path in candidates:
            try:
                if path.exists():
                    loaded=self.normalizeConfigFrame(pd.read_csv(path))
                    if loaded:defaults.update(loaded);break
            except Exception as e:
                st.warning(f"Score CSV Error: {e}")

        return defaults

    def getConfig(self,table_name):
        return self.score_config.get(str(table_name).strip().lower(),{"score":0.0,"min_score_professor":0.0,"min_score_for_non_phd_holders":0.0})

    def getFacultyList(self,department_name):
        try:
            rows=get_rows("faculty",{"department":department_name},"faculty_id,faculty_name",order_by="faculty_name")
            df=pd.DataFrame(rows,columns=["faculty_id","faculty_name"])
            if df.empty:return df
            return df[df["faculty_id"].notna()].reset_index(drop=True)
        except Exception as e:
            st.error(f"Faculty Fetch Error: {e}")
            return pd.DataFrame()

    def getFacultyProfile(self,department_name,faculty_id):
        try:
            row=get_one("faculty",{"department":department_name,"faculty_id":str(faculty_id)})
            if not row:return {}
            row=dict(row);row.pop("id",None);row.pop("department",None)
            return row
        except Exception as e:
            st.error(f"Faculty Profile Error: {e}")
            return {}

    def getFacultyImage(self,department_name,faculty_id):
        try:
            row=get_one("faculty_images",{"department":department_name,"faculty_id":str(faculty_id)},"faculty_image")
            return decode_bytea(row.get("faculty_image")) if row and row.get("faculty_image") else None
        except:
            return None

    def getApprovalTables(self,department_name):
        return self.all_scoring_tables.copy()

    def normalizeApproval(self,value):
        value=" ".join(str(value or "").strip().upper().replace("_"," ").split())
        if value in {"UNKNOWN","UN-KNOWN","UN KNOWN"}:return "UN KNOWN"
        if value in {"NA","N/A","NOT APPLICABLE"}:return "NOT APPLICABLE"
        return value

    def isApproved(self,hod,admin):
        hod=self.normalizeApproval(hod);admin=self.normalizeApproval(admin);denied={"DENIED","DENIEL","DENIAL"}
        if admin=="APPROVED":return True
        if admin in denied:return False
        if admin=="UN KNOWN":return hod=="APPROVED"
        if admin=="NOT APPLICABLE":return hod in {"APPROVED","NOT APPLICABLE"}
        return False

    def getScoreColumn(self,df):
        return next((c for c in ["credits","awarded_credits","awarded_credit","credit"] if c in df.columns),None)

    def getDesignation(self,profile):
        designation=str(profile.get("designation",profile.get("faculty_designation","")) or "").strip().lower()
        if designation=="professor" or designation.startswith("professor "):return "professor"
        if "associate professor" in designation:return "associate professor"
        if "assistant professor" in designation:return "assistant professor"
        return designation

    def isPhdHolder(self,profile):
        return str(profile.get("is_phd_holder",profile.get("faculty_is_phd_holder",profile.get("phd_holder",""))) or "").strip().lower() in {"yes","true","1","y"}

    def getDesignationRequirements(self,profile):
        designation=self.getDesignation(profile);phd=self.isPhdHolder(profile);recognized=True
        if designation=="professor":values=(25.0,25.0,10.0,60.0)
        elif designation=="associate professor":values=(25.0,20.0,10.0,55.0)
        elif designation=="assistant professor" and phd:values=(25.0,20.0,5.0,50.0)
        elif designation=="assistant professor":values=(25.0,10.0,5.0,40.0)
        else:values=(0.0,0.0,0.0,0.0);recognized=False
        return {"Academic Activities":values[0],"Research And Development":values[1],"Academic Extensions":values[2],"minimum_total_marks":values[3],"designation":str(profile.get("designation",profile.get("faculty_designation","Not Available")) or "Not Available"),"is_phd_holder":"Yes" if phd else "No","recognized":recognized}

    def getTableMinimum(self,table_name,profile):
        config=self.getConfig(table_name);designation=self.getDesignation(profile)
        if designation=="professor":return config["min_score_professor"]
        if designation=="assistant professor" and not self.isPhdHolder(profile):return config["min_score_for_non_phd_holders"]
        return 0.0

    def getDetailedTableResult(self,department_name,faculty_id,faculty_name,table_name,faculty_profile):
        config=self.getConfig(table_name);maximum=float(config["score"]);minimum=self.getTableMinimum(table_name,faculty_profile)
        empty={"total_score_achieved":0.0,"score_approved":0.0,"score_considered":0.0,"max_score":maximum,"minimum_required":minimum,"minimum_satisfied":minimum<=0}

        try:
            rows=get_rows(table_name,{"department":department_name,"faculty_id":str(faculty_id)})
            df=pd.DataFrame(rows)

            if df.empty:return pd.DataFrame(),empty

            score_col=self.getScoreColumn(df)
            if not score_col:return pd.DataFrame(),empty

            scores=pd.to_numeric(df[score_col],errors="coerce").fillna(0.0)
            total=float(scores.sum())

            if table_name=="hod_feedbacks":
                eligible_df=df.copy()
            elif "hod_approval" in df.columns and "admin_approval" in df.columns:
                eligible_df=df.loc[df.apply(lambda row:self.isApproved(row.get("hod_approval"),row.get("admin_approval")),axis=1)].copy()
            else:
                eligible_df=df.iloc[0:0].copy()

            eligible_scores=pd.to_numeric(eligible_df[score_col],errors="coerce").fillna(0.0) if not eligible_df.empty else pd.Series(dtype=float)
            approved=float(eligible_scores.sum())
            considered=min(approved,maximum) if maximum>0 else 0.0
            minimum_ok=considered>=minimum if minimum>0 else True
            display_df=eligible_df.drop(columns=[c for c in ["id","department","faculty_id","faculty_name","hod_approval","admin_approval"] if c in eligible_df.columns],errors="ignore").reset_index(drop=True)

            return display_df,{"total_score_achieved":total,"score_approved":approved,"score_considered":considered,"max_score":maximum,"minimum_required":minimum,"minimum_satisfied":minimum_ok}
        except Exception as e:
            st.warning(f"{table_name} Score Error: {e}")
            return pd.DataFrame(),empty

    def getTableResult(self,department_name,faculty_id,table_name,faculty_name=None,faculty_profile=None):
        faculty_profile=faculty_profile or self.getFacultyProfile(department_name,faculty_id)
        faculty_name=faculty_name or str(faculty_profile.get("faculty_name","") or "")
        df,score=self.getDetailedTableResult(department_name,faculty_id,faculty_name,table_name,faculty_profile)
        return df,score["score_approved"],score["max_score"]

    def getConsideredScore(self,score,maximum):
        return min(float(score or 0),float(maximum or 0)) if float(maximum or 0)>0 else 0.0

    def getCategoryWiseScores(self,all_scores):
        result={}

        for category,activities in self.categories.items():
            tables=[]
            for _,table in activities:
                if table not in tables:tables.append(table)

            total=sum(float(all_scores.get(table,{}).get("total_score_achieved",0) or 0) for table in tables)
            approved=sum(float(all_scores.get(table,{}).get("score_approved",0) or 0) for table in tables)
            table_considered=sum(float(all_scores.get(table,{}).get("score_considered",0) or 0) for table in tables)
            cap=self.category_caps[category]

            result[category]={"total_score_achieved":total,"score_approved":approved,"table_considered":table_considered,"score_considered":min(table_considered,cap),"max_score":cap}

        return result

    def getRequirementResults(self,category_scores,all_scores,profile):
        req=self.getDesignationRequirements(profile);rows=[];category_ok=req["recognized"]

        for category in self.category_caps:
            obtained=category_scores[category]["score_considered"];required=req[category];ok=req["recognized"] and obtained>=required
            category_ok=category_ok and ok
            rows.append({"Category":category,"Minimum Required":required,"Score Considered":obtained,"Satisfied":"YES" if ok else "NO"})

        final_score=sum(value["score_considered"] for value in category_scores.values())
        total_ok=req["recognized"] and final_score>=req["minimum_total_marks"]
        category_ok=category_ok and total_ok
        activity_rows=[];activity_ok=True

        for table,score in all_scores.items():
            required=float(score.get("minimum_required",0) or 0)

            if required<=0:continue

            ok=float(score.get("score_considered",0) or 0)>=required
            activity_ok=activity_ok and ok
            activity_rows.append({"Activity":self.getActivityTitle(table),"Minimum Required":required,"Score Considered":score["score_considered"],"Satisfied":"YES" if ok else "NO"})

        overall=category_ok and activity_ok
        return pd.DataFrame(rows),pd.DataFrame(activity_rows),category_ok,activity_ok,overall,final_score,req

    def getActivityTitle(self,table_name):
        for activities in self.categories.values():
            for title,table in activities:
                if table==table_name:return title
        return table_name.replace("_"," ").title()

    def displayFacultyProfile(self,profile,faculty_image):
        st.subheader("Faculty Personal Details",divider=True)

        with st.container(border=True):
            if faculty_image:
                try:st.image(faculty_image,width="stretch")
                except:st.warning("Unable To Display Faculty Image.")
            else:
                st.info("No Faculty Image Present.")

            data=[(key,value) for key,value in profile.items() if key!="faculty_password"]

            for i in range(0,len(data),3):
                cols=st.columns(3)

                for j,(key,value) in enumerate(data[i:i+3]):
                    with cols[j]:
                        st.caption(key.replace("_"," ").title())
                        st.write(value if value not in [None,""] else "—")

    def displayTableSection(self,title,df,score,max_score=None):
        if not isinstance(score,dict):score={"total_score_achieved":float(score or 0),"score_approved":float(score or 0),"max_score":float(max_score or 0),"score_considered":self.getConsideredScore(score,max_score),"minimum_required":0.0,"minimum_satisfied":True}

        st.subheader(title,divider=True)
        col1,col2,col3,col4=st.columns(4)
        col1.metric("Total Score Achieved",f"{score['total_score_achieved']:.2f}")
        col2.metric("Score Approved",f"{score['score_approved']:.2f}")
        col3.metric("Maximum Score",f"{score['max_score']:.2f}")
        col4.metric("Score Considered",f"{score['score_considered']:.2f}")
        style_metric_cards()

        if score.get("minimum_required",0)>0:st.info(f"Minimum Required: {score['minimum_required']:.2f} | {'Satisfied' if score.get('minimum_satisfied') else 'Not Satisfied'}")

        if df.empty:st.info("No Score-Eligible Records Present.")
        else:st.dataframe(df,use_container_width=True,hide_index=True)

    def safeValue(self,value):
        if value is None:return ""
        try:
            if pd.isna(value):return ""
        except:pass
        return str(value)

    def p(self,value,style):
        return Paragraph(escape(self.safeValue(value)),style)

    def pageBorder(self,canvas,doc):
        canvas.saveState();width,height=A4
        canvas.setStrokeColor(colors.HexColor("#64748B"));canvas.setLineWidth(.8);canvas.rect(12,12,width-24,height-24)
        canvas.setFillColor(colors.HexColor("#64748B"));canvas.setFont("Helvetica",8);canvas.drawRightString(width-20,18,f"Page {doc.page}")
        canvas.restoreState()

    def heading(self,title,style,width):
        line=Table([[""]],colWidths=[width],rowHeights=[2])
        line.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#0F766E"))]))
        return [Spacer(1,7),self.p(title.upper(),style),line,Spacer(1,7)]

    def makeTable(self,data,widths=None,header=True,font=8):
        table=Table(data,colWidths=widths,repeatRows=1 if header else 0)
        commands=[("GRID",(0,0),(-1,-1),.35,colors.HexColor("#CBD5E1")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(0,0),(-1,-1),"CENTER"),("FONTSIZE",(0,0),(-1,-1),font),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]

        if header:commands += [("BACKGROUND",(0,0),(-1,0),colors.HexColor("#D5F5EF")),("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#115E59")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]

        table.setStyle(TableStyle(commands))
        return table

    def pdfDataTable(self,df,width,normal):
        if df.empty:return None

        n=len(df.columns)
        font=8 if n<=5 else 6.7 if n<=8 else 5.7 if n<=11 else 4.8
        head=ParagraphStyle(f"ph{n}",parent=normal,fontName="Helvetica-Bold",fontSize=font,leading=font+1.1,textColor=colors.HexColor("#115E59"),alignment=TA_CENTER)
        cell=ParagraphStyle(f"pc{n}",parent=normal,fontSize=font,leading=font+1.1)
        data=[[self.p(str(column).replace("_"," ").title(),head) for column in df.columns]]

        for _,row in df.iterrows():data.append([self.p(self.safeValue(value)[:350],cell) for value in row.tolist()])

        return self.makeTable(data,[width/n]*n,True,font)

    def categoryChart(self,category_scores,width):
        drawing=Drawing(width,235)
        chart=VerticalBarChart();chart.x=45;chart.y=45;chart.width=width-90;chart.height=150
        categories=list(self.category_caps);keys=["total_score_achieved","score_approved","score_considered","max_score"]
        chart.data=[[float(category_scores[category][key]) for category in categories] for key in keys]
        chart.categoryAxis.categoryNames=["Academic","R & D","Extensions"]
        highest=max([max(series) if series else 0 for series in chart.data]+[0])
        chart.valueAxis.valueMin=0;chart.valueAxis.valueMax=max(5,highest+5);chart.valueAxis.valueStep=max(1,int(chart.valueAxis.valueMax/5))
        palette=[colors.HexColor("#64748B"),colors.HexColor("#2563EB"),colors.HexColor("#0F766E"),colors.HexColor("#94A3B8")]

        for i,color in enumerate(palette):chart.bars[i].fillColor=color

        legend=Legend();legend.x=45;legend.y=220;legend.fontSize=7;legend.colorNamePairs=list(zip(palette,["Total Achieved","Approved","Considered","Maximum"]))
        drawing.add(chart);drawing.add(legend)
        return drawing

    def activityChart(self,all_scores,width):
        rows=sorted([(self.getActivityTitle(table),float(value.get("score_approved",0)),float(value.get("score_considered",0))) for table,value in all_scores.items()],key=lambda item:item[2],reverse=True)[:10]
        drawing=Drawing(width,255)

        if not rows:return drawing

        chart=VerticalBarChart();chart.x=40;chart.y=80;chart.width=width-70;chart.height=125
        chart.data=[[row[1] for row in rows],[row[2] for row in rows]]
        chart.categoryAxis.categoryNames=[row[0][:14] for row in rows];chart.categoryAxis.labels.angle=35;chart.categoryAxis.labels.fontSize=5.5;chart.categoryAxis.labels.dy=-8
        highest=max([max(series) if series else 0 for series in chart.data]+[0])
        chart.valueAxis.valueMin=0;chart.valueAxis.valueMax=max(2,highest+2)
        palette=[colors.HexColor("#2563EB"),colors.HexColor("#0F766E")]
        chart.bars[0].fillColor=palette[0];chart.bars[1].fillColor=palette[1]

        legend=Legend();legend.x=45;legend.y=240;legend.fontSize=7;legend.colorNamePairs=list(zip(palette,["Approved","Considered"]))
        drawing.add(chart);drawing.add(legend)
        return drawing

    def normalizeLegacyScores(self,all_scores):
        normalized={}

        for table,value in (all_scores or {}).items():
            if isinstance(value,dict) and "score_considered" in value:
                normalized[table]=value
                continue

            raw=float(value.get("score",0) if isinstance(value,dict) else value or 0)
            maximum=float(value.get("max_score",self.getConfig(table)["score"]) if isinstance(value,dict) else self.getConfig(table)["score"])
            normalized[table]={"total_score_achieved":raw,"score_approved":raw,"score_considered":self.getConsideredScore(raw,maximum),"max_score":maximum,"minimum_required":0.0,"minimum_satisfied":True}

        return normalized

    def convert_to_pdf(self,all_scores=None,all_dataframes=None,faculty_image=None,faculty_profile=None,table_names=None,all_scores_from_all_tables=None,all_df_from_tables=None,**kwargs):
        all_scores=self.normalizeLegacyScores(all_scores or all_scores_from_all_tables or {})
        all_dataframes=all_dataframes or all_df_from_tables or {}
        faculty_profile=faculty_profile or {}
        buffer=BytesIO()
        page_width,_=A4;margin=22;width=page_width-margin*2
        doc=SimpleDocTemplate(buffer,pagesize=A4,leftMargin=margin,rightMargin=margin,topMargin=margin,bottomMargin=26)
        styles=getSampleStyleSheet()
        title=ParagraphStyle("title",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=19,leading=23,textColor=colors.HexColor("#17365D"),alignment=TA_CENTER)
        section=ParagraphStyle("section",parent=styles["Heading1"],fontName="Helvetica-Bold",fontSize=13,textColor=colors.HexColor("#0F766E"))
        activity=ParagraphStyle("activity",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=10,textColor=colors.HexColor("#334155"))
        normal=ParagraphStyle("normal",parent=styles["BodyText"],fontSize=7.2,leading=8.6)
        label=ParagraphStyle("label",parent=normal,fontName="Helvetica-Bold",textColor=colors.HexColor("#0F766E"))
        story=[]

        if self.institute_banner.exists():
            try:story.append(Image(str(self.institute_banner),width=width,height=78))
            except:pass

        story += [Spacer(1,10),self.p("FACULTY APPRAISAL SYSTEM",title),Spacer(1,8)]

        if faculty_image:
            try:story.append(Image(BytesIO(faculty_image),width=width,height=210))
            except:pass

        story += self.heading("Faculty Personal Details",section,width)
        details=[(key,value) for key,value in faculty_profile.items() if key!="faculty_password"]
        rows=[]

        for i in range(0,len(details),2):
            row=[]

            for key,value in details[i:i+2]:
                row.extend([self.p(key.replace("_"," ").title(),label),self.p(value,normal)])

            while len(row)<4:row.extend(["",""])

            rows.append(row)

        if rows:story.append(self.makeTable(rows,[width*.18,width*.32,width*.18,width*.32],False,7.0))

        story.append(PageBreak())

        category_scores=self.getCategoryWiseScores(all_scores)
        category_req,activity_req,category_ok,activity_ok,overall_ok,final_score,requirements=self.getRequirementResults(category_scores,all_scores,faculty_profile)

        story += self.heading("Category Wise Performance",section,width)
        category_data=[["Category","Total Achieved","Approved","Considered","Maximum"]]+[[category,f"{value['total_score_achieved']:.2f}",f"{value['score_approved']:.2f}",f"{value['score_considered']:.2f}",f"{value['max_score']:.2f}"] for category,value in category_scores.items()]+[["TOTAL",f"{sum(value['total_score_achieved'] for value in category_scores.values()):.2f}",f"{sum(value['score_approved'] for value in category_scores.values()):.2f}",f"{final_score:.2f}","100.00"]]
        story.append(self.makeTable(category_data,[width*.30,width*.18,width*.17,width*.17,width*.18],True,7.5))

        story += self.heading("Minimum Requirement",section,width)
        req_data=[["Category","Minimum Required","Score Considered","Satisfied"]]+category_req.values.tolist()+[["TOTAL",f"{requirements['minimum_total_marks']:.2f}",f"{final_score:.2f}","YES" if category_ok else "NO"]]
        story.append(self.makeTable(req_data,[width*.40,width*.20,width*.20,width*.20],True,7.5))
        story += [Spacer(1,6),self.p(f"Designation: {requirements['designation']} | PhD Holder: {requirements['is_phd_holder']}",normal)]

        if not requirements["recognized"]:story += [Spacer(1,4),self.p("Designation is not mapped to a minimum-requirement rule.",normal)]

        if not activity_req.empty:
            story += self.heading("Activity Wise Mandatory Minimums",section,width)
            story.append(self.makeTable([["Activity","Minimum Required","Score Considered","Satisfied"]]+activity_req.values.tolist(),[width*.52,width*.16,width*.16,width*.16],True,7.1))

        story += self.heading("Final Result",section,width)
        performance=final_score
        story.append(self.makeTable([["Final Score","Maximum","Performance","Category Minimums","Activity Minimums","Overall"],[f"{final_score:.2f}","100.00",f"{performance:.2f}%","YES" if category_ok else "NO","YES" if activity_ok else "NO","SATISFIED" if overall_ok else "NOT SATISFIED"]],[width/6]*6,True,7.0))
        story.append(PageBreak())

        story += self.heading("Performance Charts",section,width)
        story.append(self.categoryChart(category_scores,width))
        story.append(Spacer(1,5))
        story.append(self.activityChart(all_scores,width))
        story.append(PageBreak())

        displayed=set()

        for category,activities in self.categories.items():
            valid=[(title_name,table) for title_name,table in activities if table in all_scores and table not in displayed]

            if not valid:continue

            story += self.heading(category,section,width)

            for title_name,table in valid:
                displayed.add(table)
                score=all_scores[table]
                block=[self.p(title_name,activity),self.makeTable([["Total Achieved","Approved","Maximum","Considered","Minimum"],[f"{score['total_score_achieved']:.2f}",f"{score['score_approved']:.2f}",f"{score['max_score']:.2f}",f"{score['score_considered']:.2f}",f"{score.get('minimum_required',0):.2f}"]],[width/5]*5,True,7.2),Spacer(1,5)]
                story.append(KeepTogether(block))
                df=all_dataframes.get(table,pd.DataFrame())

                if df.empty:
                    story.append(self.p("No score-eligible records present.",normal))
                else:
                    table_obj=self.pdfDataTable(df,width,normal)
                    if table_obj:story.append(table_obj)

                story.append(Spacer(1,10))

        doc.build(story,onFirstPage=self.pageBorder,onLaterPages=self.pageBorder)
        buffer.seek(0)
        return buffer.getvalue()

    def download_pdf(self,created_pdf,faculty_id):
        st.download_button("Download Faculty Appraisal PDF",data=created_pdf,file_name=f"{faculty_id}_faculty_appraisal.pdf",mime="application/pdf",type="primary",width="stretch",key=f"faculty_profile_pdf_{faculty_id}")

    def renderFaculty(self,department_name,faculty_id,faculty_name):
        profile=self.getFacultyProfile(department_name,faculty_id)
        image=self.getFacultyImage(department_name,faculty_id)

        if not profile:
            st.warning("Faculty Profile Not Found.")
            return

        self.displayFacultyProfile(profile,image)
        available=self.getApprovalTables(department_name)

        if not available:
            st.warning("No Faculty Scoring Tables Found.")
            return

        all_scores={}
        all_dataframes={}

        for table in self.all_scoring_tables:
            if table not in available:continue
            df,score=self.getDetailedTableResult(department_name,faculty_id,faculty_name,table,profile)
            all_scores[table]=score
            all_dataframes[table]=df

        displayed=set()

        for category,activities in self.categories.items():
            valid=[(title,table) for title,table in activities if table in all_scores and table not in displayed]

            if not valid:continue

            st.header(category,divider=True)

            for title,table in valid:
                displayed.add(table)
                self.displayTableSection(title,all_dataframes[table],all_scores[table])

        category_scores=self.getCategoryWiseScores(all_scores)
        category_req,activity_req,category_ok,activity_ok,overall_ok,final_score,requirements=self.getRequirementResults(category_scores,all_scores,profile)

        st.header("Category Wise Performance",divider=True)
        summary=pd.DataFrame([{"Category":category,"Total Score Achieved":value["total_score_achieved"],"Score Approved":value["score_approved"],"Score Considered":value["score_considered"],"Maximum Score":value["max_score"]} for category,value in category_scores.items()])
        st.dataframe(summary,use_container_width=True,hide_index=True)

        st.header("Minimum Requirement",divider=True)
        st.dataframe(category_req,use_container_width=True,hide_index=True)

        if not activity_req.empty:
            st.subheader("Activity Wise Mandatory Minimums")
            st.dataframe(activity_req,use_container_width=True,hide_index=True)

        if not requirements["recognized"]:st.warning("Faculty designation is not mapped to a minimum-requirement rule.")

        total_achieved=sum(value["total_score_achieved"] for value in category_scores.values())
        total_approved=sum(value["score_approved"] for value in category_scores.values())

        col1,col2,col3,col4=st.columns(4)
        col1.metric("Total Score Achieved",f"{total_achieved:.2f}")
        col2.metric("Score Approved",f"{total_approved:.2f}")
        col3.metric("Final Score",f"{final_score:.2f} / 100")
        col4.metric("Performance",f"{final_score:.2f}%")
        style_metric_cards()

        if overall_ok:st.success("Minimum Requirements Satisfied.")
        else:st.error("Minimum Requirements Not Satisfied.")

        chart=pd.DataFrame([{"Category":category,"Total Score Achieved":value["total_score_achieved"],"Score Approved":value["score_approved"],"Score Considered":value["score_considered"],"Maximum":value["max_score"]} for category,value in category_scores.items()]).set_index("Category")

        st.subheader("Category Performance Chart",divider=True)
        st.bar_chart(chart,use_container_width=True)

        st.subheader("Download Faculty Profile",divider=True)
        pdf=self.convert_to_pdf(all_scores=all_scores,all_dataframes=all_dataframes,faculty_image=image,faculty_profile=profile)
        self.download_pdf(pdf,faculty_id)

    def main_layout(self):
        col1,col2=st.columns([1,3],border=True,gap="small")

        with col1:
            st.subheader("Faculty Profile")
            selected_department=st.pills("Select Department",department,selection_mode="single",key="profile_department")

            if not selected_department:
                st.info("Please Select A Department.")
                return

            faculty_df=self.getFacultyList(selected_department)

            if faculty_df.empty:
                st.warning("No Faculty Members Present.")
                return

            options={f"{row['faculty_id']} - {row['faculty_name']}":(str(row["faculty_id"]),str(row["faculty_name"])) for _,row in faculty_df.iterrows()}
            selected=st.selectbox("Select Faculty",list(options),index=None,key="profile_faculty")
            proceed=st.toggle("Proceed To View",key="profile_proceed")

        with col2:
            if not proceed:return

            if not selected:
                st.warning("Please Select A Faculty.")
                return

            faculty_id,faculty_name=options[selected]
            self.renderFaculty(selected_department,faculty_id,faculty_name)