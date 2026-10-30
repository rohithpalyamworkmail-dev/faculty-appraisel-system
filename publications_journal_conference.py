
import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase


class publicationsJournalsConference:
    def __init__(self):
        self.db = ActivityDatabase(
            "publications_conferences_journals_book_chapters"
        )

    def createTable(self):
        return True

    @staticmethod
    def _to_integer_or_none(value, field_name):
        """
        Convert values such as 1900.0 to 1900 before sending them to
        PostgreSQL INTEGER columns. Empty/NaN values become None.
        """
        if value is None:
            return None

        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field_name} must be a whole number. Received: {value!r}"
            )

        if not numeric_value.is_integer():
            raise ValueError(
                f"{field_name} must be a whole number. Received: {value!r}"
            )

        return int(numeric_value)

    def _normalize_integer_columns(self, dataframe):
        """
        Keep integer database columns as Python int/None objects.
        dtype=object prevents Pandas from converting int + None back to float.
        """
        dataframe = dataframe.copy()

        for column in ("author_position", "year_of_publication"):
            if column in dataframe.columns:
                values = [
                    self._to_integer_or_none(value, column)
                    for value in dataframe[column].tolist()
                ]
                dataframe[column] = pd.Series(
                    values,
                    index=dataframe.index,
                    dtype=object
                )

        if "credits" in dataframe.columns:
            values = [
                self._to_integer_or_none(value, "credits")
                for value in dataframe["credits"].tolist()
            ]
            dataframe["credits"] = pd.Series(
                values,
                index=dataframe.index,
                dtype=object
            )

        return dataframe

    def calculateCredits(
        self,
        publication_type,
        scopus_indexed,
        author_type,
        author_position=None,
        quartile=None
    ):
        """
        Credit rules:
        - Not Scopus indexed: 0 credits.
        - Scopus indexed and first author: 2 credits.
        - Scopus indexed and corresponding author: 2 credits.
        - Other Scopus-indexed co-authors: 1 credit.

        The same rule is applied to Journals, Conferences and Book Chapters.
        """
        if str(scopus_indexed).strip().lower() not in ("yes", "true", "1"):
            return 0

        try:
            position = int(author_position) if author_position is not None else 0
        except (TypeError, ValueError):
            position = 0

        if position == 1 or author_type == "Corresponding Author":
            return 2

        return 1

    def getAuthorType(self, author_position, corresponding_author):
        """
        Resolve the value stored in the author_type database column.
        First author takes priority over the corresponding-author checkbox.
        """
        try:
            position = int(author_position)
        except (TypeError, ValueError):
            position = 0

        if position == 1:
            return "Author"

        if bool(corresponding_author):
            return "Corresponding Author"

        return "Co-Author"

    def _value(self, value):
        if value is None:
            return ""

        try:
            if pd.isna(value):
                return ""
        except Exception:
            pass

        return str(value)

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
                self._value(x)
                for x in [
                    paper_title,
                    journal_name,
                    name_of_the_conference,
                    chapter_title,
                    doi_link
                ]
            ]

            for row in rows:
                current = [
                    self._value(row.get(x))
                    for x in [
                        "paper_title",
                        "journal_name",
                        "name_of_the_conference",
                        "chapter_title",
                        "doi_link"
                    ]
                ]

                if current == target:
                    return True

            return False

        except Exception as e:
            st.error(f"Duplicate Entry Check Error: {e}")
            return False

    def insertDocuments(self, df):
        df = self._normalize_integer_columns(df)
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns = (
                "publication_type,paper_title,journal_name,issn_number,"
                "scopus_indexed,quartile,impact_factor_or_snip,"
                "author_position,author_type,doi_link,paper_proof_url,"
                "journal_scopus_proof_url,name_of_the_conference,isbn_number,"
                "chapter_title,title_of_the_book,book_level,"
                "year_of_publication,chapter_isbn_issn_number,chapter_proof,"
                "credits"
            )

            df = self.db.editable_dataframe(columns)

            if df.empty:
                st.info("No Publication entries are available for editing.")
                return

            df["scopus_indexed"] = (
                df["scopus_indexed"]
                .fillna("no")
                .astype(str)
                .str.lower()
                .eq("yes")
            )

            config = {
                "publication_type": st.column_config.SelectboxColumn(
                    "Publication Type",
                    options=["Journal", "Conference", "Book Chapter"],
                    required=True
                ),
                "paper_title": "Paper Title",
                "journal_name": "Journal Name",
                "issn_number": "ISSN Number",
                "scopus_indexed": st.column_config.CheckboxColumn(
                    "Scopus Indexed"
                ),
                "quartile": st.column_config.SelectboxColumn(
                    "Quartile",
                    options=["Q1", "Q2", "Q3", "Q4"]
                ),
                "impact_factor_or_snip": st.column_config.NumberColumn(
                    "Impact Factor / SNIP",
                    min_value=0.0
                ),
                "author_position": st.column_config.NumberColumn(
                    "Author Position",
                    min_value=0,
                    step=1
                ),
                "author_type": st.column_config.SelectboxColumn(
                    "Author Type",
                    options=["Author", "Co-Author", "Corresponding Author"],
                    required=True
                ),
                "doi_link": "DOI Link",
                "paper_proof_url": "Paper Proof URL",
                "journal_scopus_proof_url": "Journal Scopus Proof URL",
                "name_of_the_conference": "Conference Name",
                "isbn_number": "ISBN Number",
                "chapter_title": "Chapter Title",
                "title_of_the_book": "Book Title",
                "book_level": st.column_config.SelectboxColumn(
                    "National / International",
                    options=["National", "International"]
                ),
                "year_of_publication": st.column_config.NumberColumn(
                    "Publication Year",
                    min_value=1900,
                    step=1
                ),
                "chapter_isbn_issn_number": "ISBN / ISSN Number",
                "chapter_proof": "Chapter Proof",
                "credits": "Credits"
            }

            edited_df = st.data_editor(
                df,
                num_rows="delete",
                use_container_width=True,
                hide_index=True,
                disabled=["credits"],
                column_config=config,
                key="publications_editor"
            )

            if st.toggle("Update", key="publications_update"):
                # Convert Pandas float values (e.g. 1900.0) to Python integers
                # before ActivityDatabase sends rows to PostgreSQL.
                edited_df = self._normalize_integer_columns(edited_df)

                # First author always takes priority. For other positions,
                # retain Corresponding Author only when that option is selected.
                edited_df["author_type"] = edited_df.apply(
                    lambda r: self.getAuthorType(
                        r["author_position"],
                        str(r["author_type"]).strip() == "Corresponding Author"
                    ),
                    axis=1
                )

                edited_df["scopus_indexed"] = (
                    edited_df["scopus_indexed"]
                    .apply(lambda x: "yes" if bool(x) else "no")
                )

                edited_df["credits"] = edited_df.apply(
                    lambda r: self.calculateCredits(
                        r["publication_type"],
                        r["scopus_indexed"],
                        r["author_type"],
                        r["author_position"],
                        r["quartile"]
                    ),
                    axis=1
                )

                # Re-normalize after calculation; preserve integer objects.
                edited_df = self._normalize_integer_columns(edited_df)

                if self.db.replace_pending(edited_df):
                    st.success("Publication Entries Updated Successfully.")
                else:
                    st.warning("Publication Entries Could Not Be Updated.")

        except Exception as e:
            st.error(f"Edit Error: {e}")

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
                title = (
                    row["chapter_title"]
                    if row["publication_type"] == "Book Chapter"
                    else row["paper_title"]
                )

                with st.container(border=True):
                    st.subheader(
                        str(title),
                        divider=True,
                        text_alignment="center"
                    )

                    st.write(f"**Type:** {row['publication_type']}")
                    st.write(
                        f"**Scopus Indexed:** "
                        f"{str(row['scopus_indexed']).title()}"
                    )
                    st.write(f"**Author Type:** {row['author_type']}")
                    st.write(f"**Author Position:** {row['author_position']}")

                    if row["publication_type"] == "Journal":
                        st.write(f"**Journal Name:** {row['journal_name']}")
                        st.write(f"**ISSN Number:** {row['issn_number']}")
                        st.write(f"**Quartile:** {row['quartile']}")
                        st.write(
                            f"**Impact Factor / SNIP:** "
                            f"{row['impact_factor_or_snip']}"
                        )
                        st.write(f"**DOI Link:** {row['doi_link']}")
                        st.write(
                            f"**Paper Proof URL:** {row['paper_proof_url']}"
                        )
                        st.write(
                            f"**Journal Scopus Proof URL:** "
                            f"{row['journal_scopus_proof_url']}"
                        )

                    elif row["publication_type"] == "Conference":
                        st.write(
                            f"**Conference Name:** "
                            f"{row['name_of_the_conference']}"
                        )
                        st.write(f"**ISBN Number:** {row['isbn_number']}")
                        st.write(f"**DOI Link:** {row['doi_link']}")
                        st.write(
                            f"**Paper Proof URL:** {row['paper_proof_url']}"
                        )

                    elif row["publication_type"] == "Book Chapter":
                        st.write(f"**Book Title:** {row['title_of_the_book']}")
                        st.write(f"**Level:** {row['book_level']}")
                        st.write(
                            f"**Year Of Publication:** "
                            f"{row['year_of_publication']}"
                        )
                        st.write(
                            f"**ISBN / ISSN:** "
                            f"{row['chapter_isbn_issn_number']}"
                        )
                        st.write(f"**Chapter Proof:** {row['chapter_proof']}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write(f"**Credits:** {row['credits']}")

                    with col2:
                        st.write(f"**HoD Approval:** {row['hod_approval']}")

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
                st.subheader("Publication Entry")

                publication_type = st.radio(
                    "Select Type",
                    ["Journal", "Conference", "Book Chapter"],
                    horizontal=True,
                    index=None
                )

                paper_title = None
                journal_name = None
                issn_number = None
                scopus_indexed = False
                quartile = None
                impact_factor_or_snip = None
                author_position = None
                author_type = None
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

                if publication_type in ["Journal", "Conference"]:
                    paper_title = st.text_input("Paper Title")

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
                        ["Q1", "Q2", "Q3", "Q4"],
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
                    paper_proof_url = st.text_input("Paper Proof URL")
                    journal_scopus_proof_url = st.text_input(
                        "Journal Scopus Proof URL"
                    )

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
                    paper_proof_url = st.text_input("Paper Proof URL")

                elif publication_type == "Book Chapter":
                    chapter_title = st.text_input("Chapter Title")
                    title_of_the_book = st.text_input("Title Of The Book")

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
                        label="ISBN / ISSN Number",
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
                    chapter_proof = st.text_input("Chapter Proof URL")

                # Automatic validation based on publication type.
                proceed = bool(publication_type)

                if publication_type == "Journal":
                    proceed = all([
                        bool(paper_title and paper_title.strip()),
                        bool(journal_name and journal_name.strip()),
                        not scopus_indexed or bool(quartile),
                        bool(doi_link and doi_link.strip()),
                        bool(paper_proof_url and paper_proof_url.strip()),
                        bool(
                            journal_scopus_proof_url
                            and journal_scopus_proof_url.strip()
                        )
                    ])

                elif publication_type == "Conference":
                    proceed = all([
                        bool(paper_title and paper_title.strip()),
                        bool(
                            name_of_the_conference
                            and name_of_the_conference.strip()
                        ),
                        bool(doi_link and doi_link.strip()),
                        bool(paper_proof_url and paper_proof_url.strip())
                    ])

                elif publication_type == "Book Chapter":
                    proceed = all([
                        bool(chapter_title and chapter_title.strip()),
                        bool(title_of_the_book and title_of_the_book.strip()),
                        bool(book_level),
                        bool(chapter_isbn_issn_number and
                             chapter_isbn_issn_number.strip()),
                        bool(chapter_proof and chapter_proof.strip())
                    ])

                if not publication_type:
                    st.warning("Please select Publication Type.")

                elif publication_type == "Journal":
                    if not paper_title or not paper_title.strip():
                        st.warning("Please enter Paper Title.")
                    elif not journal_name or not journal_name.strip():
                        st.warning("Please enter Journal Name.")
                    elif scopus_indexed and not quartile:
                        st.warning("Please select Quartile.")
                    elif not doi_link or not doi_link.strip():
                        st.warning("Please enter DOI Link.")
                    elif not paper_proof_url or not paper_proof_url.strip():
                        st.warning("Please enter Paper Proof URL.")
                    elif (
                        not journal_scopus_proof_url
                        or not journal_scopus_proof_url.strip()
                    ):
                        st.warning("Please enter Journal Scopus Proof URL.")

                elif publication_type == "Conference":
                    if not paper_title or not paper_title.strip():
                        st.warning("Please enter Paper Title.")
                    elif (
                        not name_of_the_conference
                        or not name_of_the_conference.strip()
                    ):
                        st.warning("Please enter Conference Name.")
                    elif not doi_link or not doi_link.strip():
                        st.warning("Please enter DOI Link.")
                    elif not paper_proof_url or not paper_proof_url.strip():
                        st.warning("Please enter Paper Proof URL.")

                elif publication_type == "Book Chapter":
                    if not chapter_title or not chapter_title.strip():
                        st.warning("Please enter Chapter Title.")
                    elif not title_of_the_book or not title_of_the_book.strip():
                        st.warning("Please enter Book Title.")
                    elif not book_level:
                        st.warning("Please select National / International.")
                    elif (
                        not chapter_isbn_issn_number
                        or not chapter_isbn_issn_number.strip()
                    ):
                        st.warning("Please enter ISBN / ISSN Number.")
                    elif not chapter_proof or not chapter_proof.strip():
                        st.warning("Please enter Chapter Proof URL.")

            with col2:
                if proceed:
                    scopus_value = "yes" if scopus_indexed else "no"

                    credits = self.calculateCredits(
                        publication_type,
                        scopus_value,
                        author_type,
                        author_position,
                        quartile
                    )

                    st.subheader("Publication Details")
                    st.write(f"**Publication Type:** {publication_type}")
                    st.write(
                        f"**Scopus Indexed:** "
                        f"{'Yes' if scopus_indexed else 'No'}"
                    )
                    st.write(f"**Author Type:** {author_type}")
                    st.write(f"**Author Position:** {author_position}")

                    if publication_type == "Journal":
                        st.write(f"**Paper Title:** {paper_title}")
                        st.write(f"**Journal Name:** {journal_name}")
                        st.write(f"**ISSN Number:** {issn_number}")
                        st.write(f"**Quartile:** {quartile}")
                        st.write(
                            f"**Impact Factor / SNIP:** "
                            f"{impact_factor_or_snip}"
                        )
                        st.write(f"**DOI Link:** {doi_link}")
                        st.write(f"**Paper Proof URL:** {paper_proof_url}")
                        st.write(
                            f"**Journal Scopus Proof URL:** "
                            f"{journal_scopus_proof_url}"
                        )

                    elif publication_type == "Conference":
                        st.write(f"**Paper Title:** {paper_title}")
                        st.write(
                            f"**Conference Name:** {name_of_the_conference}"
                        )
                        st.write(f"**ISBN Number:** {isbn_number}")
                        st.write(f"**DOI Link:** {doi_link}")
                        st.write(f"**Paper Proof URL:** {paper_proof_url}")

                    elif publication_type == "Book Chapter":
                        st.write(f"**Chapter Title:** {chapter_title}")
                        st.write(f"**Book Title:** {title_of_the_book}")
                        st.write(f"**Level:** {book_level}")
                        st.write(f"**Year:** {year_of_publication}")
                        st.write(
                            f"**ISBN / ISSN Number:** "
                            f"{chapter_isbn_issn_number}"
                        )
                        st.write(f"**Chapter Proof URL:** {chapter_proof}")

                    st.info(f"Credits: {credits}")

                    if st.button(
                        "Add Entry",
                        key="publication_add",
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
                            df = pd.DataFrame([{
                                "publication_type": publication_type,
                                "paper_title": paper_title,
                                "journal_name": journal_name,
                                "issn_number": (
                                    str(issn_number)
                                    if issn_number is not None
                                    else None
                                ),
                                "scopus_indexed": scopus_value,
                                "quartile": quartile,
                                "impact_factor_or_snip": impact_factor_or_snip,
                                "author_position": self._to_integer_or_none(
                                    author_position, "author_position"
                                ),
                                "author_type": author_type,
                                "doi_link": doi_link,
                                "paper_proof_url": paper_proof_url,
                                "journal_scopus_proof_url":
                                    journal_scopus_proof_url,
                                "name_of_the_conference":
                                    name_of_the_conference,
                                "isbn_number": (
                                    str(isbn_number)
                                    if isbn_number is not None
                                    else None
                                ),
                                "chapter_title": chapter_title,
                                "title_of_the_book": title_of_the_book,
                                "book_level": book_level,
                                "year_of_publication": self._to_integer_or_none(
                                    year_of_publication, "year_of_publication"
                                ),
                                "chapter_isbn_issn_number":
                                    chapter_isbn_issn_number,
                                "chapter_proof": chapter_proof,
                                "credits": credits
                            }])

                            if self.insertDocuments(df):
                                st.success("Publication Added Successfully.")
                            else:
                                st.warning(
                                    "Publication Could Not Be Added."
                                )

        with tab_edit:
            self.edit_document()

        with tab_view:
            self.viewDocuments()
