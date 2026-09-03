import pandas as pd
import streamlit as st
from activity_database import ActivityDatabase

class consultancy:
    def __init__(self):
        self.db=ActivityDatabase("consultancy_funding_grants")
        self.types=["Research Grant Applied","Applied Grant For Organizing Programmes Like Seminar Workshop Conference FDP","Research Grants For Workshop Seminar FDP Conference Etc & Projects Received","Consultancy Received"]

    def createTable(self):
        return True

    def calculateCredits(self,entry_type,amount=0,is_greater=False):
        if entry_type=="Research Grant Applied":return 1.5 if is_greater else 1
        if entry_type=="Applied Grant For Organizing Programmes Like Seminar Workshop Conference FDP":return 1
        if entry_type=="Research Grants For Workshop Seminar FDP Conference Etc & Projects Received":return amount/100000
        if entry_type=="Consultancy Received":return amount/10000
        return 0

    def duplicateEntryCheck(self,entry_type,description,proof_url,amount):
        try:
            rows=self.db.rows("type,description,proof_url,amount",{"type":entry_type})
            target_amount=float(amount or 0)
            for row in rows:
                value=row.get("amount")
                row_amount=0 if value is None or pd.isna(value) else float(value)
                if row.get("description")==description and row.get("proof_url")==proof_url and row_amount==target_amount:return True
            return False
        except Exception as e:
            st.error(f"Duplicate Entry Check Error: {e}")
            return False

    def insertDocuments(self,df):
        try:
            data=df.copy() if isinstance(df,pd.DataFrame) else dict(df)
            if isinstance(data,pd.DataFrame):data["faculty_number"]=st.session_state["faculty_id"]
            else:data["faculty_number"]=st.session_state["faculty_id"]
            return self.db.insert(data)
        except Exception as e:
            st.error(f"Insert Error: {e}")
            return False

    def deleteAllRows(self):
        return self.db.delete_pending()

    def normalizeRow(self,row):
        entry_type=row["type"]
        amount=row.get("amount",0)
        amount=0 if amount is None or pd.isna(amount) else float(amount)

        if entry_type=="Research Grant Applied":
            greater=row.get("is_amount_greater_than_10_lakhs",False)
            greater=greater if isinstance(greater,bool) else str(greater).lower()=="yes"
            row["is_amount_greater_than_10_lakhs"]="yes" if greater else "no"
        else:
            row["is_amount_greater_than_10_lakhs"]="no"

        if entry_type=="Applied Grant For Organizing Programmes Like Seminar Workshop Conference FDP":amount=0
        row["amount"]=amount
        row["credits"]=self.calculateCredits(entry_type,amount,row["is_amount_greater_than_10_lakhs"]=="yes")
        return row

    def edit_document(self):
        try:
            df=self.db.editable_dataframe("type,description,proof_url,amount,is_amount_greater_than_10_lakhs,credits")

            if df.empty:
                st.info("No Consultancy / Grant entries are available for editing.")
                return

            df["is_amount_greater_than_10_lakhs"]=df["is_amount_greater_than_10_lakhs"].fillna("no").astype(str).str.lower().eq("yes")
            config={"type":st.column_config.SelectboxColumn("Type",options=self.types,required=True),"description":st.column_config.TextColumn("Description",required=True),"proof_url":st.column_config.LinkColumn("Proof URL"),"amount":st.column_config.NumberColumn("Amount",min_value=0.0,step=1000.0),"is_amount_greater_than_10_lakhs":st.column_config.CheckboxColumn("Amount Greater Than 10 Lakhs"),"credits":st.column_config.NumberColumn("Credits")}
            edited_df=st.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["credits"],column_config=config,key="consultancy_editor")

            if st.toggle("Update",key="consultancy_update"):
                edited_df=edited_df.apply(self.normalizeRow,axis=1)

                if self.db.replace_pending(edited_df):st.success("Consultancy / Grant Entries Updated Successfully.")
                else:st.warning("Consultancy / Grant Entries Could Not Be Updated.")
        except Exception as e:
            st.error(f"Edit Error: {e}")

    def viewDocuments(self):
        try:
            df=self.db.dataframe("type,description,proof_url,amount,is_amount_greater_than_10_lakhs,credits,hod_approval,admin_approval")

            if df.empty:
                st.info("No Consultancy / Grant entries found.")
                return

            st.subheader("Consultancy, Funding & Grants")

            for _,row in df.iterrows():
                with st.container(border=True):
                    st.subheader(str(row["type"]),divider=True,text_alignment="center")
                    st.write(f"**Description:** {row['description']}")

                    if row["type"]=="Research Grant Applied":
                        amount=float(row["amount"] or 0)
                        st.write(f"**Amount:** ₹{amount:,.2f}")
                        st.write(f"**Amount Greater Than 10 Lakhs:** {str(row['is_amount_greater_than_10_lakhs']).title()}")

                    elif row["type"] in ["Research Grants For Workshop Seminar FDP Conference Etc & Projects Received","Consultancy Received"]:
                        amount=float(row["amount"] or 0)
                        st.write(f"**Amount:** ₹{amount:,.2f}")

                    st.write(f"**Proof URL:** {row['proof_url']}")
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
                st.subheader("Consultancy / Funding / Grants Entry")
                entry_type=st.radio("Select Type",self.types,index=None)
                amount=0.0
                is_greater=False

                if entry_type=="Research Grant Applied":
                    amount=st.number_input("Enter Amount",min_value=0.0,step=1000.0)
                    is_greater=st.checkbox("Is Amount Greater Than 10 Lakhs")
                elif entry_type=="Research Grants For Workshop Seminar FDP Conference Etc & Projects Received":
                    amount=st.number_input("Enter Amount Received",min_value=0.0,step=1000.0)
                elif entry_type=="Consultancy Received":
                    amount=st.number_input("Enter Consultancy Amount",min_value=0.0,step=1000.0)

                description=st.text_area("Description")
                proof_url=st.text_input("Proof URL")

                if st.toggle("Check",key="consultancy_check"):
                    if not entry_type:st.warning("Please select Type.")
                    elif entry_type in ["Research Grant Applied","Research Grants For Workshop Seminar FDP Conference Etc & Projects Received","Consultancy Received"] and amount<=0:st.warning("Please enter a valid Amount.")
                    elif not description:st.warning("Please enter Description.")
                    elif not proof_url:st.warning("Please enter Proof URL.")
                    else:proceed=True;st.success("Consultancy / Grant details verified.")

            with col2:
                if proceed:
                    credits=self.calculateCredits(entry_type,amount,is_greater)
                    st.subheader("Consultancy / Grant Details")
                    st.write(f"**Type:** {entry_type}")

                    if entry_type!="Applied Grant For Organizing Programmes Like Seminar Workshop Conference FDP":st.write(f"**Amount:** ₹{amount:,.2f}")
                    if entry_type=="Research Grant Applied":st.write(f"**Amount Greater Than 10 Lakhs:** {'Yes' if is_greater else 'No'}")

                    st.write(f"**Description:** {description}")
                    st.write(f"**Proof URL:** {proof_url}")
                    st.info(f"Credits: {credits}")

                    if st.toggle("Add Entry",key="consultancy_add"):
                        if self.duplicateEntryCheck(entry_type,description,proof_url,amount):
                            st.warning("Record Already Exists.")
                        else:
                            df=pd.DataFrame([{"type":entry_type,"description":description,"proof_url":proof_url,"amount":amount if entry_type!="Applied Grant For Organizing Programmes Like Seminar Workshop Conference FDP" else None,"is_amount_greater_than_10_lakhs":"yes" if entry_type=="Research Grant Applied" and is_greater else "no","credits":credits}])

                            if self.insertDocuments(df):st.success("Consultancy / Grant Entry Added Successfully.")
                            else:st.warning("Consultancy / Grant Entry Could Not Be Added.")

        with tab_edit:self.edit_document()
        with tab_view:self.viewDocuments()