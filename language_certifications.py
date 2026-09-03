import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class languageCertifications:
    language_country={"English":"United Kingdom","Hindi":"India","Bengali":"Bangladesh","Spanish":"Spain","French":"France","Arabic":"Saudi Arabia","Portuguese":"Portugal","Russian":"Russia","Urdu":"Pakistan","German":"Germany","Japanese":"Japan","Korean":"South Korea","Chinese":"China","Italian":"Italy","Dutch":"Netherlands","Greek":"Greece","Turkish":"Turkey","Persian":"Iran","Hebrew":"Israel","Swedish":"Sweden","Norwegian":"Norway","Danish":"Denmark","Finnish":"Finland","Icelandic":"Iceland","Polish":"Poland","Czech":"Czech Republic","Slovak":"Slovakia","Hungarian":"Hungary","Romanian":"Romania","Bulgarian":"Bulgaria","Serbian":"Serbia","Croatian":"Croatia","Slovenian":"Slovenia","Ukrainian":"Ukraine","Lithuanian":"Lithuania","Latvian":"Latvia","Estonian":"Estonia","Albanian":"Albania","Macedonian":"North Macedonia","Bosnian":"Bosnia and Herzegovina","Malay":"Malaysia","Indonesian":"Indonesia","Thai":"Thailand","Vietnamese":"Vietnam","Filipino":"Philippines","Tamil":"India","Telugu":"India","Kannada":"India","Malayalam":"India","Marathi":"India","Gujarati":"India","Punjabi":"India","Odia":"India","Assamese":"India","Nepali":"Nepal","Sinhala":"Sri Lanka","Burmese":"Myanmar","Khmer":"Cambodia","Lao":"Laos","Mongolian":"Mongolia","Tibetan":"China","Kazakh":"Kazakhstan","Uzbek":"Uzbekistan","Turkmen":"Turkmenistan","Kyrgyz":"Kyrgyzstan","Tajik":"Tajikistan","Azerbaijani":"Azerbaijan","Armenian":"Armenia","Georgian":"Georgia","Swahili":"Kenya","Zulu":"South Africa","Xhosa":"South Africa","Afrikaans":"South Africa","Amharic":"Ethiopia","Somali":"Somalia","Hausa":"Nigeria","Yoruba":"Nigeria","Igbo":"Nigeria","Fula":"Senegal","Wolof":"Senegal","Kinyarwanda":"Rwanda","Kirundi":"Burundi","Malagasy":"Madagascar","Shona":"Zimbabwe","Sesotho":"Lesotho","Setswana":"Botswana","Tsonga":"South Africa","Tswana":"Botswana","Luxembourgish":"Luxembourg","Maltese":"Malta","Irish":"Ireland","Welsh":"United Kingdom","Scottish Gaelic":"United Kingdom","Basque":"Spain","Catalan":"Spain","Galician":"Spain","Esperanto":"International"}

    def __init__(self):
        self.db=ActivityDatabase("language_certifications")

    def insertDocuments(self,df):
        df=df.copy();df["awarded_credits"]=1
        return self.db.insert(df)

    def deleteAllRows(self):
        return self.db.delete_pending()

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("language,country,proof_url,awarded_credits")
            if df.empty:
                st.info("No language certification entries are available for editing.")
                return

            config={"language":st.column_config.SelectboxColumn("Language",options=list(self.language_country.keys()),required=True),"country":"Country","proof_url":"Proof URL","awarded_credits":"Awarded Credits"}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["country","awarded_credits"],column_config=config,key="language_certification_editor")
            edited_df["country"]=edited_df["language"].map(self.language_country)

            if st.toggle("Update",key="language_certification_update"):
                edited_df["awarded_credits"]=1
                if self.db.replace_pending(edited_df):st.success("Language Certifications Updated Successfully.")
                else:st.warning("Language Certifications Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("language,country,proof_url,awarded_credits,hod_approval,admin_approval")
            if df.empty:
                st.info("No language certifications found.")
                return

            st.subheader("Language Certifications")
            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["language"]))
                    st.write(f"**Country:** {row['country']}")
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
                language=st.selectbox("Select Language",list(self.language_country.keys()))
                country=self.language_country.get(language,"")
                st.info(f"Country: {country}")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="language_certification_check"):
                    if not language:st.warning("Please select a language.")
                    elif not proof_url:st.warning("Please enter the Proof URL.")
                    else:proceed=True;st.success("Language certification details verified.")

            with col2:
                if proceed:
                    st.subheader("Certification Details")
                    st.write(f"**Language:** {language}")
                    st.write(f"**Country:** {country}")
                    st.info("Awarded Credits: 1")

                    if st.toggle("Add Entry",key="language_certification_add"):
                        df=pd.DataFrame([{"language":language,"country":country,"proof_url":proof_url,"awarded_credits":1}])
                        if self.insertDocuments(df):st.success("Language Certification Added Successfully.")
                        else:st.warning("Language Certification Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()