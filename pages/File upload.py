import os
import streamlit as st


#Get uploaded file
temp_file = st.file_uploader("Enter file here!")

#Write back out to disk (button to confirm)
if st.button("Save file on disk"):
    with open(f"{os.getcwd()}/data/uploaded_files/"+temp_file.name,"wb") as f:
        f.write(temp_file.getvalue())
