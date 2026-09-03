import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class publicationsJournalsConference:
    def __init__(self):
        self.db=ActivityDatabase("publications_conferences_journals_book_chapters")

    def createTable(self):
        return True

    def calculateCredits(self,publication_type,scopus_indexed,author_type,quartile=None):
        if str(scopus_indexed).lower()!="yes":return 0
        if publication_type=="Journal":
            author_credits={"Q1":7,"Q2":6,"Q3":4,"Q4":3}
            coauthor_credits={"Q1":5,"Q2":4,"Q3":3,"Q4":1.5}
            return author_credits.get(quartile,0) if author_type=="Author" else coauthor_credits.get(quartile,0)
        if publication_type in ["Conference","Book Chapter"]:return 2 if author_type=="Author" else 1
        return 0

    def _value(self,value):
        if value is None:return ""
        try:
            if pd.isna(value):return ""
        except:pass
        return str(value)

    def duplicateEntryCheck(self,publication_type,paper_title,journal_name,name_of_the_conference,chapter_title,doi_link):
        try:
            rows=self.db.rows("publication_type,paper_title,journal_name,name_of_the_conference,chapter_title,doi_link",{"publication_type":publication_type})
            target=[self._value(x) for x in [paper_title,journal_name,name_of_the_conference,chapter_title,doi_link]]
            for row in rows:
                current=[self._value(row.get(x)) for x in ["paper_title","journal_name","name_of_the_conference","chapter_title","doi_link"]]
                if current==target:return True
            return False
        except Exception as e:
            st.error(f"Duplicate Entry Check Error: {e}")
            return False

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            columns="publication_type,paper_title,journal_name,issn_number,scopus_indexed,quartile,impact_factor_or_snip,author_position,author_type,doi_link,paper_proof_url,journal_scopus_proof_url,name_of_the_conference,isbn_number,chapter_title,title_of_the_book,book_level,year_of_publication,chapter_isbn_issn_number,chapter_proof,credits"
            df=self.db.editable_dataframe(columns)

            if df.empty:
                st.info("No Publication entries are available for editing.")
                return

            df["scopus_indexed"]=df["scopus_indexed"].fillna("no").astype(str).str.lower().eq("yes")
            config={"publication_type":st.column_config.SelectboxColumn("Publication Type",options=["Journal","Conference","Book Chapter"],required=True),"paper_title":"Paper Title","journal_name":"Journal Name","issn_number":"ISSN Number","scopus_indexed":st.column_config.CheckboxColumn("Scopus Indexed"),"quartile":st.column_config.SelectboxColumn("Quartile",options=["Q1","Q2","Q3","Q4"]),"impact_factor_or_snip":st.column_config.NumberColumn("Impact Factor / SNIP",min_value=0.0),"author_position":st.column_config.NumberColumn("Author Position",min_value=1,step=1),"author_type":st.column_config.SelectboxColumn("Author Type",options=["Author","Co-Author"],required=True),"doi_link":"DOI Link","paper_proof_url":"Paper Proof URL","journal_scopus_proof_url":"Journal Scopus Proof URL","name_of_the_conference":"Conference Name","isbn_number":"ISBN Number","chapter_title":"Chapter Title","title_of_the_book":"Book Title","book_level":st.column_config.SelectboxColumn("National / International",options=["National","International"]),"year_of_publication":st.column_config.NumberColumn("Publication Year",min_value=1900,step=1),"chapter_isbn_issn_number":"ISBN / ISSN Number","chapter_proof":"Chapter Proof","credits":"Credits"}

            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["credits"],column_config=config,key="publications_editor")

            if st.toggle("Update",key="publications_update"):
                edited_df["scopus_indexed"]=edited_df["scopus_indexed"].apply(lambda x:"yes" if bool(x) else "no")
                edited_df["credits"]=edited_df.apply(lambda r:self.calculateCredits(r["publication_type"],r["scopus_indexed"],r["author_type"],r["quartile"]),axis=1)

                if self.db.replace_pending(edited_df):st.success("Publication Entries Updated Successfully.")
                else:st.warning("Publication Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            columns="publication_type,paper_title,journal_name,issn_number,scopus_indexed,quartile,impact_factor_or_snip,author_position,author_type,doi_link,paper_proof_url,journal_scopus_proof_url,name_of_the_conference,isbn_number,chapter_title,title_of_the_book,book_level,year_of_publication,chapter_isbn_issn_number,chapter_proof,credits,hod_approval,admin_approval"
            df=self.db.dataframe(columns)

            if df.empty:
                st.info("No Publication entries found.")
                return

            st.subheader("Publications - Journals / Conferences / Book Chapters")

            for _,row in df.iterrows():
                title=row["chapter_title"] if row["publication_type"]=="Book Chapter" else row["paper_title"]

                with st.container(border=True):
                    st.subheader(str(title),divider=True,text_alignment="center")
                    st.write(f"**Type:** {row['publication_type']}")
                    st.write(f"**Scopus Indexed:** {str(row['scopus_indexed']).title()}")
                    st.write(f"**Author Type:** {row['author_type']}")
                    st.write(f"**Author Position:** {row['author_position']}")

                    if row["publication_type"]=="Journal":
                        st.write(f"**Journal Name:** {row['journal_name']}")
                        st.write(f"**ISSN Number:** {row['issn_number']}")
                        st.write(f"**Quartile:** {row['quartile']}")
                        st.write(f"**Impact Factor / SNIP:** {row['impact_factor_or_snip']}")
                        st.write(f"**DOI Link:** {row['doi_link']}")
                        st.write(f"**Paper Proof URL:** {row['paper_proof_url']}")
                        st.write(f"**Journal Scopus Proof URL:** {row['journal_scopus_proof_url']}")

                    elif row["publication_type"]=="Conference":
                        st.write(f"**Conference Name:** {row['name_of_the_conference']}")
                        st.write(f"**ISBN Number:** {row['isbn_number']}")
                        st.write(f"**DOI Link:** {row['doi_link']}")
                        st.write(f"**Paper Proof URL:** {row['paper_proof_url']}")

                    elif row["publication_type"]=="Book Chapter":
                        st.write(f"**Book Title:** {row['title_of_the_book']}")
                        st.write(f"**Level:** {row['book_level']}")
                        st.write(f"**Year Of Publication:** {row['year_of_publication']}")
                        st.write(f"**ISBN / ISSN:** {row['chapter_isbn_issn_number']}")
                        st.write(f"**Chapter Proof:** {row['chapter_proof']}")

                    col1,col2,col3=st.columns(3)
                    with col1:st.write(f"**Credits:** {row['credits']}")
                    with col2:st.write(f"**HoD Approval:** {row['hod_approval']}")
                    with col3:st.write(f"**Admin Approval:** {row['admin_approval']}")
        except Exception as e:
            st.error(f"View Error: {e}")

    def main_layout(self):
        tab_entry,tab_edit,tab_view=st.tabs(["Entry","Edit","View"])

        with tab_entry:
            col1,col2=st.columns([1,2],border=True,gap="small")
            proceed=False

            with col1:
                st.subheader("Publication Entry")
                publication_type=st.radio("Select Type",["Journal","Conference","Book Chapter"],horizontal=True,index=None)

                paper_title=None;journal_name=None;issn_number=None;scopus_indexed=False;quartile=None;impact_factor_or_snip=None
                author_position=None;author_type=None;doi_link=None;paper_proof_url=None;journal_scopus_proof_url=None
                name_of_the_conference=None;isbn_number=None;chapter_title=None;title_of_the_book=None;book_level=None
                year_of_publication=None;chapter_isbn_issn_number=None;chapter_proof=None

                if publication_type in ["Journal","Conference"]:paper_title=st.text_input("Paper Title")

                if publication_type=="Journal":
                    journal_name=st.text_input("Journal Name")
                    issn_number=st.number_input("ISSN Number",min_value=0,step=1)
                    scopus_indexed=st.checkbox("Scopus Indexed")
                    quartile=st.segmented_control("Quartile",["Q1","Q2","Q3","Q4"],selection_mode="single")
                    impact_factor_or_snip=st.number_input("Impact Factor Or SNIP",min_value=0.0,step=0.01)
                    author_position=st.number_input("Author Position",min_value=1,step=1)
                    author_type="Author" if st.checkbox("Are You An Author") else "Co-Author"
                    doi_link=st.text_input("DOI Link")
                    paper_proof_url=st.text_input("Paper Proof URL")
                    journal_scopus_proof_url=st.text_input("Journal Scopus Proof URL")

                elif publication_type=="Conference":
                    name_of_the_conference=st.text_input("Name Of The Conference")
                    isbn_number=st.number_input("ISBN Number",min_value=0,step=1)
                    scopus_indexed=st.checkbox("Scopus Indexed")
                    author_position=st.number_input("Author Position",min_value=1,step=1)
                    author_type="Author" if st.checkbox("Are You An Author") else "Co-Author"
                    doi_link=st.text_input("DOI Link")
                    paper_proof_url=st.text_input("Paper Proof URL")

                elif publication_type=="Book Chapter":
                    chapter_title=st.text_input("Chapter Title")
                    title_of_the_book=st.text_input("Title Of The Book")
                    book_level=st.pills("National / International",["National","International"],selection_mode="single")
                    year_of_publication=st.number_input("Year Of Publication",min_value=1900,step=1)
                    chapter_isbn_issn_number=st.text_input("ISBN / ISSN Number")
                    author_position=st.number_input("Author Position",min_value=1,step=1)
                    author_type="Author" if st.checkbox("Are You An Author") else "Co-Author"
                    scopus_indexed=st.checkbox("Scopus Indexed")
                    chapter_proof=st.text_input("Chapter Proof URL")

                if st.toggle("Check",key="publication_check"):
                    if not publication_type:st.warning("Please select Publication Type.")
                    elif publication_type in ["Journal","Conference"] and not paper_title:st.warning("Please enter Paper Title.")
                    elif publication_type=="Journal" and not journal_name:st.warning("Please enter Journal Name.")
                    elif publication_type=="Journal" and scopus_indexed and not quartile:st.warning("Please select Quartile.")
                    elif publication_type=="Journal" and not doi_link:st.warning("Please enter DOI Link.")
                    elif publication_type=="Journal" and not paper_proof_url:st.warning("Please enter Paper Proof URL.")
                    elif publication_type=="Journal" and not journal_scopus_proof_url:st.warning("Please enter Journal Scopus Proof URL.")
                    elif publication_type=="Conference" and not name_of_the_conference:st.warning("Please enter Conference Name.")
                    elif publication_type=="Conference" and not doi_link:st.warning("Please enter DOI Link.")
                    elif publication_type=="Conference" and not paper_proof_url:st.warning("Please enter Paper Proof URL.")
                    elif publication_type=="Book Chapter" and not chapter_title:st.warning("Please enter Chapter Title.")
                    elif publication_type=="Book Chapter" and not title_of_the_book:st.warning("Please enter Book Title.")
                    elif publication_type=="Book Chapter" and not book_level:st.warning("Please select National / International.")
                    elif publication_type=="Book Chapter" and not chapter_isbn_issn_number:st.warning("Please enter ISBN / ISSN Number.")
                    elif publication_type=="Book Chapter" and not chapter_proof:st.warning("Please enter Chapter Proof URL.")
                    else:proceed=True;st.success("Publication details verified.")

            with col2:
                if proceed:
                    scopus_value="yes" if scopus_indexed else "no"
                    credits=self.calculateCredits(publication_type,scopus_value,author_type,quartile)

                    st.subheader("Publication Details")
                    st.write(f"**Publication Type:** {publication_type}")
                    st.write(f"**Scopus Indexed:** {'Yes' if scopus_indexed else 'No'}")
                    st.write(f"**Author Type:** {author_type}")
                    st.write(f"**Author Position:** {author_position}")

                    if publication_type=="Journal":
                        st.write(f"**Paper Title:** {paper_title}")
                        st.write(f"**Journal Name:** {journal_name}")
                        st.write(f"**ISSN Number:** {issn_number}")
                        st.write(f"**Quartile:** {quartile}")
                        st.write(f"**Impact Factor / SNIP:** {impact_factor_or_snip}")

                    elif publication_type=="Conference":
                        st.write(f"**Paper Title:** {paper_title}")
                        st.write(f"**Conference Name:** {name_of_the_conference}")
                        st.write(f"**ISBN Number:** {isbn_number}")

                    elif publication_type=="Book Chapter":
                        st.write(f"**Chapter Title:** {chapter_title}")
                        st.write(f"**Book Title:** {title_of_the_book}")
                        st.write(f"**Level:** {book_level}")
                        st.write(f"**Year:** {year_of_publication}")

                    st.info(f"Credits: {credits}")

                    if st.toggle("Add Entry",key="publication_add"):
                        if self.duplicateEntryCheck(publication_type,paper_title,journal_name,name_of_the_conference,chapter_title,doi_link):
                            st.warning("Record Already Exists.")
                        else:
                            df=pd.DataFrame([{"publication_type":publication_type,"paper_title":paper_title,"journal_name":journal_name,"issn_number":str(issn_number) if issn_number is not None else None,"scopus_indexed":scopus_value,"quartile":quartile,"impact_factor_or_snip":impact_factor_or_snip,"author_position":author_position,"author_type":author_type,"doi_link":doi_link,"paper_proof_url":paper_proof_url,"journal_scopus_proof_url":journal_scopus_proof_url,"name_of_the_conference":name_of_the_conference,"isbn_number":str(isbn_number) if isbn_number is not None else None,"chapter_title":chapter_title,"title_of_the_book":title_of_the_book,"book_level":book_level,"year_of_publication":year_of_publication,"chapter_isbn_issn_number":chapter_isbn_issn_number,"chapter_proof":chapter_proof,"credits":credits}])

                            if self.insertDocuments(df):st.success("Publication Added Successfully.")
                            else:st.warning("Publication Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()