
import os
import requests
import json
import base64
import logging
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_headers(auth_token=None):
    """
    Return headers for GitHub API requests, including auth token if provided.
    
    :param auth_token: GitHub personal access token (optional).
    :return: A dictionary containing headers.
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if auth_token:
        headers["Authorization"] = f"token {auth_token}"
    return headers

def fetch_github_repos(username, auth_token=None):
    """
    Fetch public and private repositories for the authenticated user.
    If no auth token is provided, only public repositories are fetched.

    :param username: The GitHub username to fetch repositories for.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A list of dictionaries representing GitHub repositories for the user.
    """
    repos = []
    page = 1
    headers = get_headers(auth_token)

    # Use /user/repos for authenticated requests to fetch private repos, otherwise /users/{username}/repos
    url = "https://api.github.com/user/repos" if auth_token else f"https://api.github.com/users/{username}/repos"

    while True:
        resp = requests.get(url, params={'page': page, 'per_page': 10}, headers=headers)
        if resp.status_code == 200:
            cur_repos = resp.json()
            if not cur_repos:
                break  # Exit when there are no more repos
            repos.extend(cur_repos)
            page += 1
        else:
            logging.error(f"Error fetching repos: {resp.status_code}")
            logging.error(f"Response: {resp.json()}")
            break

    return repos

def fetch_extra_repo_metadata(username, repo_name, auth_token=None):
    """
    Fetch additional metadata for a repository, including contributors, README, and images.
    
    :param username: GitHub username of the repository owner.
    :param repo_name: Name of the repository.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A dictionary with additional metadata.
    """
    metadata = {}
    headers = get_headers(auth_token)

    # Fetch contributors
    contr_url = f"https://api.github.com/repos/{username}/{repo_name}/contributors"
    contr_resp = requests.get(contr_url, headers=headers)
    if contr_resp.status_code == 200:
        metadata["contributors"] = [{"name": c['login'], "commits": c['contributions']} for c in contr_resp.json()]
    else:
        logging.warning(f"Failed to fetch contributors for {repo_name}: {contr_resp.status_code}")

    # Fetch README content
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    readme_resp = requests.get(readme_url, headers=headers)
    if readme_resp.status_code == 200:
        readme_data = readme_resp.json()
        try:
            metadata["readme_content"] = base64.urlsafe_b64decode(readme_data['content']).decode('utf-8')
        except Exception as e:
            logging.error(f"Error decoding README for {repo_name}: {e}")
    else:
        logging.warning(f"Failed to fetch README for {repo_name}: {readme_resp.status_code}")

    # Fetch images and identify the canonical image (e.g., logo)
    image_urls = fetch_images(username, repo_name, headers)
    if image_urls:
        metadata['images'] = image_urls
        canonical_image = find_canonical_image(image_urls)
        metadata['canonical_image'] = canonical_image

    return metadata

def fetch_images(username, repo_name, headers):
    """
    Fetch all image files from the root directory of the repository.
    
    :param username: GitHub username of the repository owner.
    :param repo_name: Name of the repository.
    :param headers: Headers with authentication token, if available.
    :return: A list of image URLs found in the repository.
    """
    content_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/"
    content_resp = requests.get(content_url, headers=headers)
    image_urls = []

    if content_resp.status_code == 200:
        content_data = content_resp.json()
        # Look for image files
        for file in content_data:
            if file["type"] == "file" and file["name"].endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_urls.append(file["download_url"])
    else:
        logging.warning(f"Failed to fetch repository contents for {repo_name}: {content_resp.status_code}")

    return image_urls

def find_canonical_image(image_urls):
    """
    Identify a canonical image from the list, prioritizing logos and banners.
    
    :param image_urls: List of image URLs from the repository.
    :return: The URL of the most likely canonical image, or None if none found.
    """
    for image_url in image_urls:
        if any(keyword in image_url.lower() for keyword in ["logo", "banner"]):
            return image_url
    # Fallback: return the first image if no canonical image is found
    return image_urls[0] if image_urls else None

def fetch_extra_metadata(username, repos, auth_token=None):
    """
    Fetch extra metadata for retrieved repositories.
    
    :param username: The GitHub username whose repositories will be fetched.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :return: A list of dictionaries representing GitHub repositories with additional metadata for the user.
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
    parser = argparse.ArgumentParser(description="Generate detailed GitHub repository JSON data.")
    parser.add_argument("username", type=str, help="GitHub username to retrieve repositories for")
    parser.add_argument("--auth-token", type=str, help="GitHub personal access token for accessing private repositories")
    parser.add_argument("--extra-metadata", action="store_true", help="Fetch extra metadata for each retrieve repository", default=False)

    args = parser.parse_args()

    # Check for auth token in environment variable if not provided as argument
    auth_token = args.auth_token or os.getenv('GITHUB_TOKEN')

    # Fetch repositories
    repos = fetch_github_repos(username=args.username, auth_token=auth_token)
    
    # Optionally fetch extra metadata
    if args.extra_metadata:
        repos = fetch_extra_metadata(username=args.username, repos=repos, auth_token=auth_token)

    # Output the result
    print(json.dumps(repos, indent=4))

if __name__ == "__main__":
    main()