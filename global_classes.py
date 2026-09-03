import pandas as pd
import streamlit as st

from database import get_rows,insert_rows,delete_rows
from supabase_client import get_supabase


CORE_TABLES=[
    "subjects",
    "faculty",
    "students",
    "students_academic_details",
    "alumni",
    "faculty_images",
    "examination_results_faculty"
]


ACTIVITY_TABLES=[
    "academic_results",
    "feedback",
    "hod_feedbacks",
    "project_guidence",
    "innovation_in_teaching",
    "obe_practice",
    "product_development_by_student",
    "seminar_workshop_conference_symposium_by_students",
    "competetion_contest__by_students",
    "language_certifications",
    "online_certifications",
    "internships_inplant_training",
    "special_awards",
    "student_involvements_in_startups",
    "competetive_examinations",
    "placements",
    "ict_skill_rack",
    "coding_data",
    "publications_conferences_journals_book_chapters",
    "patent_copy_rights",
    "consultancy_funding_grants",
    "citation_impacts",
    "phd_guidance",
    "book_publications",
    "on_campus_recruitments_by_faculty",
    "guest_lectures",
    "online_certifications_4weeks",
    "mooc_courses_by_faculty",
    "news_letters_and_magazines",
    "nirf_event_participations",
    "special_awards_fellowships",
    "membership",
    "faculty_exchanges",
    "extension_activities",
    "alumni_connection_by_faculties",
    "collaborations_industry_institute",
    "value_added_courses",
    "organizing_international_conference",
    "event_organizations"
]


APPLICATION_TABLES=CORE_TABLES+ACTIVITY_TABLES+[
    "max_scores_for_fs"
]


DEPARTMENT_TABLES=ACTIVITY_TABLES+[
    "examination_results_faculty",
    "faculty_images",
    "students_academic_details",
    "alumni",
    "subjects",
    "students",
    "faculty"
]


LEGACY_COLUMNS={
    "subjects":[
        "subject_name",
        "subject_code",
        "subject_semister",
        "subject_type",
        "subject_credits",
        "alloted_faculty_ids",
        "alloted_sections"
    ],

    "faculty":[
        "faculty_name",
        "faculty_department",
        "faculty_id",
        "faculty_salary",
        "faculty_overall_experience",
        "faculty_experience_mtiet",
        "faculty_password",
        "faculty_permanent_district",
        "faculty_permanent_state",
        "faculty_current_district",
        "faculty_current_state",
        "is_controller",
        "is_hod",
        "is_principal",
        "is_admin",
        "designation",
        "is_phd_holder"
    ],

    "students":[
        "student_name",
        "student_age",
        "stuent_batch",
        "student_regulation",
        "student_adress",
        "student_district",
        "student_state",
        "student_gender",
        "student_roll_number",
        "student_mentor_id"
    ],

    "students_academic_details":[
        "student_roll_numner",
        "student_batch",
        "student_department",
        "regulation",
        "status"
    ],

    "alumni":[
        "student_roll_number",
        "student_batch",
        "student_department",
        "student_regulation"
    ],

    "faculty_images":[
        "faculty_image",
        "faculty_id"
    ],

    "examination_results_faculty":[
        "faculty_id",
        "faculty_name",
        "awarded_credits",
        "academic_year",
        "quarter",
        "hod_approval",
        "admin_approval"
    ]
}


INTEGER_COLUMNS={
    "subjects":[
        "subject_semister"
    ],

    "faculty":[
        "faculty_salary",
        "faculty_overall_experience",
        "faculty_experience_mtiet"
    ],

    "students":[
        "student_age"
    ]
}


NUMERIC_COLUMNS={
    "subjects":[
        "subject_credits"
    ],

    "examination_results_faculty":[
        "awarded_credits"
    ]
}


_SCHEMA_READY=set()


def initialize_all_tables(department_name=None,force=False):
    key=department_name or "__GLOBAL__"

    if key in _SCHEMA_READY and not force:
        return True,{"success":True}

    try:
        response=get_supabase().rpc(
            "initialize_faculty_app_schema",
            {
                "p_department":department_name
            }
        ).execute()

        _SCHEMA_READY.add(key)

        return True,response.data

    except Exception as e:
        st.error(f"Schema Initialization Error: {e}")
        return False,None


def get_or_create_db(db_name,type):
    if not db_name:
        return None

    if type=="create":
        status,_=initialize_all_tables(
            db_name,
            force=True
        )

        return status

    if type=="get":
        status,_=initialize_all_tables(
            db_name
        )

        return db_name if status else None

    return False


def delete_db(db_name):
    if not db_name:
        return "Please Select A Department"

    errors=[]

    for table in DEPARTMENT_TABLES:
        try:
            delete_rows(
                table,
                {
                    "department":db_name
                }
            )

        except Exception as e:
            errors.append(
                f"{table}: {e}"
            )

    try:
        delete_rows(
            "departments_registry",
            {
                "department":db_name
            }
        )

    except Exception as e:
        errors.append(
            f"departments_registry: {e}"
        )

    _SCHEMA_READY.discard(db_name)

    if errors:
        return (
            "Department Data Removal Incomplete: "
            +" | ".join(errors)
        )

    return (
        f"Department {db_name} Data Successfully Removed"
    )


def create_table(connection,table_name,fields):
    try:
        if table_name not in APPLICATION_TABLES:
            return (
                f"Table {table_name} Is Not Present In Application Schema",
                False
            )

        status,_=initialize_all_tables(
            connection
        )

        if not status:
            return (
                "Unable To Initialize Supabase Schema",
                False
            )

        return (
            "Success",
            True
        )

    except Exception as e:
        return (
            str(e),
            False
        )


def _integer_value(value,column):
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except:
        pass

    if isinstance(value,str) and not value.strip():
        return None

    try:
        number=float(value)

        if not number.is_integer():
            raise ValueError

        return int(number)

    except:
        raise ValueError(
            f"Invalid integer value '{value}' in column '{column}'"
        )


def _numeric_value(value,column):
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except:
        pass

    if isinstance(value,str) and not value.strip():
        return None

    try:
        return float(value)

    except:
        raise ValueError(
            f"Invalid numeric value '{value}' in column '{column}'"
        )


def normalize_dataframe(table_name,dataframe):
    df=dataframe.copy()

    if "id" in df.columns:
        df=df.drop(
            columns=["id"]
        )

    if "department" in df.columns:
        df=df.drop(
            columns=["department"]
        )


    for column in INTEGER_COLUMNS.get(
        table_name,
        []
    ):
        if column in df.columns:
            values=[
                _integer_value(
                    value,
                    column
                )
                for value in df[column].tolist()
            ]

            df[column]=pd.Series(
                values,
                index=df.index,
                dtype=object
            )


    for column in NUMERIC_COLUMNS.get(
        table_name,
        []
    ):
        if column in df.columns:
            values=[
                _numeric_value(
                    value,
                    column
                )
                for value in df[column].tolist()
            ]

            df[column]=pd.Series(
                values,
                index=df.index,
                dtype=object
            )


    return (
        df.astype(object)
        .where(pd.notnull(df),None)
    )


def addAllRows(db_name,table_name,dataframe):
    if not db_name or dataframe is None:
        return False

    try:
        if dataframe.empty:
            return True


        status,_=initialize_all_tables(
            db_name
        )

        if not status:
            return False


        df=normalize_dataframe(
            table_name,
            dataframe
        )


        df.insert(
            0,
            "department",
            db_name
        )


        insert_rows(
            table_name,
            df
        )

        return True

    except Exception as e:
        st.error(
            f"Insert Error: {e}"
        )

        return False


def deleteAllRows(db_name,table_name):
    if not db_name:
        return False

    try:
        delete_rows(
            table_name,
            {
                "department":db_name
            }
        )

        return True

    except Exception as e:
        st.error(
            f"Delete Error: {e}"
        )

        return False


def displayRows(db_name,table_name):
    if not db_name:
        return [],[]

    try:
        rows=get_rows(
            table_name,
            {
                "department":db_name
            }
        )


        columns=LEGACY_COLUMNS.get(
            table_name,
            []
        )


        result=[
            tuple(
                row.get(column)
                for column in columns
            )
            for row in rows
        ]


        return columns,result

    except Exception as e:
        st.error(
            f"Display Error: {e}"
        )

        return [],[]


def select_students(db_name,table_name,batch):
    if not db_name or batch is None:
        return [],[]

    try:
        rows=get_rows(
            table_name,
            {
                "department":db_name,
                "stuent_batch":batch
            }
        )


        columns=LEGACY_COLUMNS[
            "students"
        ]


        result=[
            tuple(
                row.get(column)
                for column in columns
            )
            for row in rows
        ]


        return columns,result

    except Exception as e:
        st.error(
            f"Student Fetch Error: {e}"
        )

        return [],[]


def delete_students(db_name,table_name,batch):
    if not db_name or batch is None:
        return False

    try:
        delete_rows(
            table_name,
            {
                "department":db_name,
                "stuent_batch":batch
            }
        )

        return True

    except Exception as e:
        st.error(
            f"Student Delete Error: {e}"
        )

        return False