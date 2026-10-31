
import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase


class publicationsJournalsConference:

    TABLE_NAME = "publications_conferences_journals_book_chapters"

    PUBLICATION_TYPES = ["Journal", "Conference", "Book Chapter"]
    AUTHOR_TYPES = ["Author", "Co-Author", "Corresponding Author"]
    QUARTILES = ["Q1", "Q2", "Q3", "Q4"]

    INTEGER_COLUMNS = ("author_position", "year_of_publication")

    EDIT_COLUMNS = [
        "id",
        "publication_type",
        "paper_title",
        "journal_name",
        "issn_number",
        "scopus_indexed",
        "quartile",
        "impact_factor_or_snip",
        "author_position",
        "author_type",
        "doi_link",
        "paper_proof_url",
        "journal_scopus_proof_url",
        "name_of_the_conference",
        "isbn_number",
        "chapter_title",
        "title_of_the_book",
        "book_level",
        "year_of_publication",
        "chapter_isbn_issn_number",
        "chapter_proof",
        "credits",
    ]

    def __init__(self):
        self.db = ActivityDatabase(self.TABLE_NAME)

    def createTable(self):
        return True

    # ==============================================================
    # VALUE CONVERSION AND VALIDATION
    # ==============================================================

    @staticmethod
    def _is_missing(value):
        if value is None:
            return True

        try:
            result = pd.isna(value)
            return bool(result) if not hasattr(result, "__len__") else False
        except (TypeError, ValueError):
            return False

    @classmethod
    def _to_integer_or_none(cls, value, field_name):

        if cls._is_missing(value) or value == "":
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field_name} must be a whole number. "
                f"Received: {value!r}"
            )

        if not number.is_integer():
            raise ValueError(
                f"{field_name} must be a whole number. "
                f"Received: {value!r}"
            )

        return int(number)

    def _normalize_integer_columns(self, dataframe):

        result = dataframe.copy()

        for column in self.INTEGER_COLUMNS:

            if column in result.columns:

                result[column] = pd.Series(
                    [
                        self._to_integer_or_none(value, column)
                        for value in result[column]
                    ],
                    index=result.index,
                    dtype=object
                )

        return result

    @classmethod
    def _db_value(cls, column, value):

        if cls._is_missing(value) or value == "":
            return None

        if column in cls.INTEGER_COLUMNS:
            return cls._to_integer_or_none(value, column)

        if column == "scopus_indexed":

            if isinstance(value, bool):
                return "yes" if value else "no"

            return (
                "yes"
                if str(value).strip().lower()
                in {"yes", "true", "1", "y"}
                else "no"
            )

        return value

    @classmethod
    def _same_value(cls, first, second):

        first_missing = cls._is_missing(first) or first == ""
        second_missing = cls._is_missing(second) or second == ""

        if first_missing or second_missing:
            return first_missing and second_missing

        if isinstance(first, (int, float)) and isinstance(
            second, (int, float)
        ):
            return float(first) == float(second)

        return str(first).strip() == str(second).strip()

    @staticmethod
    def _value(value):

        if value is None:
            return ""

        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            pass

        return str(value).strip()

    # ==============================================================
    # AUTHOR TYPE AND CREDIT CALCULATION
    # ==============================================================

    def getAuthorType(self, author_position, corresponding_author):

        try:
            position = self._to_integer_or_none(
                author_position,
                "author_position"
            )
        except ValueError:
            position = None

        # First author always has priority.
        if position == 1:
            return "Author"

        if bool(corresponding_author):
            return "Corresponding Author"

        return "Co-Author"

    def calculateCredits(
        self,
        publication_type,
        scopus_indexed,
        author_type,
        author_position=None,
        quartile=None
    ):

        is_scopus = (
            str(scopus_indexed).strip().lower()
            in {"yes", "true", "1", "y"}
        )

        if not is_scopus:
            return 0

        try:
            position = self._to_integer_or_none(
                author_position,
                "author_position"
            )
        except ValueError:
            position = None

        if (
            position == 1
            or author_type == "Corresponding Author"
        ):
            return 2

        return 1

    # ==============================================================
    # DUPLICATE ENTRY CHECK
    # ==============================================================

    def duplicateEntryCheck(
        self,
        publication_type,
        paper_title,
        journal_name,
        name_of_the_conference,
        chapter_title,
        doi_link
    ):

        try:

            rows = self.db.rows(
                "publication_type,paper_title,journal_name,"
                "name_of_the_conference,chapter_title,doi_link",
                {"publication_type": publication_type}
            )

            target = [
                self._value(paper_title),
                self._value(journal_name),
                self._value(name_of_the_conference),
                self._value(chapter_title),
                self._value(doi_link)
            ]

            for row in rows:

                current = [
                    self._value(row.get("paper_title")),
                    self._value(row.get("journal_name")),
                    self._value(row.get("name_of_the_conference")),
                    self._value(row.get("chapter_title")),
                    self._value(row.get("doi_link"))
                ]

                if current == target:
                    return True

            return False

        except Exception as e:
            st.error(f"Duplicate Entry Check Error: {e}")
            return False

    # ==============================================================
    # INSERT AND DELETE OPERATIONS
    # ==============================================================

    def insertDocuments(self, dataframe):

        try:
            dataframe = self._normalize_integer_columns(dataframe)
            return self.db.insert(dataframe)

        except Exception as e:
            st.error(f"Publication Insert Error: {e}")
            return False

    def deleteAllRows(self):
        return self.db.delete_pending()

    # ==============================================================
    # EDIT PUBLICATION RECORDS
    # ==============================================================

    def edit_document(self):

        try:

            # Fetch complete pending records, including their database IDs.
            original_rows = self.db.editable_rows("*")

            if not original_rows:
                st.info(
                    "No Publication entries are available for editing."
                )
                return

            original_by_id = {
                str(row["id"]): dict(row)
                for row in original_rows
                if row.get("id") is not None
            }

            if not original_by_id:

                st.error(
                    "The fetched publication records do not contain "
                    "database IDs. Safe editing is not possible."
                )
                return

            # Determine which columns actually exist in the database.
            available_columns = set()

            for row in original_by_id.values():
                available_columns.update(row.keys())

            visible_columns = [
                column
                for column in self.EDIT_COLUMNS
                if column == "id" or column in available_columns
            ]

            df = pd.DataFrame(
                list(original_by_id.values())
            )

            df = df.reindex(columns=visible_columns)

            # Normalize integer columns only.
            # Credits are deliberately excluded because old records
            # may contain fractional values such as 1.5.
            df = self._normalize_integer_columns(df)

            # Convert Scopus values into checkbox-compatible booleans.
            if "scopus_indexed" in df.columns:

                df["scopus_indexed"] = (
                    df["scopus_indexed"]
                    .fillna("no")
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(["yes", "true", "1", "y"])
                )

            # Convert legacy credits to numeric values for the editor.
            if "credits" in df.columns:
                df["credits"] = pd.to_numeric(
                    df["credits"],
                    errors="coerce"
                )

            # ------------------------------------------------------
            # EDITOR CONFIGURATION
            # ------------------------------------------------------

            config = {

                "id": st.column_config.TextColumn(
                    "Record ID",
                    disabled=True
                ),

                "publication_type": st.column_config.SelectboxColumn(
                    "Publication Type",
                    options=self.PUBLICATION_TYPES,
                    required=True
                ),

                "paper_title": st.column_config.TextColumn(
                    "Paper Title"
                ),

                "journal_name": st.column_config.TextColumn(
                    "Journal Name"
                ),

                "issn_number": st.column_config.TextColumn(
                    "ISSN Number"
                ),

                "scopus_indexed": st.column_config.CheckboxColumn(
                    "Scopus Indexed"
                ),

                "quartile": st.column_config.SelectboxColumn(
                    "Quartile",
                    options=self.QUARTILES
                ),

                "impact_factor_or_snip": st.column_config.NumberColumn(
                    "Impact Factor / SNIP",
                    min_value=0.0,
                    step=0.01
                ),

                "author_position": st.column_config.NumberColumn(
                    "Author Position",
                    min_value=0,
                    step=1
                ),

                "author_type": st.column_config.SelectboxColumn(
                    "Author Type",
                    options=self.AUTHOR_TYPES,
                    required=True
                ),

                "doi_link": st.column_config.TextColumn(
                    "DOI Link"
                ),

                "paper_proof_url": st.column_config.TextColumn(
                    "Paper Proof URL"
                ),

                "journal_scopus_proof_url": st.column_config.TextColumn(
                    "Journal Scopus Proof URL"
                ),

                "name_of_the_conference": st.column_config.TextColumn(
                    "Conference Name"
                ),

                "isbn_number": st.column_config.TextColumn(
                    "ISBN Number"
                ),

                "chapter_title": st.column_config.TextColumn(
                    "Chapter Title"
                ),

                "title_of_the_book": st.column_config.TextColumn(
                    "Book Title"
                ),

                "book_level": st.column_config.SelectboxColumn(
                    "National / International",
                    options=["National", "International"]
                ),

                "year_of_publication": st.column_config.NumberColumn(
                    "Publication Year",
                    min_value=1900,
                    step=1
                ),

                "chapter_isbn_issn_number": st.column_config.TextColumn(
                    "ISBN / ISSN Number"
                ),

                "chapter_proof": st.column_config.TextColumn(
                    "Chapter Proof"
                ),

                "credits": st.column_config.NumberColumn(
                    "Credits",
                    disabled=True
                )
            }

            # Avoid passing configuration for missing database columns.
            config = {
                key: value
                for key, value in config.items()
                if key in df.columns
            }

            edited_df = st.data_editor(
                df,
                num_rows="delete",
                use_container_width=True,
                hide_index=True,
                disabled=[
                    column
                    for column in ["id", "credits"]
                    if column in df.columns
                ],
                column_config=config,
                key="publications_editor_v3"
            )

            # ------------------------------------------------------
            # UPDATE BUTTON
            # ------------------------------------------------------

            if not st.button(
                "Update",
                key="publications_update_v3",
                type="primary",
                width="stretch"
            ):
                return

            if "id" not in edited_df.columns:
                st.error("Record ID is missing from the editor.")
                return

            edited_ids = {
                str(value)
                for value in edited_df["id"].tolist()
                if not self._is_missing(value)
            }

            original_ids = set(original_by_id.keys())

            deleted_ids = original_ids - edited_ids

            errors = []
            updated_count = 0
            deleted_count = 0

            # ------------------------------------------------------
            # UPDATE EXISTING RECORDS INDIVIDUALLY
            # ------------------------------------------------------

            for _, edited_row in edited_df.iterrows():

                record_id = str(edited_row.get("id"))

                original = original_by_id.get(record_id)

                if original is None:
                    errors.append(
                        f"Unknown publication record ID: {record_id}"
                    )
                    continue

                values = edited_row.to_dict()

                # Convert author position safely.
                try:

                    position = self._to_integer_or_none(
                        values.get("author_position"),
                        "author_position"
                    )

                except ValueError as e:
                    errors.append(f"Record {record_id}: {e}")
                    continue

                # Determine the corresponding-author selection.
                selected_author_type = str(
                    values.get("author_type") or ""
                ).strip()

                author_type = self.getAuthorType(
                    position,
                    selected_author_type == "Corresponding Author"
                )

                # Normalize Scopus value.
                scopus_value = self._db_value(
                    "scopus_indexed",
                    values.get("scopus_indexed")
                )

                values["author_position"] = position
                values["author_type"] = author_type
                values["scopus_indexed"] = scopus_value

                # Recalculate credits using the current rules.
                new_credits = self.calculateCredits(
                    values.get("publication_type"),
                    scopus_value,
                    author_type,
                    position,
                    values.get("quartile")
                )

                # Build an update dictionary containing only changed fields.
                # Hidden fields are never included.
                update_values = {}

                for column in visible_columns:

                    if column in {"id", "credits"}:
                        continue

                    new_value = self._db_value(
                        column,
                        values.get(column)
                    )

                    old_value = original.get(column)

                    if not self._same_value(old_value, new_value):
                        update_values[column] = new_value

                # Migrate old credit values such as 1.5 to the new
                # credit calculation, even when the user did not edit them.
                if not self._same_value(
                    original.get("credits"),
                    new_credits
                ):
                    update_values["credits"] = new_credits

                # Save only when at least one field has changed.
                if update_values:

                    try:

                        success = self.db.update_by_id(
                            original.get("id"),
                            update_values,
                            approvals=False
                        )

                        if success:
                            updated_count += 1
                        else:
                            errors.append(
                                f"Update failed for record {record_id}."
                            )

                    except Exception as e:
                        errors.append(
                            f"Record {record_id}: {e}"
                        )

            # ------------------------------------------------------
            # DELETE ONLY ROWS REMOVED BY THE USER
            # ------------------------------------------------------

            for record_id in deleted_ids:

                try:

                    success = self.db.delete_by_id(
                        original_by_id[record_id].get("id")
                    )

                    if success:
                        deleted_count += 1
                    else:
                        errors.append(
                            f"Delete failed for record {record_id}."
                        )

                except Exception as e:
                    errors.append(
                        f"Delete {record_id}: {e}"
                    )

            # ------------------------------------------------------
            # UPDATE RESULT
            # ------------------------------------------------------

            if errors:

                st.error(
                    "Some changes could not be completed. "
                    "Successful individual operations may already "
                    "have been saved."
                )

                for message in errors:
                    st.write(f"- {message}")

            else:

                st.success(
                    "Publication entries updated successfully. "
                    f"Updated: {updated_count} | "
                    f"Deleted: {deleted_count}"
                )

                st.rerun()

        except Exception as e:
            st.error(f"Edit Error: {e}")

    # ==============================================================
    # VIEW PUBLICATION RECORDS
    # ==============================================================

    def viewDocuments(self):

        try:

            columns = (
                "publication_type,paper_title,journal_name,issn_number,"
                "scopus_indexed,quartile,impact_factor_or_snip,"
                "author_position,author_type,doi_link,paper_proof_url,"
                "journal_scopus_proof_url,name_of_the_conference,isbn_number,"
                "chapter_title,title_of_the_book,book_level,"
                "year_of_publication,chapter_isbn_issn_number,chapter_proof,"
                "credits,hod_approval,admin_approval"
            )

            df = self.db.dataframe(columns)

            if df.empty:
                st.info("No Publication entries found.")
                return

            st.subheader(
                "Publications - Journals / Conferences / Book Chapters"
            )

            for _, row in df.iterrows():

                publication_type = row.get("publication_type")

                title = (
                    row.get("chapter_title")
                    if publication_type == "Book Chapter"
                    else row.get("paper_title")
                )

                with st.container(border=True):

                    st.subheader(
                        str(title or "Untitled Publication"),
                        divider=True,
                        text_alignment="center"
                    )

                    st.write(f"**Type:** {publication_type}")

                    st.write(
                        "**Scopus Indexed:** "
                        f"{str(row.get('scopus_indexed')).title()}"
                    )

                    st.write(
                        f"**Author Type:** {row.get('author_type')}"
                    )

                    st.write(
                        f"**Author Position:** "
                        f"{row.get('author_position')}"
                    )

                    # JOURNAL DETAILS
                    if publication_type == "Journal":

                        st.write(
                            f"**Journal Name:** {row.get('journal_name')}"
                        )

                        st.write(
                            f"**ISSN Number:** {row.get('issn_number')}"
                        )

                        st.write(
                            f"**Quartile:** {row.get('quartile')}"
                        )

                        st.write(
                            "**Impact Factor / SNIP:** "
                            f"{row.get('impact_factor_or_snip')}"
                        )

                        st.write(
                            f"**DOI Link:** {row.get('doi_link')}"
                        )

                        st.write(
                            "**Paper Proof URL:** "
                            f"{row.get('paper_proof_url')}"
                        )

                        st.write(
                            "**Journal Scopus Proof URL:** "
                            f"{row.get('journal_scopus_proof_url')}"
                        )

                    # CONFERENCE DETAILS
                    elif publication_type == "Conference":

                        st.write(
                            "**Conference Name:** "
                            f"{row.get('name_of_the_conference')}"
                        )

                        st.write(
                            f"**ISBN Number:** {row.get('isbn_number')}"
                        )

                        st.write(
                            f"**DOI Link:** {row.get('doi_link')}"
                        )

                        st.write(
                            "**Paper Proof URL:** "
                            f"{row.get('paper_proof_url')}"
                        )

                    # BOOK CHAPTER DETAILS
                    elif publication_type == "Book Chapter":

                        st.write(
                            f"**Book Title:** {row.get('title_of_the_book')}"
                        )

                        st.write(
                            f"**Level:** {row.get('book_level')}"
                        )

                        st.write(
                            "**Year Of Publication:** "
                            f"{row.get('year_of_publication')}"
                        )

                        st.write(
                            "**ISBN / ISSN:** "
                            f"{row.get('chapter_isbn_issn_number')}"
                        )

                        st.write(
                            f"**Chapter Proof:** {row.get('chapter_proof')}"
                        )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(
                            f"**Credits:** {row.get('credits')}"
                        )

                    with col2:
                        st.write(
                            f"**HoD Approval:** "
                            f"{row.get('hod_approval')}"
                        )

                    with col3:
                        st.write(
                            f"**Admin Approval:** "
                            f"{row.get('admin_approval')}"
                        )

        except Exception as e:
            st.error(f"View Error: {e}")

    # ==============================================================
    # MAIN APPLICATION LAYOUT
    # ==============================================================

    def main_layout(self):

        tab_entry, tab_edit, tab_view = st.tabs(
            ["Entry", "Edit", "View"]
        )

        # ==========================================================
        # ENTRY TAB
        # ==========================================================

        with tab_entry:

            col1, col2 = st.columns(
                [1, 2],
                border=True,
                gap="small"
            )

            with col1:

                st.subheader("Publication Entry")

                publication_type = st.radio(
                    "Select Type",
                    self.PUBLICATION_TYPES,
                    horizontal=True,
                    index=None,
                    key="publication_type_entry"
                )

                # Default values for unused fields.
                paper_title = None
                journal_name = None
                issn_number = None
                scopus_indexed = False
                quartile = None
                impact_factor_or_snip = None
                author_position = 0
                author_type = None
                corresponding_author = False
                doi_link = None
                paper_proof_url = None
                journal_scopus_proof_url = None
                name_of_the_conference = None
                isbn_number = None
                chapter_title = None
                title_of_the_book = None
                book_level = None
                year_of_publication = None
                chapter_isbn_issn_number = None
                chapter_proof = None

                # Paper title for Journal and Conference.
                if publication_type in ["Journal", "Conference"]:
                    paper_title = st.text_input("Paper Title")

                # --------------------------------------------------
                # JOURNAL ENTRY
                # --------------------------------------------------

                if publication_type == "Journal":

                    journal_name = st.text_input("Journal Name")

                    issn_number = st.text_input(
                        "ISSN Number",
                        placeholder="XXXX-XXXX"
                    )

                    author_position = st.number_input(
                        "Author Position",
                        min_value=0,
                        step=1
                    )

                    scopus_indexed = st.checkbox("Scopus Indexed")

                    quartile = st.segmented_control(
                        "Quartile",
                        self.QUARTILES,
                        selection_mode="single"
                    )

                    impact_factor_or_snip = st.number_input(
                        "Impact Factor Or SNIP",
                        min_value=0.0,
                        step=0.01
                    )

                    corresponding_author = st.checkbox(
                        "Are You A Corresponding Author"
                    )

                    author_type = self.getAuthorType(
                        author_position,
                        corresponding_author
                    )

                    doi_link = st.text_input("DOI Link")

                    paper_proof_url = st.text_input(
                        "Paper Proof URL"
                    )

                    journal_scopus_proof_url = st.text_input(
                        "Journal Scopus Proof URL"
                    )

                # --------------------------------------------------
                # CONFERENCE ENTRY
                # --------------------------------------------------

                elif publication_type == "Conference":

                    name_of_the_conference = st.text_input(
                        "Name Of The Conference"
                    )

                    isbn_number = st.text_input(
                        "ISBN Number",
                        placeholder="XXXX-XXXX"
                    )

                    scopus_indexed = st.checkbox("Scopus Indexed")

                    author_position = st.number_input(
                        "Author Position",
                        min_value=0,
                        step=1
                    )

                    corresponding_author = st.checkbox(
                        "Are You A Corresponding Author"
                    )

                    author_type = self.getAuthorType(
                        author_position,
                        corresponding_author
                    )

                    doi_link = st.text_input("DOI Link")

                    paper_proof_url = st.text_input(
                        "Paper Proof URL"
                    )

                # --------------------------------------------------
                # BOOK CHAPTER ENTRY
                # --------------------------------------------------

                elif publication_type == "Book Chapter":

                    chapter_title = st.text_input("Chapter Title")

                    title_of_the_book = st.text_input(
                        "Title Of The Book"
                    )

                    book_level = st.pills(
                        "National / International",
                        ["National", "International"],
                        selection_mode="single",
                        wrap=True
                    )

                    year_of_publication = st.number_input(
                        "Year Of Publication",
                        min_value=1900,
                        step=1
                    )

                    chapter_isbn_issn_number = st.text_input(
                        "ISBN / ISSN Number",
                        placeholder="XXXX-XXXX"
                    )

                    author_position = st.number_input(
                        "Author Position",
                        min_value=0,
                        step=1
                    )

                    corresponding_author = st.checkbox(
                        "Are You A Corresponding Author"
                    )

                    author_type = self.getAuthorType(
                        author_position,
                        corresponding_author
                    )

                    scopus_indexed = st.checkbox("Scopus Indexed")

                    chapter_proof = st.text_input(
                        "Chapter Proof URL"
                    )

                # --------------------------------------------------
                # VALIDATION
                # --------------------------------------------------

                proceed = False
                validation_message = None

                if not publication_type:

                    validation_message = (
                        "Please select Publication Type."
                    )

                elif publication_type == "Journal":

                    if not paper_title.strip():
                        validation_message = "Please enter Paper Title."

                    elif not journal_name.strip():
                        validation_message = "Please enter Journal Name."

                    elif scopus_indexed and not quartile:
                        validation_message = "Please select Quartile."

                    elif not doi_link.strip():
                        validation_message = "Please enter DOI Link."

                    elif not paper_proof_url.strip():
                        validation_message = "Please enter Paper Proof URL."

                    elif not journal_scopus_proof_url.strip():
                        validation_message = (
                            "Please enter Journal Scopus Proof URL."
                        )

                    else:
                        proceed = True

                elif publication_type == "Conference":

                    if not paper_title.strip():
                        validation_message = "Please enter Paper Title."

                    elif not name_of_the_conference.strip():
                        validation_message = (
                            "Please enter Conference Name."
                        )

                    elif not doi_link.strip():
                        validation_message = "Please enter DOI Link."

                    elif not paper_proof_url.strip():
                        validation_message = "Please enter Paper Proof URL."

                    else:
                        proceed = True

                elif publication_type == "Book Chapter":

                    if not chapter_title.strip():
                        validation_message = "Please enter Chapter Title."

                    elif not title_of_the_book.strip():
                        validation_message = "Please enter Book Title."

                    elif not book_level:
                        validation_message = (
                            "Please select National / International."
                        )

                    elif not chapter_isbn_issn_number.strip():
                        validation_message = (
                            "Please enter ISBN / ISSN Number."
                        )

                    elif not chapter_proof.strip():
                        validation_message = (
                            "Please enter Chapter Proof URL."
                        )

                    else:
                        proceed = True

                if validation_message:
                    st.warning(validation_message)

            # ======================================================
            # ENTRY PREVIEW
            # ======================================================

            with col2:

                if proceed:

                    scopus_value = (
                        "yes" if scopus_indexed else "no"
                    )

                    credits = self.calculateCredits(
                        publication_type,
                        scopus_value,
                        author_type,
                        author_position,
                        quartile
                    )

                    st.subheader("Publication Details")

                    st.write(
                        f"**Publication Type:** {publication_type}"
                    )

                    st.write(
                        "**Scopus Indexed:** "
                        f"{'Yes' if scopus_indexed else 'No'}"
                    )

                    st.write(
                        f"**Author Type:** {author_type}"
                    )

                    st.write(
                        f"**Author Position:** {author_position}"
                    )

                    if publication_type == "Journal":

                        st.write(f"**Paper Title:** {paper_title}")
                        st.write(f"**Journal Name:** {journal_name}")
                        st.write(f"**ISSN Number:** {issn_number}")
                        st.write(f"**Quartile:** {quartile}")

                        st.write(
                            "**Impact Factor / SNIP:** "
                            f"{impact_factor_or_snip}"
                        )

                        st.write(f"**DOI Link:** {doi_link}")

                        st.write(
                            f"**Paper Proof URL:** {paper_proof_url}"
                        )

                        st.write(
                            "**Journal Scopus Proof URL:** "
                            f"{journal_scopus_proof_url}"
                        )

                    elif publication_type == "Conference":

                        st.write(f"**Paper Title:** {paper_title}")

                        st.write(
                            "**Conference Name:** "
                            f"{name_of_the_conference}"
                        )

                        st.write(f"**ISBN Number:** {isbn_number}")
                        st.write(f"**DOI Link:** {doi_link}")

                        st.write(
                            f"**Paper Proof URL:** {paper_proof_url}"
                        )

                    elif publication_type == "Book Chapter":

                        st.write(f"**Chapter Title:** {chapter_title}")

                        st.write(
                            f"**Book Title:** {title_of_the_book}"
                        )

                        st.write(f"**Level:** {book_level}")
                        st.write(f"**Year:** {year_of_publication}")

                        st.write(
                            "**ISBN / ISSN Number:** "
                            f"{chapter_isbn_issn_number}"
                        )

                        st.write(
                            f"**Chapter Proof URL:** {chapter_proof}"
                        )

                    st.info(f"Credits: {credits}")

                    # --------------------------------------------------
                    # ADD ENTRY
                    # --------------------------------------------------

                    if st.button(
                        "Add Entry",
                        key="publication_add_v3",
                        type="secondary",
                        width="stretch"
                    ):

                        exists = self.duplicateEntryCheck(
                            publication_type,
                            paper_title,
                            journal_name,
                            name_of_the_conference,
                            chapter_title,
                            doi_link
                        )

                        if exists:

                            st.warning("Record Already Exists.")

                        else:

                            new_record = {

                                "publication_type": publication_type,

                                "paper_title": paper_title,

                                "journal_name": journal_name,

                                "issn_number": issn_number,

                                "scopus_indexed": scopus_value,

                                "quartile": quartile,

                                "impact_factor_or_snip":
                                    impact_factor_or_snip,

                                "author_position":
                                    self._to_integer_or_none(
                                        author_position,
                                        "author_position"
                                    ),

                                "author_type": author_type,

                                "doi_link": doi_link,

                                "paper_proof_url": paper_proof_url,

                                "journal_scopus_proof_url":
                                    journal_scopus_proof_url,

                                "name_of_the_conference":
                                    name_of_the_conference,

                                "isbn_number": isbn_number,

                                "chapter_title": chapter_title,

                                "title_of_the_book": title_of_the_book,

                                "book_level": book_level,

                                "year_of_publication":
                                    self._to_integer_or_none(
                                        year_of_publication,
                                        "year_of_publication"
                                    ),

                                "chapter_isbn_issn_number":
                                    chapter_isbn_issn_number,

                                "chapter_proof": chapter_proof,

                                "credits": credits
                            }

                            new_df = pd.DataFrame([new_record])

                            if self.insertDocuments(new_df):

                                st.success(
                                    "Publication Added Successfully."
                                )

                            else:

                                st.warning(
                                    "Publication Could Not Be Added."
                                )

        # ==========================================================
        # EDIT TAB
        # ==========================================================

        with tab_edit:
            self.edit_document()

        # ==========================================================
        # VIEW TAB
        # ==========================================================

        with tab_view:
            self.viewDocuments()
