create table if not exists faculty(id bigint generated always as identity primary key,department text not null,faculty_name text,faculty_department text,faculty_id text,faculty_salary integer,faculty_overall_experience integer,faculty_experience_mtiet integer,faculty_password text,faculty_permanent_district text,faculty_permanent_state text,faculty_current_district text,faculty_current_state text,is_controller text,is_hod text,is_principal text,is_admin text,designation text,is_phd_holder text,unique(department,faculty_id));

create table if not exists students(id bigint generated always as identity primary key,department text not null,student_name text,student_age integer,stuent_batch text,student_regulation text,student_adress text,student_district text,student_state text,student_gender text,student_roll_number text not null,student_mentor_id text,unique(department,student_roll_number));

create table if not exists subjects(id bigint generated always as identity primary key,department text not null,subject_name text,subject_code text,subject_semister integer,subject_type text,subject_credits integer,alloted_faculty_ids text,alloted_sections text);

create table if not exists students_academic_details(id bigint generated always as identity primary key,department text not null,student_roll_numner text,student_batch text,student_department text,regulation text,status text);

create table if not exists alumni(id bigint generated always as identity primary key,department text not null,student_roll_number text,student_batch text,student_department text,student_regulation text,unique(department,student_roll_number));

create table if not exists faculty_images(id bigint generated always as identity primary key,department text not null,faculty_image bytea,faculty_id text not null,unique(department,faculty_id));

create table if not exists examination_results_faculty(id bigint generated always as identity primary key,department text not null,faculty_id text,faculty_name text,awarded_credits double precision,academic_year text,quarter text,hod_approval text default 'APPROVED',admin_approval text default 'APPROVED',unique(department,faculty_id,academic_year,quarter));

create table if not exists max_scores_for_fs(id bigint generated always as identity primary key,table_name text not null unique,score integer,min_score_professor integer default 0,min_score_for_non_phd_holders integer default 0);

create index if not exists idx_faculty_department_id on faculty(department,faculty_id);
create index if not exists idx_students_department_roll on students(department,student_roll_number);
create index if not exists idx_students_department_mentor on students(department,student_mentor_id);
create index if not exists idx_students_department_batch on students(department,stuent_batch);
create index if not exists idx_subjects_department_code on subjects(department,subject_code);
create index if not exists idx_academic_details_department_roll on students_academic_details(department,student_roll_numner);
create index if not exists idx_exam_results_department_faculty on examination_results_faculty(department,faculty_id);

alter table faculty enable row level security;
alter table students enable row level security;
alter table subjects enable row level security;
alter table students_academic_details enable row level security;
alter table alumni enable row level security;
alter table faculty_images enable row level security;
alter table examination_results_faculty enable row level security;
alter table max_scores_for_fs enable row level security;