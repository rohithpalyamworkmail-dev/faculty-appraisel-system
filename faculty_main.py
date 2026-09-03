import streamlit as st
import pandas as pd

from global_fields import department
from faculty_config import academic_activities,research_and_development,academic_extensions,academic_activities_icons,research_and_development_icons,academic_extensions_icons,display_option_menu
from faculty_login import facultyLogin

from academic_results import academicResults
from students_feedback import studentsFeedback
from hod_feedback import hodFeedback
from project_guidence import projectGuidance
from innovation_in_teaching import innovationInTeaching
from obe_practice import obePractice
from product_development_by_student import productDevelopmentByStudent
from seminar_workshop_symposium_conference import studentSeminarWorkshopConference
from student_competetion_contest import studentCompetetionContest
from language_certifications import languageCertifications
from online_certifications import onlineCertifications
from internship_inplant_training import internshipsInplantTraining
from special_awards import specialAwards
from student_involvements import studentInvolvement
from competetive_examinations import competetiveExaminations
from placements import placements
from examination_results import examinationResults
from ict_skill import ictSkillRack
from hacker_rank_earth import hackerRankEarth

from publications_journal_conference import publicationsJournalsConference
from patents_copy_rights import patentCopyRights
from consultancy import consultancy
from citations import citationImpacts
from phd_guidence import phdGuidance
from book_publications import bookPublications

from arrange_on_campus_placements import arrangingOnCampusRecruitments
from guest_lectures import guestLectures
from online_certifications_4weeks import onlineCertifications4Weeks
from mooc_courses import moocCourses
from news_letters_and_magazines import newsLettersAndMagazine
from event_participations import eventParticipations
from special_awards_fellowships import specialAwardsFellowships
from faculty_exchange import facultyExchange
from extension_activities import extensionActivities
from allumni_connections_by_faculty import alumni
from collaborations import collaborations
from value_added_courses import valueAddedCourses
from organizing_international_conferences import organizingInternationalConference
from event_organizations import eventsOrganizations
from memberships import memberships

from _settings import settings
from faculty_profiles import viewProfiles

for key,value in {
    "login":False,
    "faculty_name":"",
    "faculty_id":"",
    "hod_approval":"",
    "admin_approval":"",
    "department":"",
    "Faculty Image":None,
    "mentees_list":pd.DataFrame(),
    "handling_subjects":pd.DataFrame()
}.items():
    if key not in st.session_state:st.session_state[key]=value

with st.sidebar:
    pill=st.pills(
        "FACULTY MENU",
        ["Login","Academic Activities","Research And Development","Academic Extensions","Settings","My Profile View"],
        selection_mode="single",
        default="Login",
        width="stretch"
    )

if pill=="Login":
    col1,col2=st.columns([1,2],border=True,gap="small")

    with col1:
        st.subheader("Faculty Login")

        selected_department=st.pills("Select Department",department,key="faculty_login_department")
        faculty_id=st.text_input("Enter Faculty ID",key="faculty_login_id")
        faculty_password=st.text_input("Enter Faculty Password",type="password",key="faculty_login_password")

        if st.toggle("Login",key="faculty_login_toggle"):
            if not selected_department:
                st.error("Please select a department.")

            elif not faculty_id:
                st.error("Please enter Faculty ID.")

            elif not faculty_password:
                st.error("Please enter Faculty Password.")

            else:
                success=facultyLogin().do_login(selected_department,faculty_id,faculty_password)

                if success:
                    st.success("Login Successful")

    with col2:
        if st.session_state["login"]:
            st.subheader("Faculty Details")

            if st.session_state.get("Faculty Image"):
                try:
                    st.image(st.session_state["Faculty Image"],width="stretch",caption=st.session_state["faculty_name"])
                except:
                    st.info("Faculty Image Could Not Be Displayed.")
            else:
                st.info("No Faculty Image Available.")

            details={
                "Faculty Name":st.session_state["faculty_name"],
                "Faculty ID":st.session_state["faculty_id"],
                "Department":st.session_state["department"],
                "HoD Approval":st.session_state["hod_approval"],
                "Admin Approval":st.session_state["admin_approval"]
            }

            st.dataframe(pd.DataFrame([details]),use_container_width=True,hide_index=True)

            st.subheader("Subjects Handled")

            subjects_df=st.session_state.get("handling_subjects",pd.DataFrame())

            if subjects_df.empty:
                st.info("No Subjects Assigned.")
            else:
                st.dataframe(subjects_df,use_container_width=True,hide_index=True)

            st.subheader("Mentees")

            mentees_df=st.session_state.get("mentees_list",pd.DataFrame())

            if mentees_df.empty:
                st.info("No Mentees Assigned.")
            else:
                st.dataframe(mentees_df,use_container_width=True,hide_index=True)

        else:
            st.info("Please login first to view faculty details.")

elif pill=="Academic Activities":
    if not st.session_state["login"]:
        st.info("Please login first to access Academic Activities.")

    else:
        with st.sidebar:
            option_selected=display_option_menu(pill,academic_activities,academic_activities_icons)

        if option_selected=="Academic Results":
            academicResults().main_layout()

        elif option_selected=="Students Feedback":
            studentsFeedback().main_layout()

        elif option_selected=="HoD Feedback":
            hodFeedback().main_layout()

        elif option_selected=="Project Guidence":
            projectGuidance().main_layout()

        elif option_selected=="Innovations In Teaching Learning":
            innovationInTeaching().main_layout()

        elif option_selected=="OBE Practice":
            obePractice().main_layout()

        elif option_selected=="Product Development By Student":
            productDevelopmentByStudent().main_layout()

        elif option_selected=="Student Participation And Winning In Seminar, Workshop, Symposium, Conference, etc":
            studentSeminarWorkshopConference().main_layout()

        elif option_selected=="Student Participation & Wining in project Competition & MNC Contest":
            studentCompetetionContest().main_layout()

        elif option_selected=="Language Certification Courses":
            languageCertifications().main_layout()

        elif option_selected=="Online Certification (min 1 week) courses":
            onlineCertifications().main_layout()

        elif option_selected=="Internship & In-plant Training (minimum 15 days)":
            internshipsInplantTraining().main_layout()

        elif option_selected=="Special Awards from Institute and Industry":
            specialAwards().main_layout()

        elif option_selected=="Students Involvement in ENterpreneurship & Start-ups":
            studentInvolvement().main_layout()

        elif option_selected=="Competitive Examinations":
            competetiveExaminations().main_layout()

        elif option_selected=="Placement":
            placements().main_layout()

        elif option_selected=="Examination Results":
            examinationResults().main_layout()

        elif option_selected=="Achievement of ICT and Skill Rack Target":
            ictSkillRack().main_layout()

        elif option_selected=="Hacker Rank/Hacker Earth":
            hackerRankEarth().main_layout()

elif pill=="Research And Development":
    if not st.session_state["login"]:
        st.info("Please login first to access Research And Development.")

    else:
        with st.sidebar:
            option_selected=display_option_menu(pill,research_and_development,research_and_development_icons)

        if option_selected=="Publication -Journals, Conferences & Book chapters":
            publicationsJournalsConference().main_layout()

        elif option_selected=="Patents & Copyrights":
            patentCopyRights().main_layout()

        elif option_selected=="Consultancy, Funding & Grants":
            consultancy().main_layout()

        elif option_selected=="Citation Impact Of Published Work":
            citationImpacts().main_layout()

        elif option_selected=="Ph.D Guidance":
            phdGuidance().main_layout()

        elif option_selected=="Book Publication":
            bookPublications().main_layout()

elif pill=="Academic Extensions":
    if not st.session_state["login"]:
        st.info("Please login first to access Academic Extensions.")

    else:
        with st.sidebar:
            option_selected=display_option_menu(pill,academic_extensions,academic_extensions_icons)

        if option_selected=="Arranging On Campus Recruitment":
            arrangingOnCampusRecruitments().main_layout()

        elif option_selected=="Guest Lectures Delivered (Per Day)":
            guestLectures().main_layout()

        elif option_selected=="Online certification (min 4 week)":
            onlineCertifications4Weeks().main_layout()

        elif option_selected=="Online Lecture Series / MOOC Course Developed":
            moocCourses().main_layout()

        elif option_selected=="News Letter & Magazine (like electronics for you, etc.,)":
            newsLettersAndMagazine().main_layout()

        elif option_selected=="Events Participations (NIRF Ranked Institutes Only)":
            eventParticipations().main_layout()

        elif option_selected=="Special Awards and Fellowship from Recognized Professional Bodies (During Assesment year)":
            specialAwardsFellowships().main_layout()

        elif option_selected=="Faculty Exchange (Min 1 week)":
            facultyExchange().main_layout()

        elif option_selected=="Extension Activities Organized":
            extensionActivities().main_layout()

        elif option_selected=="Alumni Networking":
            alumni().main_layout()

        elif option_selected=="Collaboration With Industry/Institute":
            collaborations().main_layout()

        elif option_selected=="Value Added Courses Conducted/Organized":
            valueAddedCourses().main_layout()

        elif option_selected=="Organizing International Conference Partnered with IEEE, Springer, ELsevier to be indexed in Scopus with ISBN":
            organizingInternationalConference().main_layout()

        elif option_selected=="Event Organized (in collaboration with professional societies and accreditation/approval bodies or industry":
            eventsOrganizations().main_layout()

        elif option_selected=="Memberships":
            memberships().main_layout()

elif pill=="Settings":
    if not st.session_state["login"]:
        st.info("Please login first to access Settings.")

    else:
        col1,col2=st.columns([1,2],border=True,gap="small")
        settings(col1,col2).main_layout()

elif pill=="My Profile View":
    if not st.session_state["login"]:
        st.info("Please login first to access My Profile View.")

    else:
        viewProfiles().main_layout()