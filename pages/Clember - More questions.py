import streamlit as st
import os
import pandas as pd
from lib.openai_util import openai_command, openai_prompt
from lib.text import adjust_lang
from stqdm import stqdm
import re
import json
import io


session = st.session_state

def str_to_json(text):
    if "1." in text or "2." in text:
        splitted_text = re.split(r"\d\.", text)
        return [item.strip() for item in splitted_text if item.strip()]
    elif "[" in text:
        json_text = re.findall(r"\[.*\]", re.sub("\s+", " ", text))
    elif "{" in text:
        json_text = re.findall(r"\{.*\}", re.sub("\s+", " ", text))
    else:
        raise ValueError(f"This text does not contain JSON. Text: \n {text}")

    if len(json_text) == 0:
        raise ValueError(f"This text does not contain JSON. Text: \n {text}")

    try:
        return [item.strip() for item in json.loads(json_text[0]) if item.strip()]
    except Exception as e:
        raise ValueError(f"Json could not be loaded. Error: {e}. \nText: {text}")


BASE_DIR = "/home/streamlit-apps/data/uploaded_files"
files = os.listdir(BASE_DIR)
files = [f for f in files if ".xlsx" in f]

filename = st.selectbox("Choose a file", options=files)

if filename:
    df = pd.read_excel(f"{BASE_DIR}/{filename}")
    st.write(df.head())


    n_questions = st.number_input("Number of starting questions", value=10)
    session["n_questions"] = n_questions

    question_column = st.selectbox("Question column", options=df.columns)
    session["question_column"] = question_column

    question = st.selectbox("Select question", options=df[question_column].unique())
  
    start_empty_command = """
    Act as a journalist and list {n_questions} alternative ways to ask the question in active tense for an IT manager. Also use "You" instead of "Organization".  {question}.
    """
    empty_command = st.text_area("Open AI command", height=200, value=start_empty_command.strip()) 
    session["empty_command"] = empty_command

    command = empty_command.format(
        question=question, n_questions=n_questions
    ).strip()

    st.write(command)


    if st.button("Generate questions"):
        session["questions"] = str_to_json(openai_prompt(command))
        st.write(session["questions"])
  

    if st.button("Create an excel sheet"):
       data = []
       records = [row for _, row in df.iterrows()]
       for row in stqdm(records):
            command = session["empty_command"].format(
                 question=row[session["question_column"]], n_questions=session["n_questions"]
            ).strip()

            alternate_questions = str_to_json(openai_prompt(command))

            for alter_question in alternate_questions:
                data.append({
                    "alternate_question": alter_question, 
                    **row
                })
    
       buffer = io.BytesIO()
       output_df = pd.DataFrame(data)
       with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
           # Write each dataframe to a different worksheet.
           output_df.to_excel(writer, sheet_name='Questions')

           # Close the Pandas Excel writer and output the Excel file to the buffer
           writer.save()

           st.download_button(
               label="Download Excel",
               data=buffer,
               file_name="More Questions.xlsx",
               mime="application/vnd.ms-excel"
           )


