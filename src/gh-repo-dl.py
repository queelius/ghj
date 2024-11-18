
import os
import requests
import yaml
import argparse
import base64

# Constants
PROJECTS_DIR = "ghprojects"  # Change this to the path of your Hugo projects directory

def fetch_github_repos(username):
    """
    Fetch all repositories for the given GitHub username.

    This function will fetch all repositories, paginating through the results
    until all repositories are fetched.

    :param username: GitHub username to fetch repositories for
    :return: List of repositories (dictionaries) for the given username
    """
    repos = []
    page = 1
    while True:
        response = requests.get(f"https://api.github.com/users/{username}/repos", params={'page': page, 'per_page': 10})
        if response.status_code == 200:
            current_repos = response.json()
            if not current_repos:
                break  # Exit when there are no more repos
            repos.extend(current_repos)
            page += 1
        else:
            print(f"Error fetching repos: {response.status_code}")
            print(response.json())
            break
    return repos

def fetch_readme(username, repo_name):
    """
    Fetch the README.md file for the given repository

    :param username: GitHub username of the repository owner
    :param repo_name: Name of the repository
    :return: Content of the README.md file as a string
    """
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    response = requests.get(url)
    
    if response.status_code == 200:
        readme_data = response.json()
        # The content is base64 encoded, so we decode it
        return base64.b64decode(readme_data['content']).decode('utf-8')
    else:
        return None

def fetch_languages(username, repo_name):
    """Fetch the languages used in the repository"""
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    response = requests.get(url)
    if response.status_code == 200:
        return list(response.json().keys())
    else:
        return []

def detect_github_pages(username, repo_name):
    """Check if GitHub Pages exists for the repository"""
    pages_url = f"https://{username}.github.io/{repo_name}/"
    # A simple request to check if the page exists
    response = requests.get(pages_url)
    if response.status_code == 200:
        return pages_url
    return None

def check_docs_folder(username, repo_name):
    """
    Check if the repository has a docs/ folder

    :param username: GitHub username of the repository owner
    :param repo_name: Name of the repository
    """
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/docs"
    response = requests.get(url)
    if response.status_code == 200:
        return f"https://github.com/{username}/{repo_name}/tree/main/docs"
    return None

def create_project_item(repo, username,
                        author,
                        email,
                        layout):
    """
    Create a project markdown file for the given repository

    :param repo: Repository dictionary
    :param username: GitHub username of the repository owner
    :param author: Author name to add to the project front matter
    :param email: Email to add to the project front matter
    :param layout: Layout to add to the project front matter
    """
    # Create a folder for each project if not exists
    project_slug = repo['name'].lower().replace(" ", "-")
    project_path = os.path.join(PROJECTS_DIR, project_slug)
    os.makedirs(project_path, exist_ok=True)

    # Fetch the README.md
    readme_content = fetch_readme(username, repo['name'])
    
    # Fetch languages used
    languages = fetch_languages(username, repo['name'])

    # Check for GitHub Pages
    github_pages_url = detect_github_pages(username, repo['name'])
    
    # YAML front matter for Hugo
    project_data = {
        "title": repo['name'],
        "date": repo['created_at'],
        "description": repo['description'] or "No description available.",
        "links": [
            {"name": "GitHub", "url": repo['html_url']}
        ],
        "stars": repo['stargazers_count'],
        "forks": repo['forks_count'],
        "open_issues": repo['open_issues_count'],
        "tags": ["GitHub", "GitHub Project"]
    }

    if author:
        project_data["author"] = author

    if layout:
        project_data["layout"] = layout

    if email:
        project_data["email"] = email

    if github_pages_url:
        project_data["links"].append({"name": "GitHub Pages", "url": github_pages_url})

    if languages:
        project_data["languages"] = languages

    # Write the markdown file for Hugo
    project_file = os.path.join(project_path, "index.md")
    with open(project_file, "w") as f:
        f.write("---\n")
        yaml.dump(project_data, f, default_flow_style=False)
        f.write("---\n\n")
        
        f.write(f"# {repo['name']}\n")
        f.write(f"{repo['description'] or 'No description available.'}\n")
        f.write(f"\n[GitHub Link]({repo['html_url']})\n")

        f.write(f"\n**Stars**: {repo['stargazers_count']} | **Forks**: {repo['forks_count']} | **Open Issues**: {repo['open_issues_count']}\n")
        if languages:
            f.write(f"\n**Languages Used**: {', '.join(languages)}\n")
        
        # Add GitHub Pages link if available
        if github_pages_url:
            f.write(f"\n[GitHub Pages]({github_pages_url})\n")
        
        if readme_content:
            f.write("\n## README\n")
            f.write(readme_content)
        else:
            f.write("\n_No README available for this project._\n")

def generate_projects(username,
                      author=None,
                      email=None,
                      layout=):
    repos = fetch_github_repos(username)
    for repo in repos:
        print(f"Generating project for {repo['name']}...")
        create_project_item(repo, username, author=author, layout=layout, email=email)
    print(f"Generated {len(repos)} project markdown files in {PROJECTS_DIR}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Generate Hugo project files from GitHub repositories.")
    parser.add_argument("username", type=str, help="GitHub username to retrieve repositories for")
    parser.add_argument("--author", type=str, help="Author name to add to the project front matter")
    parser.add_argument("--layout",
                        default="ghproject",
                        type=str,
                        help="Layout to add to the project front matter")
    parser.add_argument("--email", type=str, help="Email to add to the project front matter")
    parser.add_argument("--projects-dir", type=str,
                        default=PROJECTS_DIR,
                        help="Directory to save the project files in")
    # for rate limiting, let's only retrieve by default 100 repos
    parser.add_argument("--max-repos", type=int, default=100,
                        help="Maximum number of repositories to retrieve")
    
    # for getting only repos that are above a certain number of stars
    parser.add_argument("--min-stars", type=int, default=0,
                        help="Minimum number of stars for a repository to be included")
    
    # for retrieving an image filename in the repo to add for the project
    parser.add_argument("--image-file", type=str, default=None,
                        help="Image filename to add to the project front matter")
    
    # Parse arguments
    args = parser.parse_args()

    # Generate projects for the given username
    generate_projects(args.username, author=args.author, email=args.email, layout=args.layout)