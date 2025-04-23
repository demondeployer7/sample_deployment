import streamlit as st
import pandas as pd
import base64
import requests

# Constants
REPO_OWNER = "demondeployer7"
REPO_NAME = "sample_deployment"
FILE_PATH = "data.csv"
GITHUB_TOKEN = st.secrets["github_token"]

API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

def get_file_from_github():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        content = response.json()
        decoded = base64.b64decode(content["content"]).decode("utf-8")
        sha = content["sha"]
        return decoded, sha
    else:
        st.error(f"❌ Failed to fetch file from GitHub (Status Code: {response.status_code})")
        try:
            error_message = response.json().get("message", "No message in response")
            st.text(f"GitHub Error: {error_message}")
        except Exception as e:
            st.text(f"Could not parse GitHub response. Raw response:\n{response.text}")
        return None, None


def update_file_on_github(updated_csv, sha):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    content = base64.b64encode(updated_csv.encode("utf-8")).decode("utf-8")
    message = "Appended new entry via Streamlit"
    data = {
        "message": message,
        "content": content,
        "sha": sha
    }
    response = requests.put(API_URL, headers=headers, json=data)
    return response.status_code == 200

# UI
st.title("Student Entry Form")

name = st.text_input("Enter your name:")
roll_no = st.text_input("Enter your roll number:")

if st.button("Submit"):
    if name and roll_no:
        with st.spinner("Saving to GitHub..."):
            content, sha = get_file_from_github()
            if content:
                df = pd.read_csv(pd.compat.StringIO(content))
                new_entry = pd.DataFrame({"name": [name], "roll_no": [roll_no]})
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                csv_str = updated_df.to_csv(index=False)

                if update_file_on_github(csv_str, sha):
                    st.success("Entry added successfully!")
                else:
                    st.error("Failed to update the file on GitHub.")
    else:
        st.warning("Please fill out both fields.")
