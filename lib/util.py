import json


def load_creds():
    with open("/home/streamlit-apps/creds.json", "r") as f:
        return json.loads(f.read())
