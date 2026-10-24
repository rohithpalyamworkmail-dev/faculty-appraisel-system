import pandas as pd
import streamlit as st

from activity_database import ActivityDatabase
from database import get_rows
from global_fields import batches as GLOBAL_BATCHES


class studentInvolvement:
    def __init__(self):
        self.db = ActivityDatabase(
            "student_involvements_in_startups"
        )

    def calculateCredits(self, students):
        return len(students) * 1.5

    def getStudents(self, selected_batches=None):
        """
        Fetch all student roll numbers from the current department
        and filter them by the selected batch or batches.
        """

        department = (
            st.session_state.get("department")
            or st.session_state.get("faculty_department")
            or st.session_state.get("user_department")
        )

        if not department:
            return []

        try:
            students_df = get_rows(
                "students",
                {"department": department},
                "student_roll_number,stuent_batch"
            )

            if students_df is None:
                return []

            if not isinstance(students_df, pd.DataFrame):
                students_df = pd.DataFrame(students_df)

            if students_df.empty:
                return []

            # Support the legacy batch column spelling and
            # the alternative spelling if present in the schema.
            batch_column = (
                "stuent_batch"
                if "stuent_batch" in students_df.columns
                else "student_batch"
            )

            if batch_column not in students_df.columns:
                return []

            if "student_roll_number" not in students_df.columns:
                return []

            students_df[batch_column] = (
                students_df[batch_column].astype(str).str.strip()
            )

            if selected_batches:
                if isinstance(selected_batches, str):
                    selected_batches = [selected_batches]

                selected_batches = [
                    str(batch).strip()
                    for batch in selected_batches
                    if str(batch).strip()
                ]

                students_df = students_df[
                    students_df[batch_column].isin(selected_batches)
                ]

            roll_numbers = (
                students_df["student_roll_number"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            return sorted(
                roll_numbers[roll_numbers != ""].unique().tolist()
            )

        except Exception as e:
            st.error(f"Error fetching students: {e}")
            return []

    def insertDocuments(self, df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns = (
                "batch,student_name_roll_number,team_name,description,"
                "startup_enterpernurship_name,proof_url,awarded_credits"
            )

            df = self.db.editable_dataframe(columns)

            if df.empty:
                st.info(
                    "No Student Involvement entries are available for editing."
                )
                return

            # Fetch all department students, not just faculty mentees.
            students = self.getStudents()

            df["student_name_roll_number"] = (
                df["student_name_roll_number"]
                .fillna("")
                .apply(
                    lambda x: [
                        item.strip()
                        for item in str(x).split(",")
                        if item.strip()
                    ]
                )
            )

            config = {
                "batch": st.column_config.TextColumn(
                    "Batch"
                ),
                "student_name_roll_number": (
                    st.column_config.MultiselectColumn(
                        "Student Roll Numbers",
                        options=students,
                        required=True
                    )
                ),
                "team_name": st.column_config.TextColumn(
                    "Team Name"
                ),
                "description": st.column_config.TextColumn(
                    "Description"
                ),
                "startup_enterpernurship_name": (
                    st.column_config.TextColumn(
                        "Startup / Entrepreneurship Name"
                    )
                ),
                "proof_url": st.column_config.TextColumn(
                    "Proof URL"
                ),
                "awarded_credits": st.column_config.NumberColumn(
                    "Awarded Credits"
                )
            }

            edited_df = st.data_editor(
                df,
                num_rows="delete",
                use_container_width=True,
                hide_index=True,
                disabled=["batch", "awarded_credits"],
                column_config=config,
                key="student_involvement_editor"
            )

            if st.toggle(
                "Update",
                key="student_involvement_update"
            ):
                rows = []

                for _, row in edited_df.iterrows():
                    selected = (
                        row["student_name_roll_number"]
                        if isinstance(
                            row["student_name_roll_number"], list
                        )
                        else [
                            item.strip()
                            for item in str(
                                row["student_name_roll_number"]
                            ).split(",")
                            if item.strip()
                        ]
                    )

                    rows.append({
                        "batch": row["batch"],
                        "student_name_roll_number": ",".join(selected),
                        "team_name": row["team_name"],
                        "description": row["description"],
                        "startup_enterpernurship_name": (
                            row["startup_enterpernurship_name"]
                        ),
                        "proof_url": row["proof_url"],
                        "awarded_credits": self.calculateCredits(
                            selected
                        )
                    })

                if self.db.replace_pending(pd.DataFrame(rows)):
                    st.success(
                        "Student Involvement Updated Successfully."
                    )
                else:
                    st.warning(
                        "Student Involvement Could Not Be Updated."
                    )

        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns = (
                "batch,student_name_roll_number,team_name,description,"
                "startup_enterpernurship_name,proof_url,awarded_credits,"
                "hod_approval,admin_approval"
            )

            df = self.db.dataframe(columns)

            if df.empty:
                st.info(
                    "No Student Involvement entries found."
                )
                return

            st.subheader(
                "Student Involvement In Startups / Entrepreneurship"
            )

            for _, row in df.iterrows():
                with st.container(border=True):
                    st.subheader(
                        str(row["startup_enterpernurship_name"])
                    )

                    st.write(f"**Batch:** {row['batch']}")

                    st.write(
                        "**Student Roll Numbers:** "
                        f"{row['student_name_roll_number']}"
                    )

                    st.write(f"**Team Name:** {row['team_name']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(
                            f"**Awarded Credits:** "
                            f"{row['awarded_credits']}"
                        )

                    with col2:
                        st.write(
                            f"**HoD Approval:** {row['hod_approval']}"
                        )

                    with col3:
                        st.write(
                            f"**Admin Approval:** {row['admin_approval']}"
                        )

        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        tab_entry, tab_edit, tab_view = st.tabs(
            ["Entry", "Edit", "View"]
        )

        with tab_entry:
            col1, col2 = st.columns(
                [1, 2],
                border=True,
                gap="small"
            )

            with col1:
                st.subheader(
                    "Student Involvement In Startups / Entrepreneurship"
                )

                # Batch options come from global_fields.py.
                batch_options = [
                    str(batch)
                    for batch in GLOBAL_BATCHES
                ]

                selected_batches = st.pills(
                    "Select Batches",
                    batch_options,
                    selection_mode="multi",
                    wrap=True,
                    key="student_involvement_batch"
                )

                # Fetch all students from the selected batches.
                available_students = self.getStudents(
                    selected_batches
                )

                selected_students = (
                    st.multiselect(
                        "Select Student Roll Numbers",
                        available_students,
                        key="student_involvement_students"
                    )
                    if selected_batches
                    else []
                )

                team_name = st.text_input(
                    "Team Name",
                    key="student_involvement_team_name"
                )

                startup_name = st.text_input(
                    "Startup / Entrepreneurship Name",
                    key="student_involvement_startup_name"
                )

                description = st.text_area(
                    "Description",
                    key="student_involvement_description"
                )

                proof_url = st.text_input(
                    "Proof URL",
                    key="student_involvement_proof_url"
                )

                proceed = all([
                    selected_batches,
                    selected_students,
                    team_name.strip(),
                    startup_name.strip(),
                    description.strip(),
                    proof_url.strip()
                ])

                if not proceed:
                    st.caption(
                        "Complete all required fields to preview "
                        "the student involvement entry."
                    )

            with col2:
                if proceed:
                    credits = self.calculateCredits(
                        selected_students
                    )

                    st.subheader("Entry Details")

                    st.write(
                        f"**Batches:** {', '.join(selected_batches)}"
                    )
                    st.write(
                        f"**Startup / Entrepreneurship:** {startup_name}"
                    )
                    st.write(f"**Team Name:** {team_name}")

                    st.write(
                        "**Student Roll Numbers:** "
                        f"{', '.join(selected_students)}"
                    )

                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")

                    st.info(f"Awarded Credits: {credits}")

                    if st.button(
                        "Add Entry",
                        key="student_involvement_add",
                        type="secondary",
                        width="stretch"
                    ):
                        entry_df = pd.DataFrame([{
                            "batch": ", ".join(selected_batches),
                            "student_name_roll_number": ",".join(
                                selected_students
                            ),
                            "team_name": team_name.strip(),
                            "description": description.strip(),
                            "startup_enterpernurship_name": (
                                startup_name.strip()
                            ),
                            "proof_url": proof_url.strip(),
                            "awarded_credits": credits
                        }])

                        if self.insertDocuments(entry_df):
                            st.success(
                                "Student Involvement Added Successfully."
                            )
                        else:
                            st.warning(
                                "Student Involvement Could Not Be Added."
                            )

        with tab_edit:
            self.edit_document()

        with tab_view:
            self.viewDocuments()
