import os
import requests
import json
import base64
import logging
import argparse
from typing import List, Dict, Optional

# Constants
BASE_API_URL = "https://api.github.com"
GITHUB_IO_URL = "{username}.github.io"
PER_PAGE = 10

logger = logging.getLogger(__name__)

def set_logging_level(quiet: bool, verbose: bool):
    if quiet:
        logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    elif verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _paginate_github_api(
    session: requests.Session,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, str] = None,
    per_page: int = PER_PAGE
) -> List[Dict]:
    """
    Helper function to paginate through GitHub API responses.
    """
    results = []
    page = 1
    if params is None:
        params = {}
    while True:
        current_params = params.copy()
        current_params.update({'page': page, 'per_page': per_page})
        resp = session.get(url, headers=headers, params=current_params)
        if resp.status_code != 200:
            logger.error(f"Failed to fetch results from {url}, status: {resp.status_code}")
            logger.error(f"Response: {resp.text}")
            break

        data = resp.json()
        if not data:
            break  # no more pages
        results.extend(data)
        page += 1

    return results


def fetch_github_repos(
    username: str,
    auth_token: Optional[str] = None,
    fetch_public: bool = True,
    fetch_private: bool = False
) -> List[Dict]:
    """
    Fetch public and/or private repositories from GitHub.
    """
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}
    repos = []

    with requests.Session() as session:
        # Fetch public repos
        if fetch_public:
            logger.info(f"Fetching public repositories for user '{username}'...")
            public_url = f"{BASE_API_URL}/users/{username}/repos"
            public_repos = _paginate_github_api(session, public_url, headers, params={'type': 'public'})
            repos.extend(public_repos)

        # Fetch private repos
        if fetch_private:
            if not auth_token:
                logger.warning("No auth token provided. Unable to fetch private repositories. Skipping private repos.")
            else:
                logger.info(f"Fetching private repositories for user '{username}'...")
                private_url = f"{BASE_API_URL}/user/repos"
                private_repos = _paginate_github_api(session, private_url, headers, params={'visibility': 'private'})
                repos.extend(private_repos)

    if not repos:
        logger.warning(f"No repositories found for user '{username}' with the given options.")

    # Deduplicate by full_name
    unique_repos = {r['full_name']: r for r in repos}.values()
    return list(unique_repos)


def fetch_extra_repo_metadata(
    username: str,
    repo_name: str,
    auth_token: Optional[str] = None
) -> Dict:
    """
    Fetch additional metadata for a repository.
    """
    metadata = {}
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}

    with requests.Session() as session:
        # Contributors
        contr_url = f"{BASE_API_URL}/repos/{username}/{repo_name}/contributors"
        contributors_resp = session.get(contr_url, headers=headers)
        if contributors_resp.status_code == 200:
            contributors_data = contributors_resp.json()
            metadata["contributors"] = [
                {"name": c.get('login'), "commits": c.get('contributions')}
                for c in contributors_data
            ]

        # README
        readme_url = f"{BASE_API_URL}/repos/{username}/{repo_name}/readme"
        readme_resp = session.get(readme_url, headers=headers)
        if readme_resp.status_code == 200:
            try:
                readme_data = readme_resp.json()
                metadata["readme_content"] = base64.b64decode(readme_data['content']).decode('utf-8', errors='replace')
            except (KeyError, base64.binascii.Error) as e:
                logger.warning(f"Error decoding README for {username}/{repo_name}: {e}")

        # GitHub Pages
        pages_url = f"https://{GITHUB_IO_URL.format(username=username)}/{repo_name}/"
        pages_resp = session.get(pages_url)
        if pages_resp.status_code == 200:
            metadata["github_pages"] = pages_url

        # Images in root
        content_url = f"{BASE_API_URL}/repos/{username}/{repo_name}/contents/"
        content_resp = session.get(content_url, headers=headers)
        if content_resp.status_code == 200:
            content_data = content_resp.json()
            images = [
                f["name"] for f in content_data
                if f.get("type") == "file" and f["name"].lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
            ]
            if images:
                metadata["images"] = images

    return metadata


def fetch_extra_metadata(username: str, repos: List[Dict], auth_token: Optional[str] = None) -> List[Dict]:
    """
    Fetch and attach extra metadata to each repository.
    """
    total = len(repos)
    for i, repo in enumerate(repos, start=1):
        repo_name = repo.get('name')
        if not repo_name:
            logger.warning(f"Repository missing 'name': {repo}")
            continue
        logger.info(f"Fetching extra metadata for {username}/{repo_name} ({i}/{total})")
        repo_metadata = fetch_extra_repo_metadata(username, repo_name, auth_token=auth_token)
        repo.update(repo_metadata)
    return repos


def filter_repos(repos: List[Dict], filter_str: Optional[str]) -> List[Dict]:
    """
    Filter repositories by name containing a given substring (case-insensitive).
    """
    if not filter_str:
        return repos
    filter_str_lower = filter_str.lower()
    filtered = [r for r in repos if filter_str_lower in r.get('name', '').lower()]
    return filtered


def sort_repos(repos: List[Dict], sort_key: Optional[str]) -> List[Dict]:
    """
    Sort repositories by a specified key if available.
    """
    if not sort_key:
        return repos
    return sorted(repos, key=lambda r: r.get(sort_key, ''))


def main():
    parser = argparse.ArgumentParser(description="Generate detailed GitHub repository JSON data.")
    parser.add_argument("username", type=str, help="GitHub username to retrieve repositories for")
    parser.add_argument("--auth-token", type=str, help="Personal access token for private repositories")
    parser.add_argument("--extra-metadata", action="store_true", default=False, help="Fetch extra metadata")
    parser.add_argument("--no-public", action="store_true", default=False, help="Disable public repo fetching")
    parser.add_argument("--private", action="store_true", default=False, help="Fetch private repositories (needs auth-token)")
    parser.add_argument("--input-file", type=str, help="Path to JSON file containing repository data from a previous run")
    parser.add_argument("--output-file", type=str, help="Path to write the final JSON output to (defaults to stdout)")
    parser.add_argument("--filter", type=str, help="Filter repositories by substring in name")
    parser.add_argument("--sort-by", type=str, help="Sort repositories by a given field (e.g., name, stargazers_count)")
    parser.add_argument("--quiet", action="store_true", default=False, help="Suppress informational logs")
    parser.add_argument("--verbose", action="store_true", default=False, help="Show debug-level logs")

    args = parser.parse_args()

    set_logging_level(quiet=args.quiet, verbose=args.verbose)

    fetch_public = not args.no_public
    fetch_private = args.private

    # Determine data source
    if args.input_file:
        # Load repos from file
        logger.debug(f"Loading repository data from {args.input_file}")
        with open(args.input_file, 'r') as f:
            repos = json.load(f)
        logger.info(f"Loaded {len(repos)} repositories from file.")
    else:
        # Fetch from GitHub
        repos = fetch_github_repos(
            username=args.username,
            auth_token=args.auth_token,
            fetch_public=fetch_public,
            fetch_private=fetch_private
        )

    # Apply filtering
    if args.filter:
        original_count = len(repos)
        repos = filter_repos(repos, args.filter)
        logger.info(f"Filtered repositories by '{args.filter}', {len(repos)} remain out of {original_count}.")

    # If extra-metadata is requested, fetch it (requires hitting GitHub if not already done)
    if args.extra_metadata and repos:
        repos = fetch_extra_metadata(username=args.username, repos=repos, auth_token=args.auth_token)

    # Sorting
    if args.sort_by:
        repos = sort_repos(repos, args.sort_by)
        logger.info(f"Sorted repositories by '{args.sort_by}'.")

    # Output
    output_data = json.dumps(repos, indent=4)
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output_data)
        logger.info(f"Written final JSON output to {args.output_file}")
    else:
        print(output_data)


if __name__ == "__main__":
    main()
