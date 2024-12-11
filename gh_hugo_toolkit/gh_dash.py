import streamlit as st
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime

def display_key_value_table(data_dict, title, columns_per_row=3):
    """
    Display key-value pairs in a table with a specified number of columns per row.

    Args:
        data_dict (dict): Dictionary containing key-value pairs to display.
        title (str): Title of the table section.
        columns_per_row (int): Number of columns per row in the table.
    """
    st.subheader(title)
    items = list(data_dict.items())
    # Split items into chunks based on columns_per_row
    for i in range(0, len(items), columns_per_row):
        chunk = items[i:i + columns_per_row]
        cols = st.columns(columns_per_row)
        for col, (key, value) in zip(cols, chunk):
            col.markdown(f"**{key}**: {value}")
    #st.markdown("---")  # Add a horizontal line for separation

def show_repo(repo):
    # Header with repository name, homepage, and GitHub link
    header = f"### {repo.get('name', 'Unnamed Repository')}"
    homepage = repo.get('homepage')
    github_link = repo.get('html_url')
    
    if homepage:
        header += f" 🏠 [Docs]({homepage})"
    if github_link:
        header += f" 📦 [GitHub]({github_link})"
    
    st.markdown(header)
    
    # Description
    st.markdown(repo.get('description', 'No description provided.'))
    
    # Repository Stats
    stats = {
        "⭐ Stars": repo.get('stargazers_count', 0),
        "🍴 Forks": repo.get('forks_count', 0),
        "🐛 Open Issues": repo.get('open_issues_count', 0),
        "👀 Watchers": repo.get('watchers_count', 0),
        "🗣️ Contributors": len(repo.get('contributors', [])),
        "🔽 Size": repo.get('size', 0),
    }

    lic = repo.get('license')
    if lic:
        lic = lic.get('name', 'Unknown')

    # Additional Attributes
    attributes = {
        "🗣️ Language": repo.get('language', 'Unknown'),
        "🔒 Visibility": repo.get('visibility', 'Unknown'),
        "🔑 Fork": "Yes" if repo.get('fork') else "No",
        "📦 Archived": "Yes" if repo.get('archived') else "No",
        "📅 Created": parser.parse(repo.get('created_at', '')).strftime("%d %B %Y"),
        "🔄 Last Push": parser.parse(repo.get('pushed_at', '')).strftime("%d %B %Y"),
        "📝 License": lic,
        "👤 Owner": repo.get('owner', {}).get('login', 'Unknown')
    }

    # Display Repository Stats with 3 columns per row
    display_key_value_table(stats, "📊 Repository Stats", columns_per_row=3)
    
    # Display Additional Information with 3 columns per row
    display_key_value_table(attributes, "ℹ️ Information", columns_per_row=3)

    # Expandable JSON Details
    with st.expander("🔍 View Repository Details"):
        st.json(repo)

    st.markdown(repo.get('readme_content', 'No README content available.'))

def main():
    def load_json(uploaded_file):
        if uploaded_file is not None:
            try:
                # Decode the uploaded file and load it as JSON
                return json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON file!")
                return None
        else:
            st.error("No file uploaded!")
            return None

    st.set_page_config(layout="wide")  # Make the window wider
    st.title('📊 GitHub Repo JSON Dashboard')

    # File uploader
    json_file = st.file_uploader("📁 Upload your JSON file", type=["json"])

    # Load JSON data if a file is uploaded
    if json_file is not None:
        repos = load_json(json_file)

        if repos is not None:
            # Ensure repos is a list
            if isinstance(repos, dict):
                repos = [repos]

            # Layout with two columns
            col1, col2 = st.columns([1, 3])

            with col1:
                # Search and filter
                st.subheader("🔍 Search & Filter")
                search_query = st.text_input("Search repositories:").lower()

                # Filter feature by field
                field_options = ['name', 'stargazers_count', 'forks_count', 'language']
                selected_field = st.selectbox("Filter by field:", field_options)
                field_value = st.text_input(f"Enter value for {selected_field}:").lower()

                # Filter repositories based on search query and field value

                def matcher(repo, search_query):
                    for key, value in repo.items():
                        if search_query in str(value).lower():
                            return True
                    return False

                filtered_repos = [
                    repo for repo in repos if matcher(repo, search_query) and
                       (str(repo.get(selected_field, '')).lower() == field_value if field_value else True)
                ]

                if not filtered_repos:
                    st.warning("No repositories match the filter criteria.")
                else:
                    # Sort repos by stargazers_count descending, then by pushed_at descending
                    def sort_date_key(repo):
                        pushed_at_str = repo.get('pushed_at', '1970-01-01T00:00:00Z')
                        try:
                            pushed_at_dt = parser.isoparse(pushed_at_str)
                        except Exception:
                            pushed_at_dt = datetime(1970, 1, 1)
                        # To sort pushed_at descending, use timestamp multiplied by -1
                        return -pushed_at_dt.timestamp()

                    def sort_star_key(repo):
                        return repo.get('stargazers_count', 0)

                    filtered_repos = sorted(filtered_repos, key=sort_date_key)

                    # Display list of filtered repositories as clickable items
                    st.write("### 🔗 Matching Repositories")
                    for repo in filtered_repos:
                        repo_name = repo.get('name', 'Unnamed Repository')
                        if st.button(repo_name):
                            st.session_state['selected_repo'] = repo_name

            with col2:
                # Display selected repository details
                selected_repo_name = st.session_state.get('selected_repo')
                if selected_repo_name:
                    selected_repo = next(
                        (repo for repo in filtered_repos if repo.get('name') == selected_repo_name), 
                        None
                    )
                    if selected_repo:
                        show_repo(selected_repo)
                else:
                    st.info("Select a repository from the left to view details.")
    else:
        st.info("📥 Please upload a JSON file to proceed.")

if __name__ == "__main__":
    main()
