import os
import requests
import base64
import logging
from typing import List, Dict, Optional

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

def filter_repos(repos: List[Dict], filter_str: Optional[str]) -> List[Dict]:
    """
    Filter repositories by name containing a given substring (case-insensitive).
    """
    if not filter_str:
        return repos
    filter_str_lower = filter_str.lower()
    return [r for r in repos if filter_str_lower in r.get('name', '').lower()]

def sort_repos(repos: List[Dict], sort_key: Optional[str]) -> List[Dict]:
    """
    Sort repositories by a specified key if available.
    """
    if not sort_key:
        return repos
    return sorted(repos, key=lambda r: r.get(sort_key, ''))
