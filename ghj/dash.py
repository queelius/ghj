# ghj/ghj_dash.py

import streamlit as st
import json
from rich.console import Console
from pathlib import Path
from typing import Dict, List, Union
from rich.console import Console
import subprocess

console = Console()

class DashboardApp:
    def __init__(self):
        st.set_page_config(layout="wide", page_title="GHJ Dashboard")
        self.setup_styles()

    def setup_styles(self):
        st.markdown("""
            <style>
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            </style>
            """, unsafe_allow_html=True)

    def load_json(self, file_path: Union[str, Path]) -> List[Dict]:
        try:
            with open(file_path) as f:
                data = json.load(f)
                return [data] if isinstance(data, dict) else data
        except json.JSONDecodeError:
            st.error("Invalid JSON file!")
            return []
        except FileNotFoundError:
            st.error(f"File not found: {file_path}")
            return []

    def display_stats(self, repos: List[Dict]):
        st.subheader("📈 Repository Statistics")
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Repositories", len(repos))
        col2.metric("Total Stars", total_stars)
        col3.metric("Total Forks", total_forks)

    def display_repo_details(self, repo: Dict):
        st.markdown(f"## {repo.get('name', 'Unnamed Repository')}")
        st.markdown(f"⭐ {repo.get('stargazers_count', 0)} | 🍴 {repo.get('forks_count', 0)}")
        
        if 'description' in repo and repo['description']:
            st.markdown(f"*{repo['description']}*")
            
        with st.expander("View Repository Details"):
            st.json(repo)
        
        if 'readme_content' in repo:
            st.markdown("### README")
            st.markdown(repo['readme_content'])

    def filter_repos(self, repos: List[Dict], search_query: str, field: str, value: str) -> List[Dict]:
        filtered = repos
        if search_query:
            filtered = [
                repo for repo in filtered
                if search_query.lower() in str(repo.get('name', '')).lower() or
                search_query.lower() in str(repo.get('description', '')).lower()
            ]
        if field and value:
            filtered = [
                repo for repo in filtered
                if str(repo.get(field, '')).lower() == value.lower()
            ]
        return filtered

    def run(self, json_path: str):
        st.title('📊 GitHub Repository Dashboard')

        repos = []
        if json_path:
            repos = self.load_json(json_path)
        else:
            # Show file upload widget
            uploaded_file = st.file_uploader(
                "Upload GitHub repository JSON file",
                type=['json'],
                help="Select a JSON file containing GitHub repository data"
            )
            
            if uploaded_file:
                try:
                    repos = json.loads(uploaded_file.getvalue())
                    if isinstance(repos, dict):
                        repos = [repos]
                    st.success("✅ File loaded successfully!")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file!")
                    return

        # Display overall statistics
        self.display_stats(repos)

        # Search and filter section
        col1, col2 = st.columns([1, 3])

        with col1:
            st.subheader("🔍 Search & Filter")
            search_query = st.text_input("Search repositories:").lower()
            
            # Filter controls
            field_options = ['name', 'language', 'stargazers_count', 'forks_count']
            selected_field = st.selectbox("Filter by field:", field_options)
            
            # Get unique values for selected field
            unique_values = set(str(repo.get(selected_field, '')) 
                              for repo in repos if repo.get(selected_field))
            if unique_values:
                filter_value = st.selectbox(
                    f"Select {selected_field}:",
                    sorted(unique_values)
                )
            else:
                filter_value = None

            # Sort options
            sort_by = st.selectbox(
                "Sort by:",
                ['stargazers_count', 'forks_count', 'name', 'updated_at']
            )
            sort_order = st.radio("Order:", ["Descending", "Ascending"])

        # Filter and sort repositories
        filtered_repos = self.filter_repos(repos, search_query, selected_field, filter_value)
        
        # Sort repositories
        filtered_repos.sort(
            key=lambda x: x.get(sort_by, ''),
            reverse=(sort_order == "Descending")
        )

        # Display repositories
        with col2:
            st.subheader(f"📚 Repositories ({len(filtered_repos)})")
            for repo in filtered_repos:
                self.display_repo_details(repo)

def launch_dashboard(json_path: str, port: int = 8501, host: str = 'localhost'):
    """Launch the Streamlit dashboard with the specified JSON file"""
    console.print(f"[green]Launching dashboard on {host}:{port}...")
    
    temp_script = """
import streamlit as st
from ghj.dash import DashboardApp
app = DashboardApp()
app.run('{json_path}')
    """.format(json_path=json_path or '')
    
    temp_file = Path("temp_dashboard.py")
    temp_file.write_text(temp_script)
    
    try:
        subprocess.run([
            "streamlit", "run",
            str(temp_file),
            "--server.port", str(port),
            "--server.address", host
        ])
    finally:
        temp_file.unlink()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        launch_dashboard(sys.argv[1])
    else:
        print("Please provide a JSON file path")