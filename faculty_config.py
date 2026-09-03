from streamlit_option_menu import option_menu

academic_activities=[
    "Academic Results",
    "Students Feedback",
    "HoD Feedback",
    "Project Guidence",
    "Innovations In Teaching Learning",
    "OBE Practice",
    "Product Development By Student",
    "Student Participation And Winning In Seminar, Workshop, Symposium, Conference, etc",
    "Student Participation & Wining in project Competition & MNC Contest",
    "Language Certification Courses",
    "Online Certification (min 1 week) courses",
    "Internship & In-plant Training (minimum 15 days)",
    "Special Awards from Institute and Industry",
    "Students Involvement in ENterpreneurship & Start-ups",
    "Competitive Examinations",
    "Placement",
    "Examination Results",
    "Achievement of ICT and Skill Rack Target",
    "Hacker Rank/Hacker Earth"
]

research_and_development=[
    "Publication -Journals, Conferences & Book chapters",
    "Patents & Copyrights",
    "Consultancy, Funding & Grants",
    "Citation Impact Of Published Work",
    "Ph.D Guidance",
    "Book Publication"
]

academic_extensions=[
    "Arranging On Campus Recruitment",
    "Guest Lectures Delivered (Per Day)",
    "Online certification (min 4 week)",
    "Online Lecture Series / MOOC Course Developed",
    "News Letter & Magazine (like electronics for you, etc.,)",
    "Events Participations (NIRF Ranked Institutes Only)",
    "Special Awards and Fellowship from Recognized Professional Bodies (During Assesment year)",
    "Faculty Exchange (Min 1 week)",
    "Extension Activities Organized",
    "Alumni Networking",
    "Collaboration With Industry/Institute",
    "Value Added Courses Conducted/Organized",
    "Organizing International Conference Partnered with IEEE, Springer, ELsevier to be indexed in Scopus with ISBN",
    "Event Organized (in collaboration with professional societies and accreditation/approval bodies or industry",
    "Memberships"
]

academic_activities_icons=[
    "bar-chart-fill",
    "people-fill",
    "person-check-fill",
    "journal-text",
    "lightbulb-fill",
    "clipboard-check-fill",
    "box-fill",
    "trophy-fill",
    "award-fill",
    "translate",
    "laptop-fill",
    "building-fill",
    "star-fill",
    "rocket-takeoff-fill",
    "book-fill",
    "briefcase-fill",
    "clipboard-data-fill",
    "bullseye",
    "code-slash"
]

research_and_development_icons=[
    "journal-bookmark-fill",
    "file-earmark-text-fill",
    "cash-stack",
    "graph-up-arrow",
    "mortarboard-fill",
    "book-half"
]

academic_extensions_icons=[
    "person-workspace",
    "mic-fill",
    "laptop-fill",
    "collection-play-fill",
    "newspaper",
    "calendar-event-fill",
    "award-fill",
    "arrow-left-right",
    "people-fill",
    "person-hearts",
    "building-fill",
    "book-half",
    "globe2",
    "calendar-check-fill",
    "person-vcard-fill"
]

def display_option_menu(pill,options,icons):
    return option_menu(pill,options,icons=icons,menu_icon="list-task",default_index=0,orientation="vertical",key=f"{pill}_option_menu")

categories={
    "Academic Activities":academic_activities,
    "Research And Development":research_and_development,
    "Academic Extensions":academic_extensions
}