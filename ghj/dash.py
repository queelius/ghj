# ghj/ghj_dash.py

import streamlit as st
import json
from rich.console import Console
from pathlib import Path
from typing import Dict, List, Union
import subprocess
from jaf import jaf as jaf_filter_func, JafResultSet

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
        
        if 'readme' in repo:
            with st.expander("View Repository Readme"):
                st.markdown(repo['readme'])

    def filter_repos(self,
                     repos: List[Dict],
                     jaf_query_str: str) -> List[Dict]:
        if not jaf_query_str.strip():
            return repos # No query, return all repos

        try:
            query_ast = json.loads(jaf_query_str)
        except json.JSONDecodeError:
            st.error(f"Invalid JAF query: Not a valid JSON string. Query: '{jaf_query_str}'")
            return [] # Filter failed
        
        if not isinstance(query_ast, list):
            st.error(f"Invalid JAF query AST: Must be a list (S-expression). Query: '{jaf_query_str}'")
            return []


        try:
            result_set: JafResultSet = jaf_filter_func(
                repos,
                query_ast,
                collection_id="streamlit_dashboard_repos"
            )
            return [repos[i] for i in result_set.indices]
        except Exception as e:
            st.error(f"Error applying JAF filter: {e}")
            return [] # Filter failed

    def run(self, json_path: str):
        st.title('📊 GitHub Repository Dashboard')

        repos = []
        if json_path:
            repos = self.load_json(json_path)
        else:
            uploaded_file = st.file_uploader(
                "Upload GitHub repository JSON file",
                type=['json'],
                help="Select a JSON file containing GitHub repository data"
            )
            
            if uploaded_file:
                try:
                    repos_data = json.loads(uploaded_file.getvalue())
                    if isinstance(repos_data, dict):
                        repos = [repos_data]
                    elif isinstance(repos_data, list):
                        repos = repos_data
                    else:
                        st.error("❌ Invalid JSON structure in uploaded file.")
                        return
                    st.success("✅ File loaded successfully!")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file!")
                    return
                except Exception as e:
                    st.error(f"❌ Error processing file: {e}")
                    return

        if not repos:
            st.info("No repository data to display. Upload a JSON file or provide a path.")
            return

        self.display_stats(repos)

        col1, col2 = st.columns([1, 3])

        with col1:
            st.subheader("🔍 Filter with JAF")
            jaf_query_str = st.text_area(
                "JAF Query (JSON AST):",
                height=150,
                value='["exists?", ["path", [["key", "name"]]]]', # Default/example query
                help='Example: ["eq?", ["path", [["key", "language"]]], "Python"]'
            ).strip()
            
            st.subheader("📊 Sort Options")
            sort_by = st.selectbox(
                "Sort by:",
                ['stargazers_count', 'forks_count', 'name', 'updated_at', 'pushed_at', 'created_at']
            )
            sort_order = st.radio("Order:", ["Descending", "Ascending"])

        filtered_repos = self.filter_repos(repos, jaf_query_str)
        
        # Sort repositories
        filtered_repos.sort(
            key=lambda x: x.get(sort_by, 0 if 'count' in sort_by else ''), # Handle missing keys for sorting
            reverse=(sort_order == "Descending")
        )

        with col2:
            st.subheader(f"📚 Repositories ({len(filtered_repos)})")
            if filtered_repos:
                for repo in filtered_repos:
                    self.display_repo_details(repo)
            else:
                st.info("No repositories match the current filter criteria.")

def launch_dashboard(json_path: str, port: int = 8501, host: str = 'localhost'):
    """
    Launch the Streamlit dashboard with the specified JSON file

    Args:
        json_path (str): Path to the JSON file containing GitHub repository data
        port (int): Port number for the Streamlit server
        host (str): Host address for the Streamlit server
    """
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