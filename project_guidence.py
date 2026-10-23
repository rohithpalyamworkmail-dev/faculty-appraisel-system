import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase
from database import get_rows
from global_fields import batches as GLOBAL_BATCHES


class projectGuidance:
    def __init__(self):
        self.db = ActivityDatabase("project_guidence")

    def createTable(self):
        return True

    def getStudents(self, selected_batches=None):
        """
        Return students in the logged-in faculty's department, optionally
        filtered by the selected batches. This intentionally does not use
        mentees_list, because project guidance can include any student.
        """
        department = st.session_state.get("department")
        if not department:
            return []

        try:
            rows = get_rows(
                "students",
                {"department": department},
                "student_roll_number,stuent_batch"
            )

            if not rows:
                return []

            students_df = pd.DataFrame(rows)

            # Support the actual schema spelling and common dataframe spelling.
            batch_column = (
                "stuent_batch"
                if "stuent_batch" in students_df.columns
                else "student_batch"
                if "student_batch" in students_df.columns
                else None
            )
            if batch_column is None or "student_roll_number" not in students_df.columns:
                st.error(
                    "Could not find the expected student batch/roll-number "
                    "columns in the students table."
                )
                return []

            if selected_batches:
                selected = {str(batch).strip() for batch in selected_batches}
                students_df = students_df[
                    students_df[batch_column].astype(str).str.strip().isin(selected)
                ]
            else:
                return []

            return (
                students_df["student_roll_number"]
                .dropna()
                .astype(str)
                .str.strip()
                .loc[lambda s: s.ne("")]
                .drop_duplicates()
                .tolist()
            )
        except Exception as e:
            st.error(f"Student Loading Error: {e}")
            return []

    def checkDocument(
        self,
        batches,
        student_roll_numbers,
        project_title,
        is_conference,
        is_journal,
        is_patent,
        paper_proof,
        scopus_proof,
        is_published,
        is_granted,
        proof_certificate_url
    ):
        try:
            filters = {
                "batches": batches,
                "student_roll_numbers": student_roll_numbers,
                "project_title": project_title,
                "is_conference": is_conference,
                "is_journal": is_journal,
                "is_patent": is_patent,
                "paper_proof": paper_proof,
                "scopus_proof": scopus_proof,
                "is_published": is_published,
                "is_granted": is_granted,
                "proof_certificate_url": proof_certificate_url
            }

            return self.db.exists(filters)

        except Exception as e:
            st.error(f"Record Check Error: {e}")
            return False

    def insertDocuments(self, df):
        df = df.copy()
        df["credits"] = 2
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def normalizeRow(self, row):
        if row["is_conference"] == "yes":
            row["is_journal"] = "no"
            row["is_patent"] = "no"
            row["is_published"] = "none"
            row["is_granted"] = "none"
            row["proof_certificate_url"] = "none"

        elif row["is_journal"] == "yes":
            row["is_conference"] = "no"
            row["is_patent"] = "no"
            row["is_published"] = "none"
            row["is_granted"] = "none"
            row["proof_certificate_url"] = "none"

        elif row["is_patent"] == "yes":
            row["is_conference"] = "no"
            row["is_journal"] = "no"
            row["paper_proof"] = "none"
            row["scopus_proof"] = "none"

            if row["is_published"] == "yes":
                row["is_granted"] = "no"
            elif row["is_granted"] == "yes":
                row["is_published"] = "no"

        row["credits"] = 2
        return row

    def edit_document(self):
        try:
            columns = (
                "batches,student_roll_numbers,project_title,is_conference,"
                "is_journal,is_patent,paper_proof,scopus_proof,is_published,"
                "is_granted,proof_certificate_url,credits"
            )

            df = self.db.editable_dataframe(columns)

            if df.empty:
                st.info(
                    "No Project Guidance entries are available for editing."
                )
                return

            # Use the centrally configured batch options from global_fields.py.
            all_batches = [str(batch) for batch in GLOBAL_BATCHES]
            all_students = self.getStudents(all_batches)

            df["batches"] = (
                df["batches"]
                .fillna("")
                .apply(
                    lambda x: [
                        i.strip()
                        for i in str(x).split(",")
                        if i.strip()
                    ]
                )
            )

            df["student_roll_numbers"] = (
                df["student_roll_numbers"]
                .fillna("")
                .apply(
                    lambda x: [
                        i.strip()
                        for i in str(x).split(",")
                        if i.strip()
                    ]
                )
            )

            df["credits"] = 2

            config = {
                "batches": st.column_config.MultiselectColumn(
                    "Batches",
                    options=all_batches,
                    required=True
                ),
                "student_roll_numbers": st.column_config.MultiselectColumn(
                    "Student Roll Numbers",
                    options=all_students,
                    required=True
                ),
                "project_title": st.column_config.TextColumn(
                    "Project Title",
                    required=True
                ),
                "is_conference": st.column_config.SelectboxColumn(
                    "Conference",
                    options=["yes", "no"],
                    required=True
                ),
                "is_journal": st.column_config.SelectboxColumn(
                    "Journal",
                    options=["yes", "no"],
                    required=True
                ),
                "is_patent": st.column_config.SelectboxColumn(
                    "Patent",
                    options=["yes", "no"],
                    required=True
                ),
                "paper_proof": st.column_config.TextColumn("Paper Proof"),
                "scopus_proof": st.column_config.TextColumn("Scopus Proof"),
                "is_published": st.column_config.SelectboxColumn(
                    "Published",
                    options=["yes", "no", "none"],
                    required=True
                ),
                "is_granted": st.column_config.SelectboxColumn(
                    "Granted",
                    options=["yes", "no", "none"],
                    required=True
                ),
                "proof_certificate_url": st.column_config.TextColumn(
                    "Patent Certificate URL"
                ),
                "credits": st.column_config.NumberColumn("Credits")
            }

            edited_df = st.data_editor(
                df,
                num_rows="delete",
                use_container_width=True,
                hide_index=True,
                disabled=["credits"],
                column_config=config,
                key="project_guidance_editor"
            )

            if st.toggle("Update", key="project_guidance_update"):
                edited_df = edited_df.apply(self.normalizeRow, axis=1)

                edited_df["batches"] = edited_df["batches"].apply(
                    lambda x: ",".join(x)
                    if isinstance(x, list)
                    else str(x)
                )

                edited_df["student_roll_numbers"] = (
                    edited_df["student_roll_numbers"].apply(
                        lambda x: ",".join(x)
                        if isinstance(x, list)
                        else str(x)
                    )
                )

                edited_df["credits"] = 2

                if self.db.replace_pending(edited_df):
                    st.success(
                        "Project Guidance Entries Updated Successfully."
                    )
                else:
                    st.warning(
                        "Project Guidance Entries Could Not Be Updated."
                    )

        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns = (
                "batches,student_roll_numbers,project_title,is_conference,"
                "is_journal,is_patent,paper_proof,scopus_proof,is_published,"
                "is_granted,proof_certificate_url,credits,hod_approval,"
                "admin_approval"
            )

            df = self.db.dataframe(columns)

            if df.empty:
                st.info("No Project Guidance entries found.")
                return

            st.subheader("Project Guidance")

            for _, row in df.iterrows():
                with st.container(border=True):
                    st.subheader(
                        str(row["project_title"]),
                        divider=True,
                        text_alignment="center"
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Batches:** {row['batches']}")
                        st.write(
                            f"**Student Roll Numbers:** "
                            f"{row['student_roll_numbers']}"
                        )

                        if row["is_conference"] == "yes":
                            st.write("**Project Type:** Conference")
                        elif row["is_journal"] == "yes":
                            st.write("**Project Type:** Journal")
                        elif row["is_patent"] == "yes":
                            st.write("**Project Type:** Patent")

                    with col2:
                        if (
                            row["is_conference"] == "yes"
                            or row["is_journal"] == "yes"
                        ):
                            st.write(f"**Paper Proof:** {row['paper_proof']}")
                            st.write(f"**Scopus Proof:** {row['scopus_proof']}")

                        elif row["is_patent"] == "yes":
                            st.write(f"**Published:** {row['is_published']}")
                            st.write(f"**Granted:** {row['is_granted']}")
                            st.write(
                                f"**Patent Certificate:** "
                                f"{row['proof_certificate_url']}"
                            )

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.write(f"**Credits:** {row['credits']}")

                    with c2:
                        st.write(f"**HoD Approval:** {row['hod_approval']}")

                    with c3:
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
                st.subheader("Project Guidance Entry")

                # Batch pills come from global_fields.py, not the faculty mentee list.
                batch_options = [str(batch) for batch in GLOBAL_BATCHES]

                selected_batches = st.pills(
                    "Select Batches",
                    batch_options,
                    selection_mode="multi",
                    wrap=True,
                    width="stretch",
                    key="project_guidance_batch_pills"
                )

                available_students = self.getStudents(selected_batches)

                selected_students = (
                    st.multiselect(
                        "Select Student Roll Numbers",
                        available_students,
                        key="project_guidance_student_roll_numbers"
                    )
                    if selected_batches
                    else []
                )

                project_title = st.text_input("Enter Project Title")

                project_type = st.radio(
                    "What Type It Is",
                    ["Conference", "Journal", "Patent"],
                    horizontal=True,
                    index=None
                )

                is_conference = "no"
                is_journal = "no"
                is_patent = "no"
                paper_proof = "none"
                scopus_proof = "none"
                is_published = "none"
                is_granted = "none"
                proof_certificate_url = "none"
                patent_status = None

                if project_type == "Conference":
                    is_conference = "yes"
                    paper_proof = st.text_input("Paper Proof URL")
                    scopus_proof = st.text_input("Scopus Proof URL")

                elif project_type == "Journal":
                    is_journal = "yes"
                    paper_proof = st.text_input("Paper Proof URL")
                    scopus_proof = st.text_input("Scopus Proof URL")

                elif project_type == "Patent":
                    is_patent = "yes"

                    patent_status = st.radio(
                        "Is Published Or Granted",
                        ["Published", "Granted"],
                        horizontal=True,
                        index=None
                    )

                    if patent_status == "Published":
                        is_published = "yes"
                        is_granted = "no"

                    elif patent_status == "Granted":
                        is_published = "no"
                        is_granted = "yes"

                    proof_certificate_url = st.text_input(
                        "Patent Certificate URL"
                    )

                # Automatically validate according to project type.
                proceed = all([
                    bool(selected_batches),
                    bool(selected_students),
                    bool(project_title.strip()),
                    bool(project_type)
                ])

                if proceed and project_type in ["Conference", "Journal"]:
                    proceed = all([
                        bool(paper_proof.strip()),
                        bool(scopus_proof.strip())
                    ])

                elif proceed and project_type == "Patent":
                    proceed = all([
                        bool(patent_status),
                        bool(proof_certificate_url.strip())
                    ])

                if not selected_batches:
                    st.warning("Please select at least one Batch.")
                elif not selected_students:
                    st.warning(
                        "Please select at least one Student Roll Number."
                    )
                elif not project_title.strip():
                    st.warning("Please enter Project Title.")
                elif not project_type:
                    st.warning("Please select Project Type.")
                elif (
                    project_type in ["Conference", "Journal"]
                    and not paper_proof.strip()
                ):
                    st.warning("Please enter Paper Proof URL.")
                elif (
                    project_type in ["Conference", "Journal"]
                    and not scopus_proof.strip()
                ):
                    st.warning("Please enter Scopus Proof URL.")
                elif project_type == "Patent" and not patent_status:
                    st.warning(
                        "Please select whether Patent is Published or Granted."
                    )
                elif (
                    project_type == "Patent"
                    and not proof_certificate_url.strip()
                ):
                    st.warning("Please enter Patent Certificate URL.")

            with col2:
                if selected_batches and proceed:
                    batches = ",".join(selected_batches)
                    student_roll_numbers = ",".join(selected_students)
                    credits = 2

                    st.subheader("Project Guidance Details")
                    st.write(f"**Project Title:** {project_title}")
                    st.write(f"**Project Type:** {project_type}")
                    st.write(f"**Batches:** {batches}")
                    st.write(
                        f"**Student Roll Numbers:** {student_roll_numbers}"
                    )
                    st.info(f"Credits: {credits}")

                    if project_type in ["Conference", "Journal"]:
                        st.write(f"**Paper Proof URL:** {paper_proof}")
                        st.write(f"**Scopus Proof URL:** {scopus_proof}")

                    elif project_type == "Patent":
                        st.write(f"**Published:** {is_published}")
                        st.write(f"**Granted:** {is_granted}")
                        st.write(
                            f"**Patent Certificate URL:** "
                            f"{proof_certificate_url}"
                        )

                    if st.button(
                        "Add Entry",
                        key="project_guidance_add",
                        type="secondary",
                        width="stretch"
                    ):
                        exists = self.checkDocument(
                            batches,
                            student_roll_numbers,
                            project_title,
                            is_conference,
                            is_journal,
                            is_patent,
                            paper_proof,
                            scopus_proof,
                            is_published,
                            is_granted,
                            proof_certificate_url
                        )

                        if exists:
                            st.warning("Record Already Exists.")
                        else:
                            df = pd.DataFrame([{
                                "batches": batches,
                                "student_roll_numbers": student_roll_numbers,
                                "project_title": project_title,
                                "is_conference": is_conference,
                                "is_journal": is_journal,
                                "is_patent": is_patent,
                                "paper_proof": paper_proof,
                                "scopus_proof": scopus_proof,
                                "is_published": is_published,
                                "is_granted": is_granted,
                                "proof_certificate_url": proof_certificate_url,
                                "credits": 2
                            }])

                            if self.insertDocuments(df):
                                st.success(
                                    "Project Guidance Added Successfully."
                                )
                            else:
                                st.warning(
                                    "Project Guidance Could Not Be Added."
                                )

        with tab_edit:
            self.edit_document()

        with tab_view:
            self.viewDocuments()
