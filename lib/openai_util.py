import streamlit as st
import openai
from time import sleep
from lib.util import load_creds
from openai.error import RateLimitError, ServiceUnavailableError

creds = load_creds()
openai.api_key = creds["openai"]


def _get_resp(prompt, max_tokens=500, temperature=0.3):
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=temperature,  max_tokens=max_tokens)
    return response.to_dict()["choices"][0]["text"]


def _openai_prompt(prompt, max_tokens=500, temperature=0.3):
    success = False
    while success is False:
        
        try:
            resp = _get_resp(prompt, max_tokens=max_tokens, temperature=temperature)
            success = True
        except (RateLimitError, ServiceUnavailableError):
            sleep(3)

    return resp


@st.cache(suppress_st_warning=True)
def openai_prompt(prompt, max_tokens=500, temperature=0.3):
    return _openai_prompt(prompt, max_tokens=max_tokens, temperature=temperature)


@st.cache(suppress_st_warning=True)
def openai_command(text, command, max_tokens=500, temperature=0.3):
  command += "\n"
  return _openai_prompt(command+text, max_tokens=max_tokens, temperature=temperature)
