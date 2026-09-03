import streamlit as st
from activity_database import ActivityDatabase

class hodFeedback:
    def __init__(self):
        self.db=ActivityDatabase("hod_feedbacks")

    def main_layout(self):
        try:
            df=self.db.dataframe("id,awarded_credits,reason")
            if df.empty:
                st.info("No HoD Feedback Found.")
                return

            row=df.sort_values("id").iloc[-1]

            with st.container(border=True):
                st.subheader("HoD Feedback")
                col1,col2=st.columns(2)
                with col1:st.metric("HoD Score",row["awarded_credits"])
                with col2:
                    st.write("**Reason**")
                    st.write(row["reason"])
        except Exception as e:
            st.error(f"HoD Feedback Error: {e}")