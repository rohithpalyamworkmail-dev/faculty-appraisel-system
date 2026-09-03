import streamlit as st
from streamlit_option_menu import option_menu
from classes import data_bases_and_tables,subjects,faculty,students,students_academic_details,alumni,examination_results,addTables

st.set_page_config(page_title="Faculty Appraisal Admin",layout="wide")

with st.sidebar:
    menu=option_menu("SELECT OPERATION",["Departments & Tables","Subjects","Faculty","Students","Student Academic Results","Alumni","Update Examination Results","Add Tables"],menu_icon="star",icons=["database","journal-text","person-badge","people","mortarboard-fill","person-vcard-fill","clipboard-check-fill","table"])

if menu=="Departments & Tables":
    add,delete=st.tabs(["Initialize Department","Delete Department Data"])
    with add:
        col1,col2=st.columns([1,2],border=True,gap="small")
        data_bases_and_tables(col1,col2).add()
    with delete:
        col1,col2=st.columns([2,1],border=True,gap="small")
        data_bases_and_tables(col1,col2).delete()

elif menu=="Subjects":
    add,edit=st.tabs(["Add Subjects","Edit Subjects"])
    with add:
        col1,col2=st.columns([2,1],border=True,gap="small")
        subjects(col1,col2).add()
    with edit:
        col1,col2=st.columns([2,1],border=True,gap="small")
        subjects(col1,col2).edit()

elif menu=="Faculty":
    add,edit=st.tabs(["Add Faculty","Edit Faculty"])
    with add:
        col1,col2=st.columns([2,1],border=True,gap="small")
        faculty(col1,col2).add()
    with edit:
        col1,col2=st.columns([2,1],border=True,gap="small")
        faculty(col1,col2).edit()

elif menu=="Students":
    add,edit=st.tabs(["Add Students","Edit Students"])
    with add:
        col1,col2=st.columns([2,1],border=True,gap="small")
        students(col1,col2).add()
    with edit:
        col1,col2=st.columns([2,1],border=True,gap="small")
        students(col1,col2).edit()

elif menu=="Student Academic Results":
    add,edit,view=st.tabs(["Add","Edit","View"])
    with add:
        col1,col2=st.columns([2,1],border=True,gap="small")
        students_academic_details(col1,col2).add()
    with edit:
        col1,col2=st.columns([2,1],border=True,gap="small")
        students_academic_details(col1,col2).edit()
    with view:
        col1,col2=st.columns([2,1],border=True,gap="small")
        students_academic_details(col1,col2).view()

elif menu=="Alumni":
    add,edit,view=st.tabs(["Add","Edit","View"])
    with add:
        col1,col2=st.columns([2,1],border=True,gap="small")
        alumni(col1,col2).add()
    with edit:
        col1,col2=st.columns([2,1],border=True,gap="small")
        alumni(col1,col2).edit()
    with view:
        col1,col2=st.columns([2,1],border=True,gap="small")
        alumni(col1,col2).view()

elif menu=="Update Examination Results":
    release,edit,view=st.tabs(["Release","Edit","View"])
    with release:
        col1,col2=st.columns([2,1],border=True,gap="small")
        examination_results(col1,col2).release()
    with edit:
        col1,col2=st.columns([2,1],border=True,gap="small")
        examination_results(col1,col2).edit()
    with view:
        col1,col2=st.columns([2,1],border=True,gap="small")
        examination_results(col1,col2).view()

elif menu=="Add Tables":
    add,edit,view,delete=st.tabs(["Add","Edit","View","Delete"])
    with add:
        col1,col2=st.columns([2.5,1],border=True,gap="small")
        addTables(col1,col2).add()
    with edit:
        col1,col2=st.columns([2.5,1],border=True,gap="small")
        addTables(col1,col2).edit()
    with view:
        col1,col2=st.columns([2.5,1],border=True,gap="small")
        addTables(col1,col2).view()
    with delete:
        col1,col2=st.columns([2.5,1],border=True,gap="small")
        addTables(col1,col2).delete()
