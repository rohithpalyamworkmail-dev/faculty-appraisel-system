import pandas as pd
import streamlit as st
from database import get_rows,get_one,insert_rows,update_rows,delete_rows

class ActivityDatabase:
    def __init__(self,table):
        self.table=table

    @property
    def department(self):
        return st.session_state.get("department")

    @property
    def faculty_id(self):
        return st.session_state.get("faculty_id")

    @property
    def faculty_name(self):
        return st.session_state.get("faculty_name","")

    def filters(self,extra=None):
        data={"department":self.department,"faculty_id":self.faculty_id}
        if extra:data.update(extra)
        return data

    def prepare(self,data,approvals=True):
        if isinstance(data,pd.DataFrame):
            df=data.copy()
            for column in ["id","department"]:
                if column in df.columns:df=df.drop(columns=[column])
            df["department"]=self.department
            df["faculty_id"]=self.faculty_id
            if "faculty_name" in df.columns or self.faculty_name:df["faculty_name"]=self.faculty_name
            if approvals:
                df["hod_approval"]=st.session_state.get("hod_approval","UN KNOWN")
                df["admin_approval"]=st.session_state.get("admin_approval","UN KNOWN")
            return df.astype(object).where(pd.notnull(df),None)

        row=dict(data)
        row.pop("id",None)
        row["department"]=self.department
        row["faculty_id"]=self.faculty_id
        if "faculty_name" in row or self.faculty_name:row["faculty_name"]=self.faculty_name
        if approvals:
            row["hod_approval"]=st.session_state.get("hod_approval","UN KNOWN")
            row["admin_approval"]=st.session_state.get("admin_approval","UN KNOWN")
        return row

    def insert(self,data,approvals=True):
        try:
            prepared=self.prepare(data,approvals)
            if isinstance(prepared,pd.DataFrame) and prepared.empty:return True
            insert_rows(self.table,prepared)
            return True
        except Exception as e:
            st.error(f"Insert Error: {e}")
            return False

    def rows(self,columns="*",filters=None):
        try:
            return get_rows(self.table,self.filters(filters),columns)
        except Exception as e:
            st.error(f"Data Fetch Error: {e}")
            return []

    def dataframe(self,columns="*",filters=None):
        return pd.DataFrame(self.rows(columns,filters))

    def one(self,columns="*",filters=None):
        try:
            return get_one(self.table,self.filters(filters),columns)
        except Exception as e:
            st.error(f"Data Fetch Error: {e}")
            return None

    def exists(self,filters):
        try:
            return get_one(self.table,self.filters(filters),"id") is not None
        except Exception as e:
            st.error(f"Record Check Error: {e}")
            return False

    def editable_rows(self,columns="*"):
        return self.rows(columns,{"hod_approval":"UN KNOWN","admin_approval":"UN KNOWN"})

    def editable_dataframe(self,columns="*"):
        return pd.DataFrame(self.editable_rows(columns))

    def delete_pending(self):
        try:
            delete_rows(self.table,self.filters({"hod_approval":"UN KNOWN","admin_approval":"UN KNOWN"}))
            return True
        except Exception as e:
            st.error(f"Delete Error: {e}")
            return False

    def delete_all(self):
        try:
            delete_rows(self.table,self.filters())
            return True
        except Exception as e:
            st.error(f"Delete Error: {e}")
            return False

    def update_by_id(self,record_id,data,approvals=False):
        try:
            values=dict(data)
            values.pop("id",None)
            values.pop("department",None)
            values.pop("faculty_id",None)
            if approvals:
                values["hod_approval"]=st.session_state.get("hod_approval","UN KNOWN")
                values["admin_approval"]=st.session_state.get("admin_approval","UN KNOWN")
            update_rows(self.table,values,{"id":record_id,"department":self.department,"faculty_id":self.faculty_id})
            return True
        except Exception as e:
            st.error(f"Update Error: {e}")
            return False

    def delete_by_id(self,record_id):
        try:
            delete_rows(self.table,{"id":record_id,"department":self.department,"faculty_id":self.faculty_id})
            return True
        except Exception as e:
            st.error(f"Delete Error: {e}")
            return False

    def replace_pending(self,data):
        old_rows=self.editable_rows("*")

        try:
            if not self.delete_pending():return False
            if self.insert(data):return True
            raise RuntimeError("Unable To Insert Updated Records")
        except Exception as e:
            try:
                backup=[{k:v for k,v in row.items() if k!="id"} for row in old_rows]
                if backup:insert_rows(self.table,backup)
            except Exception as restore_error:
                st.error(f"Backup Restore Error: {restore_error}")

            st.error(f"Update Error: {e}")
            return False