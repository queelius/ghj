# gh_hugo_toolkit/streamlit_app/app.py

import streamlit as st
import pandas as pd
import json

# Set page configuration
st.set_page_config(
    page_title="GitHub Repositories Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Function to load JSON data
@st.cache_data
def load_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

# Function to convert JSON to DataFrame
def json_to_df(data):
    return pd.json_normalize(data)

# Sidebar - Upload JSON File
st.sidebar.title("Configuration")
json_file = st.sidebar.file_uploader("Upload GitHub Repositories JSON", type=["json"])

if not json_file:
    st.sidebar.warning("Please upload a JSON file to proceed.")
    st.stop()

data = load_json(json_file)
df = json_to_df(data)

# Sidebar - Search Input
st.sidebar.header("Search")
search_query = st.sidebar.text_input("Search Repositories", "")

# Apply Search Query
if search_query:
    st.sidebar.info(f"Searching for: '{search_query}'")
    filtered_df = df[
        df['name'].str.contains(search_query, case=False, na=False) |
        df['description'].str.contains(search_query, case=False, na=False) |
        df['languages'].apply(lambda x: search_query.lower() in str(x).lower())
    ]
else:
    filtered_df = df

# Main Title
st.title("GitHub Repositories Dashboard")

# Display Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Repositories", len(filtered_df))
col2.metric("Total Stars", int(filtered_df['stargazers_count'].sum()))
col3.metric("Total Forks", int(filtered_df['forks_count'].sum()))

st.markdown("---")

# DataTable
st.subheader("Repositories Overview")
st.dataframe(filtered_df[['name', 'description', 'stargazers_count', 'forks_count', 'html_url']].rename(
    columns={
        'name': 'Name',
        'description': 'Description',
        'stargazers_count': 'Stars',
        'forks_count': 'Forks',
        'html_url': 'URL'
    }
))

# Repository Links
st.markdown("---")
st.subheader("Repository Links")
for index, row in filtered_df.iterrows():
    st.markdown(f"- [{row['name']}]({row['html_url']}) - ⭐ {row['stargazers_count']} | Forks: {row['forks_count']}")

