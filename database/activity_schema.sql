create table if not exists academic_results(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,subject_name text,subject_code text,subject_semister integer,subject_sections text,pass_percent double precision,subject_credits integer,awarded_credits integer,hod_approval text,admin_approval text);

create table if not exists feedback(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,subject_name text,subject_semester integer,subject_type text,feed_back_score double precision,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists hod_feedbacks(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,awarded_credits double precision,hod_approval text,admin_approval text,reason text);

create table if not exists project_guidence(id bigint generated always as identity primary key,department text not null,batches text,student_roll_numbers text,project_title text,is_conference text,is_journal text,is_patent text,paper_proof text,scopus_proof text,is_published text,is_granted text,proof_certificate_url text,credits double precision default 2,faculty_id text,faculty_name text,hod_approval text,admin_approval text);

create table if not exists innovation_in_teaching(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,subject_type text,problems_faced text,innovation text,proof_url text,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists obe_practice(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,obe_practice_type text,description text,proof_url text,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists product_development_by_student(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,students_names_roll_numbers text,team_name text,product_name text,product_description text,proof_url text,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists seminar_workshop_conference_symposium_by_students(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,name_roll_number text,batch text,participated_in text,result text,participation_type text,team_name text,proof_url text,prize_position integer,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists competetion_contest__by_students(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,name_roll_number text,batch text,participated_in text,result text,participation_type text,team_name text,proof_url text,prize_position integer,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists language_certifications(id bigint generated always as identity primary key,department text not null,language text,country text,proof_url text,hod_approval text,admin_approval text,awarded_credits double precision,faculty_id text,faculty_name text);

create table if not exists online_certifications(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,certification_name text,certification_type text,certification_company text,description text,awarded_credits double precision,hod_approval text,admin_approval text,duration integer,proof_url text);

create table if not exists internships_inplant_training(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,students_names_roll_numbers text,batch text,company_name text,duration_days integer,stipend_offered integer,proof_url text,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists special_awards(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,award_name text,award_received_from text,issuer_name text,description text,proof_url text,awarded_credits double precision,hod_approval text,admin_approval text);

create table if not exists student_involvements_in_startups(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,batch text,student_name_roll_number text,team_name text,description text,startup_enterpernurship_name text,proof_url text,awarded_credits double precision);

create table if not exists competetive_examinations(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,exam_name text,result text,description text,proof_url text,hod_approval text,admin_approval text,student_name_roll_numbers text,batch text,awarded_credits double precision);

create table if not exists placements(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,company text,package double precision,student_names_roll_numbers text,batch text,proof_url text,description text,awarded_credits double precision);

create table if not exists ict_skill_rack(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,ict_skill_rack_target text,proof_url text,awarded_credits double precision);

create table if not exists coding_data(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,batch text,student_name_roll_number text,platform text,number_of_problems_solved integer,type text,hod_approval text,admin_approval text,credits double precision);

create table if not exists publications_conferences_journals_book_chapters(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,publication_type text,paper_title text,journal_name text,issn_number text,scopus_indexed text,quartile text,impact_factor_or_snip double precision,author_position integer,author_type text,doi_link text,paper_proof_url text,journal_scopus_proof_url text,name_of_the_conference text,isbn_number text,chapter_title text,title_of_the_book text,book_level text,year_of_publication integer,chapter_isbn_issn_number text,chapter_proof text,credits double precision);

create table if not exists patent_copy_rights(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,patent_name text,patent_type text,patent_status text,proof_url text,description text,awarded_credits double precision);

create table if not exists consultancy_funding_grants(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_number text,faculty_name text,hod_approval text,admin_approval text,type text,description text,proof_url text,amount double precision,is_amount_greater_than_10_lakhs text,credits double precision);

create table if not exists citation_impacts(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,paper_name text,number_of_citations integer,proof_url text,description text,awarded_credits double precision);

create table if not exists phd_guidance(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,research_type text,proof_url text,description text,external integer,internal_full_time integer,part_time integer,full_time integer,awarded_credits double precision);

create table if not exists book_publications(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,book_name text,book_category text,publisher_name text,published_year integer,author_type text,proof_url text,description text,awarded_credits double precision);

create table if not exists on_campus_recruitments_by_faculty(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,credits double precision,company_name text,academic_year text,number_of_students_placed integer,highest_package double precision,average_package double precision,approval_of_principal integer,approval_of_placement_cell integer,is_admin_approved text default 'no',proof_url text);

create table if not exists guest_lectures(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,institute_type text,institution_name text,number_of_days integer,topics_covered text,description text,proof_url text,awarded_credits double precision);

create table if not exists online_certifications_4weeks(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,certificate_type text,certificate_name text,duration integer,proof_url text,awarded_credits double precision);

create table if not exists mooc_courses_by_faculty(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,course_name text,duration text,uploaded_in text,proof_url text,description text,awarded_credits double precision);

create table if not exists news_letters_magazines(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,name text,type text,description text,published_in text,proof_url text,awarded_credits double precision);

create table if not exists news_letters_and_magazines(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,type text,name text,description text,proof_url text,credits double precision);

create table if not exists nirf_event_participations(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,event_name text,event_type text,number_of_days integer,description text,proof_url text,awarded_credits double precision);

create table if not exists special_awards_fellowships(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,award_type text,name text,issued_institution text,proof_url text,description text,awarded_credits double precision);

create table if not exists membership(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,membership_name text,duration_in_years double precision,issued_body_name text,academic_year text,description text,proof_url text,awarded_credits double precision);

create table if not exists faculty_exchanges(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,exchange_faculty_name text,designation text,employer text,type text,number_of_days integer,proof_url text,description text,awarded_credits double precision);

create table if not exists extension_activities(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,activity_name text,description text,proof_url text,awarded_credits double precision);

create table if not exists alumini_networking(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,type text,student_name_roll_number text,batch text,semister integer,academic_year_type text,description text,proof_url text,awarded_credits double precision);

create table if not exists alumni_connection_by_faculties(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,type text,batch text,student_name_roll_numbers text,title text,credits double precision,description text,proof_url text,hod_approval text,admin_approval text);

create table if not exists collaborations_industry_institute(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,colloboration_type text,colloboration_name text,description text,proof_url text,funding integer,colloboration_with text,organization_name text,awarded_credits double precision);

create table if not exists value_added_courses(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,course_name text,number_of_days integer,number_of_students integer,type text,description text,proof_url text,awarded_credits double precision);

create table if not exists organizing_international_conference(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,conference_name text,partner text,scopused_in_index integer,description text,proof_url text,awarded_credits double precision);

create table if not exists event_organizations(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,hod_approval text,admin_approval text,event_name text,organized_with text,number_of_days integer,proof_url text,description text,awarded_credits double precision);

create index if not exists idx_academic_results_faculty on academic_results(department,faculty_id);
create index if not exists idx_feedback_faculty on feedback(department,faculty_id);
create index if not exists idx_hod_feedbacks_faculty on hod_feedbacks(department,faculty_id);
create index if not exists idx_project_guidence_faculty on project_guidence(department,faculty_id);
create index if not exists idx_innovation_faculty on innovation_in_teaching(department,faculty_id);
create index if not exists idx_obe_faculty on obe_practice(department,faculty_id);
create index if not exists idx_product_faculty on product_development_by_student(department,faculty_id);
create index if not exists idx_seminar_faculty on seminar_workshop_conference_symposium_by_students(department,faculty_id);
create index if not exists idx_competetion_faculty on competetion_contest__by_students(department,faculty_id);
create index if not exists idx_language_faculty on language_certifications(department,faculty_id);
create index if not exists idx_online_cert_faculty on online_certifications(department,faculty_id);
create index if not exists idx_internship_faculty on internships_inplant_training(department,faculty_id);
create index if not exists idx_special_awards_faculty on special_awards(department,faculty_id);
create index if not exists idx_student_startups_faculty on student_involvements_in_startups(department,faculty_id);
create index if not exists idx_comp_exam_faculty on competetive_examinations(department,faculty_id);
create index if not exists idx_placements_faculty on placements(department,faculty_id);
create index if not exists idx_ict_faculty on ict_skill_rack(department,faculty_id);
create index if not exists idx_coding_faculty on coding_data(department,faculty_id);
create index if not exists idx_publications_faculty on publications_conferences_journals_book_chapters(department,faculty_id);
create index if not exists idx_patents_faculty on patent_copy_rights(department,faculty_id);
create index if not exists idx_consultancy_faculty on consultancy_funding_grants(department,faculty_id);
create index if not exists idx_citations_faculty on citation_impacts(department,faculty_id);
create index if not exists idx_phd_faculty on phd_guidance(department,faculty_id);
create index if not exists idx_books_faculty on book_publications(department,faculty_id);
create index if not exists idx_campus_faculty on on_campus_recruitments_by_faculty(department,faculty_id);
create index if not exists idx_guest_faculty on guest_lectures(department,faculty_id);
create index if not exists idx_online4_faculty on online_certifications_4weeks(department,faculty_id);
create index if not exists idx_mooc_faculty on mooc_courses_by_faculty(department,faculty_id);
create index if not exists idx_news1_faculty on news_letters_magazines(department,faculty_id);
create index if not exists idx_news2_faculty on news_letters_and_magazines(department,faculty_id);
create index if not exists idx_events_faculty on nirf_event_participations(department,faculty_id);
create index if not exists idx_fellowships_faculty on special_awards_fellowships(department,faculty_id);
create index if not exists idx_membership_faculty on membership(department,faculty_id);
create index if not exists idx_exchange_faculty on faculty_exchanges(department,faculty_id);
create index if not exists idx_extension_faculty on extension_activities(department,faculty_id);
create index if not exists idx_alumini_faculty on alumini_networking(department,faculty_id);
create index if not exists idx_alumni_connection_faculty on alumni_connection_by_faculties(department,faculty_id);
create index if not exists idx_collaboration_faculty on collaborations_industry_institute(department,faculty_id);
create index if not exists idx_value_courses_faculty on value_added_courses(department,faculty_id);
create index if not exists idx_conference_faculty on organizing_international_conference(department,faculty_id);
create index if not exists idx_event_org_faculty on event_organizations(department,faculty_id);

alter table academic_results enable row level security;
alter table feedback enable row level security;
alter table hod_feedbacks enable row level security;
alter table project_guidence enable row level security;
alter table innovation_in_teaching enable row level security;
alter table obe_practice enable row level security;
alter table product_development_by_student enable row level security;
alter table seminar_workshop_conference_symposium_by_students enable row level security;
alter table competetion_contest__by_students enable row level security;
alter table language_certifications enable row level security;
alter table online_certifications enable row level security;
alter table internships_inplant_training enable row level security;
alter table special_awards enable row level security;
alter table student_involvements_in_startups enable row level security;
alter table competetive_examinations enable row level security;
alter table placements enable row level security;
alter table ict_skill_rack enable row level security;
alter table coding_data enable row level security;
alter table publications_conferences_journals_book_chapters enable row level security;
alter table patent_copy_rights enable row level security;
alter table consultancy_funding_grants enable row level security;
alter table citation_impacts enable row level security;
alter table phd_guidance enable row level security;
alter table book_publications enable row level security;
alter table on_campus_recruitments_by_faculty enable row level security;
alter table guest_lectures enable row level security;
alter table online_certifications_4weeks enable row level security;
alter table mooc_courses_by_faculty enable row level security;
alter table news_letters_magazines enable row level security;
alter table news_letters_and_magazines enable row level security;
alter table nirf_event_participations enable row level security;
alter table special_awards_fellowships enable row level security;
alter table membership enable row level security;
alter table faculty_exchanges enable row level security;
alter table extension_activities enable row level security;
alter table alumini_networking enable row level security;
alter table alumni_connection_by_faculties enable row level security;
alter table collaborations_industry_institute enable row level security;
alter table value_added_courses enable row level security;
alter table organizing_international_conference enable row level security;
alter table event_organizations enable row level security;