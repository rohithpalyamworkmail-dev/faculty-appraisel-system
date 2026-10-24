import pandas as pd
import streamlit as st

from activity_database import ActivityDatabase
from database import get_rows
from global_fields import batches as GLOBAL_BATCHES


class studentCompetetionContest:
    def __init__(self):
        self.db = ActivityDatabase("competetion_contest__by_students")

    def calculateCredits(
        self, students, participation_type, result, prize_position
    ):
        count = len(students)

        if participation_type == "National":
            if result == "Prize Winning":
                return count * {
                    1: 3,
                    2: 2,
                    3: 1
                }.get(prize_position, 0)

            return count * 0.2

        if participation_type == "International":
            if result == "Prize Winning":
                return count * {
                    1: 4,
                    2: 3,
                    3: 2
                }.get(prize_position, 0)

            return count * 0.4

        return 0

    def getStudents(self, selected_batches=None):
        """
        Fetch all students from the selected batches in the
        logged-in department. Return only student roll numbers.
        """
        department = st.session_state.get("department")

        if not department or not selected_batches:
            return []

        try:
            students = get_rows(
                "students",
                {"department": department},
                "student_roll_number,stuent_batch"
            )

            if not students:
                return []

            df = pd.DataFrame(students)

            if "stuent_batch" in df.columns:
                batch_column = "stuent_batch"
            elif "student_batch" in df.columns:
                batch_column = "student_batch"
            else:
                st.error(
                    "The students table does not contain "
                    "the expected batch column."
                )
                return []

            if "student_roll_number" not in df.columns:
                st.error(
                    "The students table does not contain "
                    "student_roll_number."
                )
                return []

            selected_batch_values = {
                str(batch).strip()
                for batch in selected_batches
            }

            df = df[
                df[batch_column]
                .astype(str)
                .str.strip()
                .isin(selected_batch_values)
            ]

            return (
                df["student_roll_number"]
                .dropna()
                .astype(str)
                .str.strip()
                .loc[lambda values: values.ne("")]
                .drop_duplicates()
                .tolist()
            )

        except Exception as e:
            st.error(f"Student Loading Error: {e}")
            return []

    def insertDocuments(self, df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns = (
                "name_roll_number,batch,participated_in,result,"
                "participation_type,team_name,proof_url,prize_position,"
                "awarded_credits"
            )

            df = self.db.editable_dataframe(columns)

            if df.empty:
                st.info(
                    "No Competition/Contest entries are available for editing."
                )
                return

            all_batches = [
                str(batch) for batch in GLOBAL_BATCHES
            ]

            # Collect all student roll numbers from all configured batches.
            students = self.getStudents(all_batches)

            df["name_roll_number"] = (
                df["name_roll_number"]
                .fillna("")
                .apply(
                    lambda value: [
                        item.strip()
                        for item in str(value).split(",")
                        if item.strip()
                    ]
                )
            )

            df["prize_position"] = df.apply(
                lambda row: (
                    0
                    if row["result"] == "Participation"
                    else int(row["prize_position"] or 0)
                ),
                axis=1
            )

            config = {
                "name_roll_number": st.column_config.MultiselectColumn(
                    "Student Roll Numbers",
                    options=students,
                    required=True
                ),
                "batch": st.column_config.TextColumn("Batch"),
                "participated_in": st.column_config.SelectboxColumn(
                    "Participated In",
                    options=["competetion", "Contest"],
                    required=True
                ),
                "result": st.column_config.SelectboxColumn(
                    "Result",
                    options=["Participation", "Prize Winning"],
                    required=True
                ),
                "participation_type": st.column_config.SelectboxColumn(
                    "Participation Type",
                    options=["National", "International"],
                    required=True
                ),
                "team_name": st.column_config.TextColumn("Team Name"),
                "proof_url": st.column_config.TextColumn("Proof URL"),
                "prize_position": st.column_config.SelectboxColumn(
                    "Prize Position",
                    options=[0, 1, 2, 3],
                    required=True
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
                key="student_competetion_editor"
            )

            if st.toggle(
                "Update",
                key="student_competetion_update"
            ):
                rows = []

                for _, row in edited_df.iterrows():
                    selected = (
                        row["name_roll_number"]
                        if isinstance(row["name_roll_number"], list)
                        else [
                            value.strip()
                            for value in str(
                                row["name_roll_number"]
                            ).split(",")
                            if value.strip()
                        ]
                    )

                    result = row["result"]

                    position = (
                        0
                        if result == "Participation"
                        else int(row["prize_position"] or 0)
                    )

                    credits = self.calculateCredits(
                        selected,
                        row["participation_type"],
                        result,
                        position
                    )

                    rows.append({
                        "name_roll_number": ",".join(selected),
                        "batch": row["batch"],
                        "participated_in": row["participated_in"],
                        "result": result,
                        "participation_type": row["participation_type"],
                        "team_name": row["team_name"],
                        "proof_url": row["proof_url"],
                        "prize_position": position,
                        "awarded_credits": credits
                    })

                if self.db.replace_pending(pd.DataFrame(rows)):
                    st.success(
                        "Competition/Contest Updated Successfully."
                    )
                else:
                    st.warning("Update Failed.")

        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns = (
                "name_roll_number,batch,participated_in,result,"
                "participation_type,team_name,proof_url,prize_position,"
                "awarded_credits,hod_approval,admin_approval"
            )

            df = self.db.dataframe(columns)

            if df.empty:
                st.info("No Competition/Contest entries found.")
                return

            st.subheader("Student Competition / Contest")

            for _, row in df.iterrows():
                with st.container(border=True):
                    st.subheader(
                        str(row["participated_in"]).title()
                    )

                    st.write(
                        f"**Student Roll Numbers:** "
                        f"{row['name_roll_number']}"
                    )
                    st.write(f"**Batch:** {row['batch']}")
                    st.write(f"**Result:** {row['result']}")

                    st.write(
                        f"**Participation Type:** "
                        f"{row['participation_type']}"
                    )

                    if row["result"] == "Prize Winning":
                        st.write(
                            f"**Prize Position:** {row['prize_position']}"
                        )

                    st.write(f"**Team Name:** {row['team_name']}")
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
                st.subheader("Student Competition / Contest Entry")

                # Use batch values defined centrally in global_fields.py.
                batch_options = [
                    str(batch) for batch in GLOBAL_BATCHES
                ]

                selected_batches = st.pills(
                    "Select Batches",
                    batch_options,
                    selection_mode="multi",
                    wrap=True,
                    key="student_competetion_batch"
                )

                # Fetch every student in the selected batches.
                available_students = self.getStudents(
                    selected_batches
                )

                # Display roll numbers only.
                selected_students = (
                    st.multiselect(
                        "Select Student Roll Numbers",
                        available_students,
                        key="student_competetion_students"
                    )
                    if selected_batches
                    else []
                )

                result = st.pills(
                    "Result",
                    ["Participation", "Prize Winning"],
                    selection_mode="single",
                    wrap=True,
                    key="student_competetion_result"
                )

                prize_position = (
                    st.selectbox(
                        "Prize Position",
                        [1, 2, 3],
                        key="student_competetion_prize_position"
                    )
                    if result == "Prize Winning"
                    else 0
                )

                participated_in = st.pills(
                    "Participated In",
                    ["competetion", "Contest"],
                    selection_mode="single",
                    wrap=True,
                    key="student_competetion_participated_in"
                )

                participation_type = st.pills(
                    "Participation Type",
                    ["National", "International"],
                    selection_mode="single",
                    wrap=True,
                    key="student_competetion_participation_type"
                )

                team_name = st.text_input(
                    "Team Name",
                    key="student_competetion_team_name"
                )

                proof_url = st.text_input(
                    "Proof URL",
                    key="student_competetion_proof_url"
                )

                proceed = all([
                    bool(selected_batches),
                    bool(selected_students),
                    bool(result),
                    bool(participated_in),
                    bool(participation_type),
                    bool(team_name.strip()),
                    bool(proof_url.strip())
                ])

                if not proceed:
                    st.caption(
                        "Complete all required fields to preview "
                        "the competition/contest entry."
                    )

            with col2:
                if selected_batches and proceed:
                    credits = self.calculateCredits(
                        selected_students,
                        participation_type,
                        result,
                        prize_position
                    )

                    st.subheader("Entry Details")

                    st.write(
                        f"**Batches:** {', '.join(selected_batches)}"
                    )
                    st.write(
                        f"**Student Roll Numbers:** "
                        f"{', '.join(selected_students)}"
                    )
                    st.write(
                        f"**Participated In:** {participated_in}"
                    )
                    st.write(f"**Result:** {result}")
                    st.write(
                        f"**Participation Type:** {participation_type}"
                    )

                    if result == "Prize Winning":
                        st.write(
                            f"**Prize Position:** {prize_position}"
                        )

                    st.write(f"**Team Name:** {team_name}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.button(
                        "Add Entry",
                        key="student_competetion_add_entry",
                        type="secondary",
                        width="stretch"
                    ):
                        df = pd.DataFrame([{
                            "name_roll_number": ",".join(
                                selected_students
                            ),
                            "batch": ", ".join(selected_batches),
                            "participated_in": participated_in,
                            "result": result,
                            "participation_type": participation_type,
                            "team_name": team_name.strip(),
                            "proof_url": proof_url.strip(),
                            "prize_position": prize_position,
                            "awarded_credits": credits
                        }])

                        if self.insertDocuments(df):
                            st.success(
                                "Competition/Contest Entry Added Successfully."
                            )
                        else:
                            st.warning(
                                "Competition/Contest Entry Could Not Be Added."
                            )

        with tab_edit:
            self.edit_document()

        with tab_view:
            self.viewDocuments()
