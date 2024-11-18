import os
import requests
import json
import base64
import logging
import argparse
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def fetch_github_repos(username, auth_token=None):
    """
    Fetch public and private repositories for the authenticated user.
    If no auth token is provided, only public repositories are fetched.

    :param username: The GitHub username to fetch repositories for.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A dictionary representing GitHub repositories for the user.
    """
    repos = []
    page = 1
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}

    # Use /user/repos for authenticated requests to fetch private repos, otherwise /users/{username}/repos
    url = "https://api.github.com/user/repos" if auth_token else f"https://api.github.com/users/{username}/repos"

    while True:
        resp = requests.get(url,
                            params={'page': page, 'per_page': 10},
                            headers=headers)
        # Check response status
        if resp.status_code == 200:
            cur_repos = resp.json()
            if not cur_repos:
                break  # Exit when there are no more repos
            for repo in cur_repos:
                repos.append(repo)
            page += 1
        else:
            logging.error(f"Error fetching repos: {resp.status_code}")
            logging.error(f"Response: {resp.json()}")
            break

    return repos

def fetch_extra_repo_metadata(username, repo_name, auth_token=None):
    """
    Fetch additional metadata for a repository, i.e., contributors and README.
    
    :param username: GitHub username of the repository owner.
    :param repo_name: Name of the repository.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A dictionary with additional metadata.
    """
    metadata = {}
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}

    # Fetch contributors
    contr_url = f"https://api.github.com/repos/{username}/{repo_name}/contributors"
    contr_resp = requests.get(contr_url, headers=headers)
    if contr_resp.status_code == 200:
        metadata["contributors"] = [{"name": c['login'], "commits": c['contributions']} for c in contributors_response.json()]

    # Fetch README content
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    readme_resp = requests.get(readme_url, headers=headers)
    if readme_resp.status_code == 200:
        readme_data = readme_resp.json()
        metadata["readme_content"] = base64.b64decode(readme_data['content']).decode('utf-8')

    # Check if GitHub Pages exists
    pages_url = f"https://{username}.github.io/{repo_name}/"
    pages_resp = requests.get(pages_url)
    if pages_resp.status_code == 200:
        metadata["github_pages"] = pages_url

    # Check for images in the root directory
    content_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/"
    content_resp = requests.get(content_url, headers=headers)
    if content_resp.status_code == 200:
        content_data = content_resp.json()
        images = [f["name"] for f in content_data if f["type"] == "file" and
                  f["name"].endswith((".png", ".jpg", ".jpeg", ".gif"))]
        metadata["images"] = images

    return metadata

def fetch_extra_metadata(username, repos, auth_token=None):
    """
    Fetch extra metadata for retrieved repositories.
    
    :param username: The GitHub username whose repositories will be fetched.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A dictionary representing GitHub repositories with additional
             metadata for the user.
    """
    repos_data = []
    n = len(repos)
    k = 0
    for repo in repos:
        k += 1
        logging.info(f"Fetching extra metadata for {username}/{repo['name']} ({k}/{n})")
        repo_metadata = fetch_extra_repo_metadata(
            username, repo['name'], auth_token=auth_token)
        repo.update(repo_metadata)
        repos_data.append(repo)

    return repos_data

def main():
    parser = argparse.ArgumentParser(
        description="Generate detailed GitHub repository JSON data.")
    parser.add_argument("username",
                        type=str,
                        help="GitHub username to retrieve repositories for")
    parser.add_argument("--auth-token",
                        type=str,
                        help="GitHub personal access token for accessing private repositories")
    parser.add_argument("--extra-metadata",
                        action="store_true",
                        help="Fetch extra metadata for each retrieve repository",
                        default=False)

    args = parser.parse_args()

    repos = fetch_github_repos(username=args.username, auth_token=args.auth_token)
    if args.extra_metadata:
        repos = fetch_extra_metadata(username=args.username, repos=repos, auth_token=args.auth_token)
    print(json.dumps(repos, indent=4))

if __name__ == "__main__":
    main()
