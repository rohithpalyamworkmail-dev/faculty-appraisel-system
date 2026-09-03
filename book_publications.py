import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class bookPublications:
    def __init__(self):
        self.db=ActivityDatabase("book_publications")

    def calculateCredits(self,book_category,author_type):
        if book_category=="Group1":return 10 if author_type=="Author" else 5
        if book_category=="Group2":return 5 if author_type=="Author" else 3
        if book_category=="Other":return 3 if author_type=="Author" else 2
        return 0

    def insertDocuments(self,df):
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("book_name,book_category,publisher_name,published_year,author_type,proof_url,description,awarded_credits")

            if df.empty:
                st.info("No Book Publication entries are available for editing.")
                return

            config={"book_name":"Book Name","book_category":st.column_config.SelectboxColumn("Book Category",options=["Group1","Group2","Other"],required=True),"publisher_name":"Publisher Name","published_year":st.column_config.NumberColumn("Published Year",min_value=1900,step=1,required=True),"author_type":st.column_config.SelectboxColumn("Author Type",options=["Author","Co-Author"],required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"description":"Description","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["awarded_credits"],column_config=config,key="book_publications_editor")

            if st.toggle("Update",key="book_publications_update"):
                edited_df["published_year"]=edited_df["published_year"].fillna(1900).astype(int)
                edited_df["awarded_credits"]=edited_df.apply(lambda row:self.calculateCredits(row["book_category"],row["author_type"]),axis=1)

                if self.db.replace_pending(edited_df):st.success("Book Publication Entries Updated Successfully.")
                else:st.warning("Book Publication Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("book_name,book_category,publisher_name,published_year,author_type,proof_url,description,awarded_credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Book Publications found.")
                return

            st.subheader("Book Publications")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["book_name"]))
                    st.write(f"**Book Category:** {row['book_category']}")
                    st.write(f"**Publisher Name:** {row['publisher_name']}")
                    st.write(f"**Published Year:** {row['published_year']}")
                    st.write(f"**Author Type:** {row['author_type']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Proof URL:** {row['proof_url']}")

                    col1,col2,col3=st.columns(3)
                    with col1:st.write(f"**Awarded Credits:** {row['awarded_credits']}")
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
                st.subheader("Book Publication Entry")
                book_name=st.text_input("Book Name")
                book_category=st.pills("Book Category",["Group1","Group2","Other"],selection_mode="single")
                publisher_name=st.text_input("Publisher Name")
                published_year=st.number_input("Published Year",min_value=1900,step=1)
                author_type=st.pills("Author Type",["Author","Co-Author"],selection_mode="single")
                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="book_publications_check"):
                    if not book_name:st.warning("Please enter Book Name.")
                    elif not book_category:st.warning("Please select Book Category.")
                    elif not publisher_name:st.warning("Please enter Publisher Name.")
                    elif not published_year:st.warning("Please enter Published Year.")
                    elif not author_type:st.warning("Please select Author Type.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Book publication details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(book_category,author_type)
                    st.subheader("Book Publication Details")
                    st.write(f"**Book Name:** {book_name}")
                    st.write(f"**Book Category:** {book_category}")
                    st.write(f"**Publisher Name:** {publisher_name}")
                    st.write(f"**Published Year:** {published_year}")
                    st.write(f"**Author Type:** {author_type}")
                    st.info(f"Awarded Credits: {credits}")

                    if st.toggle("Add Entry",key="book_publications_add"):
                        df=pd.DataFrame([{"book_name":book_name,"book_category":book_category,"publisher_name":publisher_name,"published_year":int(published_year),"author_type":author_type,"proof_url":proof_url,"description":description,"awarded_credits":credits}])

                        if self.insertDocuments(df):st.success("Book Publication Added Successfully.")
                        else:st.warning("Book Publication Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()