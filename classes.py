import pandas as pd
import streamlit as st

from global_fields import department,tables_list,tables_fields,batches
from global_classes import get_or_create_db,delete_db,create_table,addAllRows,deleteAllRows,displayRows,select_students,delete_students
from database import get_rows,get_one,upsert_rows
from supabase_client import supabase


def _read_csv(file,container):
    try:return pd.read_csv(file)
    except Exception as e:container.error(f"Unable To Read File: {e}");return None


def _dataframe(database,table):
    columns,rows=displayRows(database,table)
    return pd.DataFrame(rows,columns=columns)


class data_bases_and_tables:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2

    def add(self):
        operation=self.col1.radio("Select Operation To Perform",["Add DB","Add Tables"],key="operation")

        if operation=="Add DB":
            database=self.col2.pills("Select Department",department,key="create_db")
            confirm=self.col2.toggle("Confirm To Create Department",key="confirm_create")

            if confirm:
                if not database:self.col2.warning("Please Select A Department");return
                if get_or_create_db(database,"create"):self.col2.success(f"{database} Is Ready In Supabase")
                else:self.col2.error(f"Unable To Initialize {database}")

        else:
            database=self.col2.pills("Select Department",department,key="connect_db")
            confirm=self.col2.toggle("Confirm Core Tables",key="confirm_connect")

            if confirm:
                if not database:self.col2.warning("Please Select A Department");return

                connection=get_or_create_db(database,"get")

                for table_name,fields in zip(tables_list,tables_fields):
                    message,status=create_table(connection,table_name,fields)
                    if status:self.col2.success(f"{table_name} Ready")
                    else:self.col2.error(f"{table_name}: {message}")

    def delete(self):
        database=self.col1.pills("Select Department To Remove Permanently",department,key="delete_db")
        confirm=self.col1.toggle("Confirm To Delete",key="confirm_delete")

        if confirm:
            if not database:self.col1.warning("Please Select A Department");return
            self.col1.success(delete_db(database))


class subjects:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2

    def add(self):
        database=self.col1.pills("Select Department To Add Subjects",department,key="add_subjects_db")
        file=self.col1.file_uploader("Upload Subjects Data",type=["csv"],key="subjects_file")
        confirm=self.col1.toggle(f"Confirm To Add The Uploaded File - {file.name if file else ''}",key="confirm_add_subjects")

        if not confirm:return
        if not database:self.col1.warning("Please Select A Department");return
        if not file:self.col1.warning("Please Upload A CSV File");return

        df=_read_csv(file,self.col2)
        if df is None:return

        self.col2.header(file.name,divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)

        if self.col2.toggle(f"Add To Supabase - {database}",key="upload_subjects"):
            if addAllRows(database,"subjects",df):self.col2.success("Subjects Added Successfully")
            else:self.col2.warning("Unable To Add Subjects")

    def edit(self):
        database=self.col1.pills("Select Department To Edit Subjects",department,key="edit_subjects_db")
        if not database:self.col1.warning("Please Select A Department");return

        try:df=_dataframe(database,"subjects")
        except Exception as e:self.col2.error(f"Unable To Display Subjects: {e}");return

        if df.empty:self.col2.info("No Subjects Present.");return

        edited=self.col2.data_editor(df,num_rows="dynamic",use_container_width=True,hide_index=True,key="subjects_editor")

        if self.col2.toggle("Confirm To Update",key="confirm_update_subjects"):
            if deleteAllRows(database,"subjects") and addAllRows(database,"subjects",edited):self.col2.success("SUCCESSFULLY UPDATED")
            else:self.col2.warning("SOME ERROR HAPPENED WHILE PROCESSING")


class faculty:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2

    def add(self):
        database=self.col1.pills("Select Department To Add Faculty",department,key="add_faculty_db")
        file=self.col1.file_uploader("Upload Faculty Data",type=["csv"],key="faculty_file")
        confirm=self.col1.toggle(f"Confirm To Add The Uploaded File - {file.name if file else ''}",key="confirm_add_faculty")

        if not confirm:return
        if not database:self.col1.warning("Please Select A Department");return
        if not file:self.col1.warning("Please Upload A CSV File");return

        df=_read_csv(file,self.col2)
        if df is None:return

        self.col2.header(file.name,divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)

        if self.col2.toggle(f"Add To Supabase - {database}",key="upload_faculty"):
            if addAllRows(database,"faculty",df):self.col2.success("Faculty Added Successfully")
            else:self.col2.warning("Unable To Add Faculty")

    def edit(self):
        database=self.col1.pills("Select Department To Edit Faculty",department,key="edit_faculty_db")
        if not database:self.col1.warning("Please Select A Department");return

        try:df=_dataframe(database,"faculty")
        except Exception as e:self.col2.error(f"Unable To Display Faculty: {e}");return

        if df.empty:self.col2.info("No Faculty Present.");return

        edited=self.col2.data_editor(df,num_rows="dynamic",use_container_width=True,hide_index=True,key="faculty_editor")

        if self.col2.toggle("Confirm To Update",key="confirm_update_faculty"):
            if deleteAllRows(database,"faculty") and addAllRows(database,"faculty",edited):self.col2.success("SUCCESSFULLY UPDATED")
            else:self.col2.warning("SOME ERROR HAPPENED WHILE PROCESSING")


class students:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2

    def add(self):
        database=self.col1.pills("Select Department To Add Students",department,key="add_students_db")
        file=self.col1.file_uploader("Upload Students Data",type=["csv"],key="students_file")
        confirm=self.col1.toggle(f"Confirm To Add The Uploaded File - {file.name if file else ''}",key="confirm_add_students")

        if not confirm:return
        if not database:self.col1.warning("Please Select A Department");return
        if not file:self.col1.warning("Please Upload A CSV File");return

        df=_read_csv(file,self.col2)
        if df is None:return

        self.col2.header(file.name,divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)

        if self.col2.toggle(f"Add To Supabase - {database}",key="upload_students"):
            if addAllRows(database,"students",df):self.col2.success("Students Added Successfully")
            else:self.col2.warning("Unable To Add Students")

    def edit(self):
        database=self.col1.pills("Select Department To Edit Students",department,key="edit_students_db")
        batch=self.col1.pills("Select Batch",batches,key="edit_students_batch")
        confirm=self.col1.toggle("Confirm To Display Students",key="confirm_display_students")

        if not confirm:return
        if not database:self.col1.warning("Please Select A Department");return
        if not batch:self.col1.warning("Please Select A Batch");return

        try:
            columns,rows=select_students(database,"students",batch)
            df=pd.DataFrame(rows,columns=columns)
        except Exception as e:self.col2.error(f"Unable To Display Students: {e}");return

        if df.empty:self.col2.info("No Students Present.");return

        edited=self.col2.data_editor(df,num_rows="dynamic",use_container_width=True,hide_index=True,key="students_editor")

        if self.col2.toggle("Confirm To Update",key="confirm_update_students"):
            if delete_students(database,"students",batch) and addAllRows(database,"students",edited):self.col2.success("SUCCESSFULLY UPDATED")
            else:self.col2.warning("SOME ERROR HAPPENED WHILE PROCESSING")


class students_academic_details:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2
        self.table="students_academic_details"
        self.columns=["student_roll_numner","student_batch","student_department","regulation","status"]

    def removeDuplicates(self,database,df):
        try:
            df=df[self.columns].drop_duplicates().reset_index(drop=True)
            existing=pd.DataFrame(get_rows(self.table,{"department":database},",".join(self.columns)))

            if existing.empty:return df,0

            existing_keys=set(existing[self.columns].fillna("").astype(str).apply(lambda r:tuple(x.strip() for x in r),axis=1))
            mask=df.fillna("").astype(str).apply(lambda r:tuple(x.strip() for x in r) not in existing_keys,axis=1)
            new_df=df[mask].reset_index(drop=True)

            return new_df,len(df)-len(new_df)

        except Exception as e:
            self.col2.error(f"Duplicate Check Error: {e}")
            return pd.DataFrame(),0

    def add(self):
        database=self.col1.pills("Select Department To Add Student Academic Results",department,key="academic_details_add_db")
        file=self.col1.file_uploader("Upload Student Academic Results",type=["csv"],key="academic_details_file")
        confirm=self.col1.toggle(f"Confirm To Add The Uploaded File - {file.name if file else ''}",key="academic_details_confirm")

        if not confirm:return
        if not database:self.col1.warning("Please Select A Department");return
        if not file:self.col1.warning("Please Upload A CSV File");return

        df=_read_csv(file,self.col2)
        if df is None:return

        missing=[column for column in self.columns if column not in df.columns]
        if missing:self.col2.error(f"Missing Columns: {', '.join(missing)}");return

        original_count=len(df)
        df=df[self.columns].drop_duplicates().reset_index(drop=True)
        dataframe_duplicates=original_count-len(df)

        self.col2.header(file.name,divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)

        if self.col2.toggle(f"Add To Supabase - {database}",key="academic_details_upload"):
            new_df,database_duplicates=self.removeDuplicates(database,df)
            duplicate_count=dataframe_duplicates+database_duplicates

            if new_df.empty:self.col2.info(f"No New Records To Add. {duplicate_count} Duplicate Record(s) Skipped.");return

            if addAllRows(database,self.table,new_df):
                self.col2.success(f"{len(new_df)} Record(s) Added Successfully.")
                if duplicate_count:self.col2.warning(f"{duplicate_count} Duplicate Record(s) Skipped.")
            else:self.col2.warning("Unable To Add Records")

    def edit(self):
        database=self.col1.pills("Select Department To Edit Student Academic Results",department,key="academic_details_edit_db")
        if not database:self.col1.warning("Please Select A Department");return

        try:df=_dataframe(database,self.table)
        except Exception as e:self.col2.error(f"Unable To Display Records: {e}");return

        if df.empty:self.col2.info("No Records Present.");return

        edited=self.col2.data_editor(df,num_rows="dynamic",use_container_width=True,hide_index=True,key="academic_details_editor")

        if self.col2.toggle("Confirm To Update",key="academic_details_update"):
            edited=edited[self.columns].drop_duplicates().reset_index(drop=True)
            if deleteAllRows(database,self.table) and addAllRows(database,self.table,edited):self.col2.success("SUCCESSFULLY UPDATED")
            else:self.col2.warning("SOME ERROR HAPPENED WHILE PROCESSING")

    def view(self):
        database=self.col1.pills("Select Department To View Student Academic Results",department,key="academic_details_view_db")
        if not database:self.col1.warning("Please Select A Department");return

        try:df=_dataframe(database,self.table)
        except Exception as e:self.col2.error(f"Unable To Display Records: {e}");return

        if df.empty:self.col2.info("No Records Present.");return

        self.col2.header("Student Academic Results",divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)


class alumni:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2
        self.table="alumni"
        self.columns=["student_roll_number","student_batch","student_department","student_regulation"]

    def removeDuplicates(self,database,df):
        try:
            df=df[self.columns].drop_duplicates(subset=["student_roll_number"]).reset_index(drop=True)
            existing=pd.DataFrame(get_rows(self.table,{"department":database},"student_roll_number"))

            if existing.empty:return df,0

            existing_rolls=set(existing["student_roll_number"].dropna().astype(str).str.strip())
            mask=~df["student_roll_number"].fillna("").astype(str).str.strip().isin(existing_rolls)
            new_df=df[mask].reset_index(drop=True)

            return new_df,len(df)-len(new_df)

        except Exception as e:
            self.col2.error(f"Duplicate Check Error: {e}")
            return pd.DataFrame(),0

    def add(self):
        database=self.col1.pills("Select Department To Add Alumni",department,key="alumni_add_db")
        file=self.col1.file_uploader("Upload Alumni Data",type=["csv"],key="alumni_file")
        confirm=self.col1.toggle(f"Confirm To Add The Uploaded File - {file.name if file else ''}",key="alumni_confirm")

        if not confirm:return
        if not database:self.col1.warning("Please Select A Department");return
        if not file:self.col1.warning("Please Upload A CSV File");return

        df=_read_csv(file,self.col2)
        if df is None:return

        missing=[column for column in self.columns if column not in df.columns]
        if missing:self.col2.error(f"Missing Columns: {', '.join(missing)}");return

        original_count=len(df)
        df=df[self.columns].drop_duplicates(subset=["student_roll_number"]).reset_index(drop=True)
        dataframe_duplicates=original_count-len(df)

        self.col2.header(file.name,divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)

        if self.col2.toggle(f"Add To Supabase - {database}",key="alumni_upload"):
            new_df,database_duplicates=self.removeDuplicates(database,df)
            duplicate_count=dataframe_duplicates+database_duplicates

            if new_df.empty:self.col2.info(f"No New Records To Add. {duplicate_count} Duplicate Record(s) Skipped.");return

            if addAllRows(database,self.table,new_df):
                self.col2.success(f"{len(new_df)} Record(s) Added Successfully.")
                if duplicate_count:self.col2.warning(f"{duplicate_count} Duplicate Record(s) Skipped.")
            else:self.col2.warning("Unable To Add Alumni")

    def edit(self):
        database=self.col1.pills("Select Department To Edit Alumni",department,key="alumni_edit_db")
        if not database:self.col1.warning("Please Select A Department");return

        try:df=_dataframe(database,self.table)
        except Exception as e:self.col2.error(f"Unable To Display Alumni: {e}");return

        if df.empty:self.col2.info("No Records Present.");return

        edited=self.col2.data_editor(df,num_rows="dynamic",use_container_width=True,hide_index=True,key="alumni_editor")

        if self.col2.toggle("Confirm To Update",key="alumni_update"):
            edited=edited[self.columns].drop_duplicates(subset=["student_roll_number"]).reset_index(drop=True)
            if deleteAllRows(database,self.table) and addAllRows(database,self.table,edited):self.col2.success("SUCCESSFULLY UPDATED")
            else:self.col2.warning("SOME ERROR HAPPENED WHILE PROCESSING")

    def view(self):
        database=self.col1.pills("Select Department To View Alumni",department,key="alumni_view_db")
        if not database:self.col1.warning("Please Select A Department");return

        try:df=_dataframe(database,self.table)
        except Exception as e:self.col2.error(f"Unable To Display Alumni: {e}");return

        if df.empty:self.col2.info("No Records Present.");return

        self.col2.header("Alumni",divider="blue",text_alignment="center")
        self.col2.dataframe(df,use_container_width=True,hide_index=True)


class examination_results:
    def __init__(self,col1,col2):
        self.col1,self.col2=col1,col2
        self.table="examination_results_faculty"
        self.columns=["faculty_id","faculty_name","awarded_credits","academic_year","quarter","hod_approval","admin_approval"]

    def createTable(self,database):
        try:
            get_rows(self.table,{"department":database},"id")
            return True
        except Exception as e:
            self.col2.error(f"Supabase Table Error: {e}")
            return False

    def fetch_mentees(self,database,faculty_id):
        try:return [str(row["student_roll_number"]).strip() for row in get_rows("students",{"department":database,"student_mentor_id":faculty_id},"student_roll_number") if row.get("student_roll_number") is not None]
        except Exception as e:self.col2.error(f"Mentee Fetch Error For {faculty_id}: {e}");return []

    def fetchStudentStatus(self,database,student_roll_number):
        try:
            row=get_one("students_academic_details",{"department":database,"student_roll_numner":student_roll_number},"status")
            return str(row["status"]).strip() if row and row.get("status") is not None else None
        except:return None

    def calculateCredits(self,database,faculty_id):
        mentees=self.fetch_mentees(database,faculty_id)
        if not mentees:return 0
        return 2 if all((self.fetchStudentStatus(database,roll) or "").lower()=="pass" for roll in mentees) else 0

    def saveResult(self,database,faculty_id,faculty_name,credits,academic_year,quarter):
        try:
            upsert_rows(self.table,{"department":database,"faculty_id":faculty_id,"faculty_name":faculty_name,"awarded_credits":float(credits),"academic_year":academic_year,"quarter":quarter,"hod_approval":"APPROVED","admin_approval":"APPROVED"},on_conflict="department,faculty_id,academic_year,quarter")
            return True
        except Exception as e:
            self.col2.error(f"Result Save Error For {faculty_id}: {e}")
            return False

    def release(self):
        database=self.col1.pills("Select Department",department,key="examination_results_department")
        academic_year=self.col1.text_input("Enter Academic Year",placeholder="2026-2027",key="examination_results_year")
        quarter=self.col1.pills("Select Quarter",["Q1","Q2"],key="examination_results_quarter")
        proceed=self.col1.checkbox("Proceed To Update Results",key="examination_results_proceed")

        if not proceed:return
        if not database:self.col1.warning("Please Select Department.");return
        if not academic_year:self.col1.warning("Please Enter Academic Year.");return
        if not quarter:self.col1.warning("Please Select Quarter.");return
        if not self.createTable(database):return

        try:
            faculty_rows=get_rows("faculty",{"department":database},"faculty_id,faculty_name")
            unique={str(row["faculty_id"]).strip():row.get("faculty_name","") for row in faculty_rows if row.get("faculty_id") is not None}

            if not unique:self.col2.info("No Faculty Records Present.");return

            results=[]

            for faculty_id,faculty_name in unique.items():
                credits=self.calculateCredits(database,faculty_id)
                status=self.saveResult(database,faculty_id,faculty_name,credits,academic_year,quarter)
                results.append({"Faculty ID":faculty_id,"Faculty Name":faculty_name,"Awarded Credits":credits,"Academic Year":academic_year,"Quarter":quarter,"HoD Approval":"APPROVED","Admin Approval":"APPROVED","Updated":"Yes" if status else "No"})

            self.col2.header("Examination Results Updated",divider="blue",text_alignment="center")
            self.col2.dataframe(pd.DataFrame(results),use_container_width=True,hide_index=True)
            self.col2.success("Examination Results Released Successfully.")

        except Exception as e:self.col2.error(f"Release Error: {e}")

    def edit(self):
        database=self.col1.pills("Select Department To Edit Results",department,key="edit_examination_results_db")
        if not database:self.col1.warning("Please Select Department.");return
        if not self.createTable(database):return

        try:df=_dataframe(database,self.table)
        except Exception as e:self.col2.error(f"Unable To Display Examination Results: {e}");return

        if df.empty:self.col2.info("No Examination Results Present.");return

        edited=self.col2.data_editor(df,num_rows="delete",use_container_width=True,hide_index=True,disabled=["faculty_id","faculty_name","hod_approval","admin_approval"],column_config={"awarded_credits":st.column_config.NumberColumn("Awarded Credits",min_value=0.0,max_value=2.0,step=0.5),"quarter":st.column_config.SelectboxColumn("Quarter",options=["Q1","Q2"]),"academic_year":st.column_config.TextColumn("Academic Year"),"hod_approval":"HoD Approval","admin_approval":"Admin Approval"},key="examination_results_editor")

        if self.col2.toggle("Confirm To Update",key="confirm_update_examination_results"):
            edited=edited.drop_duplicates().reset_index(drop=True)
            edited["hod_approval"]="APPROVED"
            edited["admin_approval"]="APPROVED"

            if deleteAllRows(database,self.table) and addAllRows(database,self.table,edited):self.col2.success("EXAMINATION RESULTS UPDATED SUCCESSFULLY")
            else:self.col2.warning("SOME ERROR HAPPENED WHILE UPDATING")

    def view(self):
        database=self.col1.pills("Select Department To View Results",department,key="view_examination_results_db")
        if not database:self.col1.warning("Please Select Department.");return
        if not self.createTable(database):return

        academic_year=self.col1.text_input("Academic Year Filter",key="view_results_year")
        quarter=self.col1.pills("Quarter Filter",["All","Q1","Q2"],default="All",key="view_results_quarter")

        try:
            filters={"department":database}
            if academic_year:filters["academic_year"]=academic_year
            if quarter and quarter!="All":filters["quarter"]=quarter

            df=pd.DataFrame(get_rows(self.table,filters,",".join(self.columns),order_by="faculty_id"))

            if df.empty:self.col2.info("No Examination Results Present.");return

            self.col2.header("Faculty Examination Results",divider="blue",text_alignment="center")
            c1,c2,c3=self.col2.columns(3)
            c1.metric("Faculty",len(df))
            c2.metric("Full Credits",len(df[df["awarded_credits"]==2]))
            c3.metric("Zero Credits",len(df[df["awarded_credits"]==0]))
            self.col2.dataframe(df,use_container_width=True,hide_index=True)

        except Exception as e:self.col2.error(f"View Error: {e}")


class addTables:
    def __init__(self,col1,col2,key_prefix="table_manager"):
        self.col1,self.col2,self.key_prefix=col1,col2,key_prefix

    def key(self,name):return f"{self.key_prefix}_{name}"
    def getDatabases(self):return list(department)+["organization"]

    def cleanName(self,name):
        name=str(name).strip().replace(" ","_").replace("-","_").replace("/","_")
        name="".join(c for c in name if ((c.isascii() and c.isalnum()) or c=="_")).strip("_").lower()
        if name and name[0].isdigit():name=f"column_{name}"
        return name

    def inferSqlType(self,series):
        clean=series.dropna()
        clean=clean[clean.astype(str).str.strip()!=""] if not clean.empty else clean
        if clean.empty:return "TEXT"
        numeric=pd.to_numeric(clean,errors="coerce")
        if numeric.notna().all():return "BIGINT" if (numeric%1==0).all() else "DOUBLE PRECISION"
        return "TEXT"

    def prepareEnteredData(self,df):
        if df is None or df.empty:return None,None
        df=df.dropna(how="all").reset_index(drop=True)
        if df.empty:return None,None

        headers=[self.cleanName(value) if not pd.isna(value) else f"column_{i+1}" for i,value in enumerate(df.iloc[0].tolist())]
        headers=[value if value else f"column_{i+1}" for i,value in enumerate(headers)]

        if len(headers)!=len(set(headers)):st.error("Duplicate Column Names Are Not Allowed.");return None,None

        data=df.iloc[1:].copy()
        data.columns=headers
        return headers,data.dropna(how="all").drop_duplicates().reset_index(drop=True)

    def isMissing(self,value):
        if value is None:return True
        try:
            result=pd.isna(value)
            if not hasattr(result,"__len__"):return bool(result)
        except:pass
        return False

    def convertValue(self,value,data_type,column):
        if self.isMissing(value) or (isinstance(value,str) and not value.strip()):return None
        data_type=str(data_type).upper()

        if data_type in ["INTEGER","BIGINT"]:
            try:
                number=float(value)
                if not number.is_integer():raise ValueError
                return int(number)
            except:raise ValueError(f"Column '{column}' requires a whole number. Received '{value}'.")

        if data_type in ["REAL","DOUBLE PRECISION","FLOAT"]:
            try:return float(value)
            except:raise ValueError(f"Column '{column}' requires a numeric value. Received '{value}'.")

        return str(value)

    def normalizeDataFrame(self,df,definitions):
        data=df.copy()
        types={item["name"]:item["type"] for item in definitions}
        for column in data.columns:data[column]=data[column].apply(lambda value:self.convertValue(value,types.get(column,"TEXT"),column))
        return data

    def dataframeToRecords(self,df):
        if df is None or df.empty:return []
        records=[]

        for _,row in df.iterrows():
            record={}
            for column,value in row.items():
                if self.isMissing(value):record[column]=None
                elif hasattr(value,"item"):
                    try:record[column]=value.item()
                    except:record[column]=value
                else:record[column]=value
            records.append(record)

        return records

    def getTables(self,database):
        if not database:return []

        try:
            data=supabase.rpc("dynamic_list_tables",{"p_database":database}).execute().data or []
            result=[]

            for item in data:
                if isinstance(item,dict) and item.get("table_name"):result.append(item["table_name"])
                elif item:result.append(str(item))

            return sorted(set(result))

        except Exception as e:st.error(f"Table Fetch Error: {e}");return []

    def tableExists(self,database,table):return table in self.getTables(database)

    def getTablePayload(self,database,table):
        try:
            data=supabase.rpc("dynamic_get_table",{"p_database":database,"p_table":table}).execute().data
            if isinstance(data,list) and len(data)==1:data=data[0]
            return data if isinstance(data,dict) else {}
        except Exception as e:st.error(f"Data Fetch Error: {e}");return {}

    def getTableColumnsMetadata(self,database,table):
        columns=self.getTablePayload(database,table).get("columns",[])
        return columns if isinstance(columns,list) else []

    def getTableColumns(self,database,table):return [item.get("name") for item in self.getTableColumnsMetadata(database,table) if item.get("name")]

    def getTableData(self,database,table):
        payload=self.getTablePayload(database,table)
        metadata=payload.get("columns",[])
        rows=payload.get("rows",[])
        columns=[item.get("name") for item in metadata if item.get("name")]

        if not rows:return pd.DataFrame(columns=columns)

        df=pd.DataFrame(rows)

        for column in columns:
            if column not in df.columns:df[column]=None

        return df[columns]

    def createTableFromDataFrame(self,database,table_name,df):
        try:
            table_name=self.cleanName(table_name)

            if not table_name:st.warning("Please Enter A Valid Table Name.");return False
            if self.tableExists(database,table_name):st.warning(f'Table "{table_name}" Already Exists.');return False
            if df is None or len(df.columns)==0:st.warning("No Columns Are Available.");return False

            cleaned=[self.cleanName(column) for column in df.columns]

            if any(not column for column in cleaned):st.error("Invalid Column Name Detected.");return False
            if len(cleaned)!=len(set(cleaned)):st.error("Duplicate Column Names Are Not Allowed.");return False

            data=df.copy()
            data.columns=cleaned
            definitions=[{"name":column,"type":self.inferSqlType(data[column])} for column in data.columns]
            normalized=self.normalizeDataFrame(data,definitions)
            rows=self.dataframeToRecords(normalized)

            supabase.rpc("dynamic_create_table",{"p_database":database,"p_table":table_name,"p_columns":definitions,"p_rows":rows}).execute()
            return True

        except Exception as e:st.error(f"Table Creation Error: {e}");return False

    def replaceTableData(self,database,table,df):
        try:
            metadata=self.getTableColumnsMetadata(database,table)
            columns=[item.get("name") for item in metadata if item.get("name")]

            if list(df.columns)!=columns:st.error("Column Structure Cannot Be Changed In Edit Mode.");return False

            data=df.dropna(how="all").drop_duplicates().reset_index(drop=True)
            data=self.normalizeDataFrame(data,metadata)
            rows=self.dataframeToRecords(data)

            supabase.rpc("dynamic_replace_table_data",{"p_database":database,"p_table":table,"p_rows":rows}).execute()
            return True

        except Exception as e:st.error(f"Update Error: {e}");return False

    def dropTable(self,database,table):
        try:
            if not self.tableExists(database,table):st.error(f'Table "{table}" Does Not Exist.');return False
            supabase.rpc("dynamic_drop_table",{"p_database":database,"p_table":table}).execute()
            return True
        except Exception as e:st.error(f"Drop Table Error: {e}");return False

    def add(self):
        with self.col1:
            st.subheader("Add Table")
            database=st.pills("Select Database / Scope",self.getDatabases(),selection_mode="single",key=self.key("add_database"))
            mode=st.radio("Add Using",["Enter","Upload CSV"],horizontal=True,key=self.key("add_mode"))
            table_name=st.text_input("Enter Table Name",key=self.key("add_table_name"))
            number_of_columns=st.number_input("Number Of Columns",min_value=1,max_value=50,value=3,step=1,key=self.key("column_count")) if mode=="Enter" else None

        with self.col2:
            if not database:st.info("Please Select A Database / Scope.");return

            if mode=="Enter":
                st.info("First row contains column names. Remaining rows contain actual records.")
                initial=pd.DataFrame([[f"column_{i+1}" for i in range(int(number_of_columns))]],columns=[f"Field {i+1}" for i in range(int(number_of_columns))])
                entered=st.data_editor(initial,num_rows="dynamic",use_container_width=True,hide_index=True,key=self.key(f"manual_editor_{number_of_columns}"))

                if st.button("Create Table",type="primary",width="stretch",key=self.key("manual_create")):
                    if not table_name:st.warning("Please Enter Table Name.");return

                    columns,data=self.prepareEnteredData(entered)
                    if columns is None:return

                    st.dataframe(pd.DataFrame({"Column Name":columns,"Detected Data Type":[self.inferSqlType(data[column]) if not data.empty else "TEXT" for column in columns]}),use_container_width=True,hide_index=True)

                    if self.createTableFromDataFrame(database,table_name,data):st.success(f'Table "{self.cleanName(table_name)}" Created Successfully In Supabase.')

            else:
                file=st.file_uploader("Upload CSV File",type=["csv"],key=self.key("csv_upload"))
                if not file:st.info("Upload A CSV File To Continue.");return

                try:
                    df=pd.read_csv(file).dropna(how="all").drop_duplicates().reset_index(drop=True)
                    df.columns=[self.cleanName(column) for column in df.columns]

                    if any(not column for column in df.columns):st.error("CSV Contains Invalid Column Names.");return
                    if len(df.columns)!=len(set(df.columns)):st.error("CSV Contains Duplicate Column Names.");return

                    st.subheader("CSV Preview",divider=True)
                    st.dataframe(df,use_container_width=True,hide_index=True)

                    structure=pd.DataFrame({"Column Name":df.columns,"Detected Data Type":[self.inferSqlType(df[column]) for column in df.columns]})
                    st.subheader("Detected Structure")
                    st.dataframe(structure,use_container_width=True,hide_index=True)

                    if st.button("Create Table From CSV",type="primary",width="stretch",key=self.key("csv_create")):
                        if not table_name:st.warning("Please Enter Table Name.");return
                        if self.createTableFromDataFrame(database,table_name,df):st.success(f'Table "{self.cleanName(table_name)}" Created Successfully In Supabase.')

                except Exception as e:st.error(f"CSV Read Error: {e}")

    def edit(self):
        with self.col1:
            st.subheader("Edit Table")
            database=st.pills("Select Database / Scope",self.getDatabases(),selection_mode="single",key=self.key("edit_database"))
            tables=self.getTables(database) if database else []
            table=st.radio("Select Table",tables,key=self.key("edit_table")) if tables else None

        with self.col2:
            if not database:st.info("Please Select A Database / Scope.");return
            if not tables:st.info("No Dynamic Tables Present In Selected Scope.");return
            if not table:return

            df=self.getTableData(database,table)
            metadata=self.getTableColumnsMetadata(database,table)

            st.subheader(table.replace("_"," ").title(),divider=True,text_alignment="center")
            st.dataframe(pd.DataFrame([{"Column":item.get("name"),"Type":item.get("type")} for item in metadata]),use_container_width=True,hide_index=True)

            edited=st.data_editor(df,num_rows="dynamic",use_container_width=True,hide_index=True,key=self.key(f"editor_{database}_{table}"))

            if st.button("Update Table",type="primary",width="stretch",key=self.key(f"update_{database}_{table}")):
                if self.replaceTableData(database,table,edited):st.success("Table Updated Successfully In Supabase.")

    def view(self):
        with self.col1:
            st.subheader("View Table")
            database=st.pills("Select Database / Scope",self.getDatabases(),selection_mode="single",key=self.key("view_database"))
            tables=self.getTables(database) if database else []
            table=st.radio("Select Table",tables,key=self.key("view_table")) if tables else None

        with self.col2:
            if not database:st.info("Please Select A Database / Scope.");return
            if not tables:st.info("No Dynamic Tables Present In Selected Scope.");return
            if not table:return

            df=self.getTableData(database,table)
            metadata=self.getTableColumnsMetadata(database,table)

            st.subheader(table.replace("_"," ").title(),divider=True,text_alignment="center")

            c1,c2,c3=st.columns(3)
            c1.metric("Rows",len(df))
            c2.metric("Columns",len(metadata))
            c3.metric("Scope",database)

            st.subheader("Table Structure")
            st.dataframe(pd.DataFrame([{"Column Name":item.get("name"),"Data Type":item.get("type")} for item in metadata]),use_container_width=True,hide_index=True)

            st.subheader("Table Data")
            if df.empty:st.info("No Records Present In This Table.")
            else:st.dataframe(df,use_container_width=True,hide_index=True)

    def delete(self):
        with self.col1:
            st.subheader("Delete / Drop Table")
            database=st.pills("Select Database / Scope",self.getDatabases(),selection_mode="single",key=self.key("delete_database"))
            tables=self.getTables(database) if database else []
            table=st.radio("Select Table To Delete",tables,key=self.key("delete_table")) if tables else None
            proceed=st.toggle("Proceed To Delete",key=self.key("delete_proceed"),disabled=table is None)

        with self.col2:
            if not database:st.info("Please Select A Database / Scope.");return
            if not tables:st.info("No Dynamic Tables Present In Selected Scope.");return
            if not table:st.info("Please Select A Table.");return

            st.subheader("Delete Table",divider=True,text_alignment="center")
            st.warning(f"Selected Scope: {database}")
            st.warning(f"Selected Table: {table}")

            df=self.getTableData(database,table)
            if df.empty:st.info("Selected Table Contains No Records.")
            else:st.dataframe(df,use_container_width=True,hide_index=True)

            st.error("Dropping this table permanently removes its structure and all records from Supabase.")

            confirm_name=st.text_input(f'Type "{table}" To Confirm',key=self.key(f"confirm_name_{database}_{table}"),disabled=not proceed)
            exact_match=proceed and confirm_name.strip()==table

            if not proceed:st.info("Enable 'Proceed To Delete' To Continue.")
            elif not exact_match:st.warning("Type The Exact Table Name To Enable The Delete Button.")

            if st.button("DELETE / DROP TABLE",type="primary",width="stretch",disabled=not exact_match,key=self.key(f"drop_button_{database}_{table}")):
                if self.dropTable(database,table):
                    st.success(f'Table "{table}" Deleted Permanently From Supabase.')
                    st.rerun()

    def main_layout(self):
        add_tab,edit_tab,view_tab,delete_tab=st.tabs(["Add","Edit","View","Delete"])
        with add_tab:self.add()
        with edit_tab:self.edit()
        with view_tab:self.view()
        with delete_tab:self.delete()