
import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase


class specialAwards:
    def __init__(self):
        self.db = ActivityDatabase("special_awards")

    def insertDocuments(self, df):
        df = df.copy()
        df["awarded_credits"] = 2
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df = self.db.editable_dataframe(
                "award_name,award_received_from,issuer_name,description,proof_url,awarded_credits"
            )

            if df.empty:
                st.info("No Special Award entries are available for editing.")
                return

            config = {
                "award_name": "Award Name",
                "award_received_from": st.column_config.SelectboxColumn(
                    "Award Received From",
                    options=[
                        "Institute",
                        "Company",
                        "Societies",
                        "Organization"
                    ],
                    required=True
                ),
                "issuer_name": "Issuer Name",
                "description": "Description",
                "proof_url": "Proof URL",
                "awarded_credits": "Awarded Credits"
            }

            edited_df = st.data_editor(
                df,
                num_rows="delete",
                use_container_width=True,
                hide_index=True,
                disabled=["awarded_credits"],
                column_config=config,
                key="special_awards_editor"
            )

            if st.toggle("Update", key="special_awards_update"):
                edited_df["awarded_credits"] = 2

                if self.db.replace_pending(edited_df):
                    st.success("Special Awards Updated Successfully.")
                else:
                    st.warning("Special Awards Could Not Be Updated.")

        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df = self.db.dataframe(
                "award_name,award_received_from,issuer_name,description,"
                "proof_url,awarded_credits,hod_approval,admin_approval"
            )

            if df.empty:
                st.info("No Special Awards Found.")
                return

            st.subheader("Special Awards")

            for _, row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["award_name"]))

                    st.write(
                        f"**Award Received From:** {row['award_received_from']}"
                    )
                    st.write(f"**Issuer Name:** {row['issuer_name']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(
                            f"**Awarded Credits:** {row['awarded_credits']}"
                        )

                    with col2:
                        st.write(f"**HoD Approval:** {row['hod_approval']}")

                    with col3:
                        st.write(
                            f"**Admin Approval:** {row['admin_approval']}"
                        )

        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        if st.session_state.pop("special_awards_reset", False):
            st.session_state["special_awards_name"] = ""
            st.session_state["special_awards_received_from"] = None
            st.session_state["special_awards_issuer"] = ""
            st.session_state["special_awards_description"] = ""
            st.session_state["special_awards_proof_url"] = ""
            st.toast("Special Award Added Successfully!", icon="✅")

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
                st.subheader("Special Award Entry")

                award_name = st.text_input(
                    "Award Name",
                    key="special_awards_name"
                )

                award_received_from = st.pills(
                    "Award Received From",
                    [
                        "Institute",
                        "Company",
                        "Societies",
                        "Organization"
                    ],
                    selection_mode="single",
                    wrap=True,
                    key="special_awards_received_from"
                )

                issuer_name = st.text_input(
                    "Issuer Name",
                    key="special_awards_issuer"
                )

                description = st.text_area(
                    "Description",
                    key="special_awards_description"
                )

                proof_url = st.text_input(
                    "Proof URL",
                    key="special_awards_proof_url"
                )

                proceed = all([
                    award_name.strip(),
                    award_received_from,
                    issuer_name.strip(),
                    description.strip(),
                    proof_url.strip()
                ])

                if not proceed:
                    st.caption(
                        "Fill in all required fields to preview the award."
                    )

            with col2:
                if proceed:
                    st.subheader("Award Details")

                    st.write(f"**Award:** {award_name}")
                    st.write(
                        f"**Received From:** {award_received_from}"
                    )
                    st.write(f"**Issuer:** {issuer_name}")
                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")

                    st.info("Awarded Credits: 2")

                    if st.button(
                        "Add Entry",
                        key="special_awards_add",
                        type="secondary",
                        width="stretch"
                    ):
                        df = pd.DataFrame([{
                            "award_name": award_name.strip(),
                            "award_received_from": award_received_from,
                            "issuer_name": issuer_name.strip(),
                            "description": description.strip(),
                            "proof_url": proof_url.strip(),
                            "awarded_credits": 2
                        }])

                        if self.insertDocuments(df):
                            st.session_state["special_awards_reset"] = True
                            st.rerun()
                        else:
                            st.warning(
                                "Special Award Could Not Be Added."
                            )

        with tab_edit:
            self.edit_document()

        with tab_view:
            self.viewDocuments()
