import requests
from .utils import logger
from typing import List, Dict, Optional
import base64

PER_PAGE = 10
BASE_API_URL = "https://api.github.com"
GITHUB_IO_URL = "{username}.github.io"

def fetch_repos(repos: List[str],
                extra: bool,
                auth_token: Optional[str] = None) -> Dict:
    """
    Fetch repositories from GitHub API.
    """
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}
    results = []
    for repo in repos:
        url = f"{BASE_API_URL}/repos/{repo}"
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                results.append(resp.json())
            else:
                logger.debug(f"Failed to fetch repo {url}: {resp.status_code}")
                logger.debug(f"Response: {resp.text}")
        except Exception as e:
            logger.error(f"Error fetching repo {url}: {str(e)}")

    if extra:
        total = len(results)
        for i, repo in enumerate(results, start=1):
            repo_name = repo.get('name')
            username = repo.get('owner').get('login')
            if not repo_name:
                logger.warning(f"Repository missing 'name': {repo}")
                continue
            logger.debug(f"Fetching extra metadata for {username}/{repo_name} ({i}/{total})")
            metadata = fetch_extra(username, repo_name, auth_token=auth_token)
            repo.update(metadata)
    
    return results

def fetch_extra(
    username: str,
    repo_name: str,
    auth_token: Optional[str] = None
) -> Dict:
    """
    Fetch additional meta-data for a repository.
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
                logger.debug(f"Fetched README for {username}/{repo_name}")
            except (KeyError, base64.binascii.Error) as e:
                logger.warning(f"Error decoding README for {username}/{repo_name}: {e}")

        # GitHub Pages
        pages_url = f"https://{GITHUB_IO_URL.format(username=username)}/{repo_name}/"
        pages_resp = session.get(pages_url, headers=headers)
        if pages_resp.status_code == 200:
            logger.debug(f"Fetching GitHub Pages: {pages_url}")
            metadata["github_pages"] = pages_url

        # Images in root
        content_url = f"{BASE_API_URL}/repos/{username}/{repo_name}/contents/"
        content_resp = session.get(content_url, headers=headers)
        metadata["images"] = []
        if content_resp.status_code == 200:
            content_data = content_resp.json()
            images = [
                f["name"] for f in content_data
                if f.get("type") == "file" and f["name"].lower().endswith((
                    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"))
            ]
            if images:
                metadata["images"] = images
            else:
                logger.debug(f"No images found in the root directory of {username}/{repo_name}")
        else:
            logger.debug(f"Failed to fetch content for {username}/{repo_name}: {content_resp.status_code}")

    return metadata

def _paginate_github_api(
    session: requests.Session,
    url: str,
    headers: Dict[str, str],
    params: Dict[str, str] = None,
    per_page: int = PER_PAGE,
    extra: bool = False) -> List[Dict]:
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


def fetch_user_repos(
    username: str,
    auth_token: Optional[str] = None,
    fetch_public: bool = True,
    fetch_private: bool = False,
    extra: bool = False
) -> List[Dict]:
    """
    Fetch public and/or private repositories from GitHub.
    """
    BASE_API_URL = "https://api.github.com"
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}
    repos = []

    with requests.Session() as session:
        # Fetch public repos
        if fetch_public:
            logger.debug(f"Fetching public repositories for user '{username}'...")
            public_url = f"{BASE_API_URL}/users/{username}/repos"
            public_repos = _paginate_github_api(session, public_url, headers, params={'type': 'public'})
            logger.debug(f"Fetched {len(public_repos)} public repositories.")
            repos.extend(public_repos)

        # Fetch private repos
        if fetch_private:
            if not auth_token:
                logger.warning("No auth token provided. Unable to fetch private repositories. Skipping private repos.")
            else:
                logger.debug(f"Fetching private repositories for user '{username}'...")
                private_url = f"{BASE_API_URL}/user/repos"
                private_repos = _paginate_github_api(session, private_url, headers, params={'visibility': 'private'})
                logger.debug(f"Fetched {len(private_repos)} private repositories.")
                repos.extend(private_repos)

        if extra:
            total = len(repos)
            for i, repo in enumerate(repos, start=1):
                repo_name = repo.get('name')
                if not repo_name:
                    logger.warning(f"Repository missing 'name': {repo}")
                    continue
                logger.debug(f"Fetching extra metadata for {username}/{repo_name} ({i}/{total})")
                metadata = fetch_extra(username, repo_name, auth_token=auth_token)
                repo.update(metadata)
        
        if not repos:
            logger.warning(f"No repositories found for user '{username}' with the given options.")

        # Deduplicate by full_name
        #unique_repos = {r['full_name']: r for r in repos}.values()
        #return list(unique_repos)
        return repos 


