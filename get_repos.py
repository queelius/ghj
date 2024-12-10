import os
import requests
import json
import base64
import logging
import argparse
import yaml

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

def fetch_github_repos(username, auth_token=None, private=False):
    """
    Fetch public (and private if set to True) repositories for the authenticated
    user. If no auth token is provided, only public repositories are fetched.

    :param username: The GitHub username to fetch repositories for.
    :param auth_token: Personal access token for authenticating GitHub requests.
    :param private: Boolean indicating whether to fetch private repositories.
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
            if not private:
                cur_repos = [repo for repo in cur_repos if not repo['private']]
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

def write_hugo_project(repos, base_dir="content/ghprojects"):
    os.makedirs(base_dir, exist_ok=True)

    for repo in repos:
        repo_dir = os.path.join(base_dir, repo['name'])
        os.makedirs(repo_dir, exist_ok=True)
        
        frontmatter = {
            'title': repo['name'],
            'description': repo.get('description', ''),
            'date': repo['created_at'],
            'layout': 'ghproject',
            'tags': ['GitHub', 'project'],
            'languages': list(repo.get('languages', {}).keys()),
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'open_issues': repo.get('open_issues_count', 0),
            'links': [
                {'name': 'GitHub', 'url': repo['html_url']},
            ]
        }

        # Add GitHub Pages link if available
        if repo.get('has_pages', False):
            frontmatter['links'].append({
                'name': 'GitHub Pages',
                'url': f"https://{repo['owner']['login']}.github.io/{repo['name']}/"
            })

        # Write index.md
        with open(os.path.join(repo_dir, "index.md"), "w") as f:
            # Write frontmatter
            f.write("---\n")
            f.write(yaml.dump(frontmatter, default_flow_style=False))
            f.write("---\n")
            
            # Write content
            f.write(f"# {repo['name']}\n")
            if repo.get('description'):
                f.write(f"{repo['description']}\n")
            
            # Add readme if available
            if 'readme_content' in repo:
                f.write("\n## README\n")
                f.write(repo['readme_content'])

# Update main() to use this:
    if args.output_type == "project":
        write_hugo_project(repos)

def main():
    parser = argparse.ArgumentParser(description="Generate detailed GitHub repository JSON data.")
    parser.add_argument("username", type=str, help="GitHub username to retrieve repositories for")
    parser.add_argument("--auth-token", type=str, help="GitHub personal access token for accessing private repositories. Defaults to GITHUB_TOKEN environment variable.")
    parser.add_argument("--extra-metadata", action="store_true", help="Fetch extra metadata for each retrieve repository", default=False)
    parser.add_argument("--output-type", type=str, help="Output type for the result (json or project folder)", default="json")

    args = parser.parse_args()

    # Check for auth token in environment variable if not provided as argument
    auth_token = args.auth_token or os.getenv('GITHUB_TOKEN')

    # Fetch repositories
    repos = fetch_github_repos(username=args.username, auth_token=auth_token)
    
    # Optionally fetch extra metadata
    if args.extra_metadata:
        repos = fetch_extra_metadata(username=args.username, repos=repos, auth_token=auth_token)

    if args.output_type == "project":
        # Create a directory for the project
        project_dir = f"{args.username}_repos"
        os.makedirs(project_dir, exist_ok=True)
        for repo in repos:
            repo_dir = os.path.join(project_dir, repo['name'])
            os.makedirs(repo_dir, exist_ok=True)
            with open(os.path.join(repo_dir, "metadata.json"), "w") as f:
                json.dump(repo, f, indent=4)
    else:
        print(json.dumps(repos, indent=2))

if __name__ == "__main__":
    main()
