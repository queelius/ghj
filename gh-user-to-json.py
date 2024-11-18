import os
import requests
import json
import base64
import logging
import argparse
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def fetch_github_repos(username, max_repos=100, min_stars=0, auth_token=None):
    """
    Fetch all public and private repositories for a given GitHub username using an optional auth token for private repos.
    
    :param username: The GitHub username to fetch repositories for.
    :param max_repos: Maximum number of repositories to retrieve (default is 100).
    :param min_stars: Minimum number of stars a repository must have to be included (default is 0).
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A list of dictionaries representing GitHub repositories.
    """
    repos = []
    page = 1
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}

    while len(repos) < max_repos:
        response = requests.get(f"https://api.github.com/users/{username}/repos", 
                                params={'page': page, 'per_page': 10}, headers=headers)
        if response.status_code == 200:
            current_repos = response.json()
            if not current_repos:
                break  # Exit when there are no more repos
            for repo in current_repos:
                if repo['stargazers_count'] >= min_stars:
                    repos.append(repo)
                    if len(repos) >= max_repos:
                        break
            page += 1
        else:
            logging.error(f"Error fetching repos: {response.status_code}")
            break
    return repos[:max_repos]  # Limit to max_repos

def fetch_repo_metadata(username, repo_name, auth_token=None):
    """
    Fetch additional metadata for a repository including languages, contributors, README, and more.
    
    :param username: GitHub username of the repository owner.
    :param repo_name: Name of the repository.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A dictionary with additional metadata.
    """
    metadata = {}
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}

    # Fetch languages used
    languages_url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    languages_response = requests.get(languages_url, headers=headers)
    if languages_response.status_code == 200:
        metadata["languages"] = languages_response.json()

    # Fetch contributors
    contributors_url = f"https://api.github.com/repos/{username}/{repo_name}/contributors"
    contributors_response = requests.get(contributors_url, headers=headers)
    if contributors_response.status_code == 200:
        metadata["contributors"] = [{"name": c['login'], "commits": c['contributions']} for c in contributors_response.json()]

    # Fetch README content
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    readme_response = requests.get(readme_url, headers=headers)
    if readme_response.status_code == 200:
        readme_data = readme_response.json()
        metadata["readme_content"] = base64.b64decode(readme_data['content']).decode('utf-8')

    return metadata

def generate_json(username, max_repos=100, min_stars=0, whitelist=[], blacklist=[], regex_filter=None, whitelist_file=None, blacklist_file=None, auth_token=None):
    """
    Fetch GitHub repositories and save detailed JSON files for each one, applying whitelist, blacklist, and regex filters.
    
    :param username: The GitHub username whose repositories will be fetched.
    :param max_repos: The maximum number of repositories to retrieve (default is 100).
    :param min_stars: The minimum number of stars a repository must have to be included (default is 0).
    :param whitelist: List of whitelist patterns (can be regex).
    :param blacklist: List of blacklist patterns (can be regex).
    :param regex_filter: A regex pattern to filter repositories by name.
    :param whitelist_file: Path to file containing whitelist patterns.
    :param blacklist_file: Path to file containing blacklist patterns.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: None
    """
    repos = fetch_github_repos(username, max_repos=max_repos, min_stars=min_stars, auth_token=auth_token)

    # Apply whitelist (if any)
    if whitelist:
        repos = [repo for repo in repos if any(re.match(pattern, repo['name']) for pattern in whitelist)]
    
    # Apply blacklist (if any)
    if blacklist:
        repos = [repo for repo in repos if not any(re.match(pattern, repo['name']) for pattern in blacklist)]

    # Apply regex filter (if specified)
    if regex_filter:
        repos = apply_regex_filter(repos, regex_filter)

    all_repo_data = []
    for repo in repos:
        # Fetch additional metadata
        repo_metadata = fetch_repo_metadata(username, repo['name'], auth_token=auth_token)
        repo.update(repo_metadata)
        all_repo_data.append(repo)

    print(json.dumps(all_repo_data, indent=4))  # Output unified JSON

def load_patterns_from_file(pattern_file):
    """
    Load whitelist or blacklist patterns from a file, one per line.
    
    :param pattern_file: Path to the pattern file.
    :return: A list of patterns (strings).
    """
    with open(pattern_file, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def main():
    # Argument parsing for CLI interaction
    parser = argparse.ArgumentParser(description="Generate detailed GitHub repository JSON data.")
    parser.add_argument("username", type=str, help="GitHub username to retrieve repositories for")
    parser.add_argument("--max-repos", type=int, default=100, help="Maximum number of repositories to retrieve")
    parser.add_argument("--min-stars", type=int, default=0, help="Minimum number of stars for a repository to be included")
    parser.add_argument("--whitelist", type=str, nargs='*', help="Whitelist of repositories to include")
    parser.add_argument("--blacklist", type=str, nargs='*', help="Blacklist of repositories to exclude")
    parser.add_argument("--whitelist-file", type=str, help="File containing whitelist patterns")
    parser.add_argument("--blacklist-file", type=str, help="File containing blacklist patterns")
    parser.add_argument("--regex-filter", type=str, help="Regex pattern to filter repositories by name")
    parser.add_argument("--auth-token", type=str, help="GitHub personal access token for accessing private repositories")

    args = parser.parse_args()

    # Load whitelist/blacklist from files if specified
    whitelist = args.whitelist if args.whitelist else []
    blacklist = args.blacklist if args.blacklist else []

    if args.whitelist_file:
        whitelist += load_patterns_from_file(args.whitelist_file)
    
    if args.blacklist_file:
        blacklist += load_patterns_from_file(args.blacklist_file)

    # Generate the JSON with the given arguments
    generate_json(username=args.username, 
                  max_repos=args.max_repos, 
                  min_stars=args.min_stars, 
                  whitelist=whitelist, 
                  blacklist=blacklist,
                  regex_filter=args.regex_filter,
                  auth_token=args.auth_token)

if __name__ == "__main__":
    main()
