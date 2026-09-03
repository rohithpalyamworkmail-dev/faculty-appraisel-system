import streamlit as st
from io import BytesIO
from database import get_one,update_rows,upsert_rows,encode_bytea,decode_bytea

class settings:
    def __init__(self,col1,col2):
        self.col1=col1
        self.col2=col2
        self.department=st.session_state["department"]
        self.faculty_id=st.session_state["faculty_id"]

    def getImage(self):
        try:
            row=get_one("faculty_images",{"department":self.department,"faculty_id":self.faculty_id},"faculty_image")
            return decode_bytea(row.get("faculty_image")) if row else None
        except Exception as e:
            st.error(f"Image Fetch Error: {e}")
            return None

    def updateImage(self,image_bytes):
        try:
            upsert_rows("faculty_images",{"department":self.department,"faculty_id":self.faculty_id,"faculty_image":encode_bytea(image_bytes)},on_conflict="department,faculty_id")
            st.session_state["Faculty Image"]=image_bytes
            return True
        except Exception as e:
            st.error(f"Image Update Error: {e}")
            return False

    def updatePassword(self,password):
        try:
            result=update_rows("faculty",{"faculty_password":password},{"department":self.department,"faculty_id":self.faculty_id})
            return bool(result)
        except Exception as e:
            st.error(f"Password Update Error: {e}")
            return False

    def profileImage(self):
        image=self.getImage()
        with self.col1:
            st.subheader("Faculty Profile",divider=True,text_alignment="center")
            if image:
                try:st.image(BytesIO(image),caption=f"{st.session_state['faculty_name']} - {self.faculty_id}",width="stretch")
                except Exception as e:st.warning(f"Unable to display profile image: {e}")
            else:st.warning("No Profile Image Present.")

    def updateProfileImage(self):
        option=st.radio("Profile Image Source",["Upload Image","Take Photo"],horizontal=True,key="settings_image_source")
        image_file=None
        if option=="Upload Image":image_file=st.file_uploader("Upload Profile Image",type=["png","jpg","jpeg"],key="settings_image_upload")
        elif option=="Take Photo":image_file=st.camera_input("Take Profile Photo",key="settings_camera")

        if image_file:
            image_bytes=image_file.getvalue()
            st.image(image_bytes,caption="New Profile Image",width=250)

            if st.button("Update Profile Image",type="primary",width="stretch",key="settings_update_image"):
                if self.updateImage(image_bytes):
                    st.success("Profile Image Updated Successfully.")
                    st.rerun()
                else:
                    st.warning("Profile Image Could Not Be Updated.")

    def updateFacultyPassword(self):
        new_password=st.text_input("Enter New Password",type="password",key="settings_new_password")
        confirm_password=st.text_input("Confirm New Password",type="password",key="settings_confirm_password")

        if st.button("Update Password",type="primary",width="stretch",key="settings_update_password"):
            if not new_password:st.warning("Please enter a new password.")
            elif len(new_password)<6:st.warning("Password must contain at least 6 characters.")
            elif new_password!=confirm_password:st.warning("Passwords do not match.")
            elif self.updatePassword(new_password):st.success("Password Updated Successfully.")
            else:st.warning("Password Could Not Be Updated.")

    def main_layout(self):
        if not st.session_state.get("login",False):
            st.info("Please login first to access Settings.")
            return

        self.profileImage()

        with self.col2:
            st.subheader("Settings",divider=True)
            option=st.radio("Select Option",["Update Profile Picture","Update Password"],horizontal=True,key="faculty_settings_option")

            if option=="Update Profile Picture":self.updateProfileImage()
            elif option=="Update Password":self.updateFacultyPassword()