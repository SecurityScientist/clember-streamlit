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


    n_start_questions = st.number_input("Number of starting questions", value=10)
    session["n_start_questions"] = n_start_questions
    subcategory_column = st.selectbox("Subcategory column", options=df.columns)
    session["subcategory_column"] = subcategory_column

    subcategory = st.selectbox("Select subcategory", options=df[subcategory_column].unique())
  
    inital_question = """
    List {n_start_questions} yes/no questions you could ask a company see their maturity in {subcategory}
    """
    question = st.text_area("Open AI command", height=200, value=inital_question.strip()) 
    session["inital_question"] = question

    command = question.format(
        subcategory=subcategory, n_start_questions=n_start_questions
    ).strip()

    st.write(command)


    if st.button("Generate questions"):
        session["questions"] = str_to_json(openai_prompt(command))
        st.write(session["questions"])

    if session.get("questions", None):
        followup_question = "List 3 followup likert scale questions you could ask a company to better understand their cybersecurity maturity for the following question {question}"

        followup_question_prompt = st.text_area("Open AI command", height=200, value=followup_question.strip())
        session["followup_question"] = followup_question_prompt
        
        command = followup_question_prompt.format(question=session["questions"][0]).strip()
        st.write(command)
        
        if st.button("Create followup questions"):
            session["followup_questions"] = []
            
            for question in session["questions"]:
                st.write(question)
                followups = str_to_json(openai_prompt(followup_question_prompt.format(question=question).strip()))
                st.write(followups)
                session["followup_questions"] += followups
   

    if session.get("followup_questions", None):
        if st.button("Create an excel sheet"):
           data = []
           records = [row for _, row in df.iterrows()]
           for row in stqdm(records):
                command = session["inital_question"].format(
                     subcategory=row[session["subcategory_column"]], n_start_questions=session["n_start_questions"]
                ).strip()

                initial_questions = str_to_json(openai_prompt(command))

                for question in initial_questions:
                    command = session["followup_question"].format(question=question).strip()
                    followup_questions = str_to_json(openai_prompt(command))

                    for followup in followup_questions:
                        data.append({
                            "followup_question": followup,
                            "initial_question": question, 
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
                   file_name="Generated Questions.xlsx",
                   mime="application/vnd.ms-excel"
               )


