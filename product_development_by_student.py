
import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase
from database import get_rows
from global_fields import batches as GLOBAL_BATCHES


class productDevelopmentByStudent:
    def __init__(self):
        self.db = ActivityDatabase("product_development_by_student")

    def getStudentOptions(self, batch=None):
        department = st.session_state.get("department")

        if not department or not batch:
            return []

        try:
            students = get_rows(
                "students",
                {"department": department},
                "student_name,student_roll_number,stuent_batch"
            )

            if not students:
                return []

            students_df = pd.DataFrame(students)

            if "stuent_batch" in students_df.columns:
                batch_column = "stuent_batch"
            elif "student_batch" in students_df.columns:
                batch_column = "student_batch"
            else:
                st.error("The students table does not contain the expected batch column.")
                return []

            if "student_roll_number" not in students_df.columns:
                st.error("The students table does not contain student_roll_number.")
                return []

            students_df = students_df[
                students_df[batch_column].astype(str).str.strip()
                == str(batch).strip()
            ]

            return (
                students_df["student_roll_number"]
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
        df = df.copy()
        df["awarded_credits"] = 2
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df = self.db.editable_dataframe(
                "students_names_roll_numbers,team_name,product_name,"
                "product_description,proof_url,awarded_credits"
            )

            if df.empty:
                st.info("No Product Development entries are available for editing.")
                return

            all_batches = [str(batch) for batch in GLOBAL_BATCHES]

            students = list(dict.fromkeys(
                roll_number
                for batch in all_batches
                for roll_number in self.getStudentOptions(batch)
            ))

            df["students_names_roll_numbers"] = (
                df["students_names_roll_numbers"]
                .fillna("")
                .apply(lambda value: [
                    item.strip()
                    for item in str(value).split(",")
                    if item.strip()
                ])
            )

            config = {
                "students_names_roll_numbers":
                    st.column_config.MultiselectColumn(
                        "Student Roll Numbers",
                        options=students,
                        required=True
                    ),
                "team_name": st.column_config.TextColumn(
                    "Team Name", required=True
                ),
                "product_name": st.column_config.TextColumn(
                    "Product Name", required=True
                ),
                "product_description": st.column_config.TextColumn(
                    "Product Description", required=True
                ),
                "proof_url": st.column_config.TextColumn(
                    "Proof URL", required=True
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
                disabled=["awarded_credits"],
                column_config=config,
                key="product_development_editor"
            )

            if st.toggle("Update", key="product_development_update"):
                edited_df["students_names_roll_numbers"] = (
                    edited_df["students_names_roll_numbers"].apply(
                        lambda value: ",".join(value)
                        if isinstance(value, list)
                        else str(value)
                    )
                )

                edited_df["awarded_credits"] = 2

                if self.db.replace_pending(edited_df):
                    st.success("Product Development Updated Successfully.")
                else:
                    st.warning("Product Development Could Not Be Updated.")

        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df = self.db.dataframe(
                "students_names_roll_numbers,team_name,product_name,"
                "product_description,proof_url,awarded_credits,"
                "hod_approval,admin_approval"
            )

            if df.empty:
                st.info("No Product Development entries found.")
                return

            st.subheader("Product Development By Students")

            for _, row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["product_name"]))

                    st.write(
                        f"**Student Roll Numbers:** "
                        f"{row['students_names_roll_numbers']}"
                    )

                    st.write(f"**Team Name:** {row['team_name']}")
                    st.write(f"**Product Description:** {row['product_description']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Awarded Credits:** {row['awarded_credits']}")

                    with col2:
                        st.write(f"**HoD Approval:** {row['hod_approval']}")

                    with col3:
                        st.write(f"**Admin Approval:** {row['admin_approval']}")

        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):

        if st.session_state.pop("product_development_reset", False):
            st.session_state["product_development_batch"] = None
            st.session_state["product_development_students"] = []
            st.session_state["product_development_team_name"] = ""
            st.session_state["product_development_product_name"] = ""
            st.session_state["product_development_description"] = ""
            st.session_state["product_development_proof_url"] = ""

            st.toast("Product Development Entry Added Successfully!", icon="✅")

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
                st.subheader("Product Development By Student")

                batch_options = [str(batch) for batch in GLOBAL_BATCHES]

                selected_batch = st.pills(
                    "Select Batch",
                    batch_options,
                    selection_mode="single",
                    wrap=True,
                    key="product_development_batch"
                )

                available_students = self.getStudentOptions(selected_batch)

                selected_students = (
                    st.multiselect(
                        "Select Student Roll Numbers",
                        available_students,
                        key="product_development_students"
                    )
                    if selected_batch
                    else []
                )

                team_name = st.text_input(
                    "Team Name",
                    key="product_development_team_name"
                )

                product_name = st.text_input(
                    "Product Name",
                    key="product_development_product_name"
                )

                product_description = st.text_area(
                    "Product Description",
                    key="product_development_description"
                )

                proof_url = st.text_input(
                    "Proof URL",
                    key="product_development_proof_url"
                )

                proceed = all([
                    bool(selected_batch),
                    bool(selected_students),
                    bool(team_name.strip()),
                    bool(product_name.strip()),
                    bool(product_description.strip()),
                    bool(proof_url.strip())
                ])

                if not selected_batch:
                    st.warning("Please select a Batch.")
                elif not selected_students:
                    st.warning("Please select at least one Student.")
                elif not team_name.strip():
                    st.warning("Please enter the Team Name.")
                elif not product_name.strip():
                    st.warning("Please enter the Product Name.")
                elif not product_description.strip():
                    st.warning("Please enter the Product Description.")
                elif not proof_url.strip():
                    st.warning("Please enter the Proof URL.")

            with col2:
                if selected_batch and proceed:
                    students = ",".join(selected_students)

                    st.subheader("Product Development Details")
                    st.write(f"**Batch:** {selected_batch}")
                    st.write(f"**Student Roll Numbers:** {students}")
                    st.write(f"**Team Name:** {team_name}")
                    st.write(f"**Product Name:** {product_name}")
                    st.write(f"**Product Description:** {product_description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info("Awarded Credits: 2")

                    if st.button(
                        "Add Entry",
                        key="product_development_add_entry",
                        type="secondary",
                        width="stretch"
                    ):
                        df = pd.DataFrame([{
                            "students_names_roll_numbers": students,
                            "team_name": team_name,
                            "product_name": product_name,
                            "product_description": product_description,
                            "proof_url": proof_url,
                            "awarded_credits": 2
                        }])

                        if self.insertDocuments(df):
                            st.session_state["product_development_reset"] = True
                            st.rerun()
                        else:
                            st.warning("Product Development Could Not Be Added.")

        with tab_edit:
            self.edit_document()

        with tab_view:
            self.viewDocuments()
