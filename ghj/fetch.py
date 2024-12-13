import requests
from datetime import datetime
from typing import List, Dict, Optional
from .utils import logger
import asyncio
import aiohttp
import base64

class GitHubFetcher:
    """GitHub API client for fetching repository data"""
    
    def __init__(self, auth_token: Optional[str] = None):
        self.auth_token = auth_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {auth_token}" if auth_token else None
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def repos(self, repos: List[str], extra: bool = False) -> List[Dict]:
        """Fetch basic repository data"""
        results = []
        total = len(repos)
        
        for i, repo in enumerate(repos, 1):
            owner, name = repo.split('/')
            logger.debug(f"Fetching {owner}/{name} ({i}/{total})")
            
            try:
                repo_data = self._fetch_repo(owner, name)
                if extra:
                    extra_data = self.fetch_extra(owner, name)
                    repo_data.update(extra_data)
                results.append(repo_data)
            except Exception as e:
                logger.error(f"Failed to fetch {repo}: {str(e)}")
                
        return results

    def _fetch_repo(self, owner: str, name: str) -> Dict:
        """Fetch basic repository metadata"""
        url = f"{self.base_url}/repos/{owner}/{name}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def fetch_extra(self, owner: str, name: str) -> Dict:
        """Fetch additional repository metadata"""
        return {
            "stargazer_history": self._fetch_stargazers(owner, name),
            "commit_history": self._fetch_commits(owner, name),
            "contributors": self._fetch_contributors(owner, name),
            "languages": self._fetch_languages(owner, name),
            "readme": self._fetch_readme(owner, name)
        }

    def _fetch_stargazers(self, owner: str, name: str) -> List[Dict]:
        """Fetch repository stargazer history"""
        url = f"{self.base_url}/repos/{owner}/{name}/stargazers"
        headers = {**self.headers, "Accept": "application/vnd.github.star+json"}
        
        stars = []
        page = 1
        while True:
            resp = requests.get(f"{url}?page={page}&per_page=100", headers=headers)
            resp.raise_for_status()
            
            data = resp.json()
            if not data:
                break
                
            stars.extend([{
                "user": star["user"]["login"],
                "starred_at": star["starred_at"]
            } for star in data])
            
            page += 1
            
        return stars

    def _fetch_commits(self, owner: str, name: str) -> List[Dict]:
        """Fetch repository commit history"""
        url = f"{self.base_url}/repos/{owner}/{name}/commits"
        commits = []
        page = 1
        
        while True:
            resp = requests.get(f"{url}?page={page}&per_page=100", headers=self.headers)
            resp.raise_for_status()
            
            data = resp.json()
            if not data:
                break
                
            commits.extend([{
                "sha": commit["sha"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "message": commit["commit"]["message"]
            } for commit in data])
            
            page += 1
            
        return commits

    def _fetch_contributors(self, owner: str, name: str) -> List[Dict]:
        """Fetch repository contributors"""
        url = f"{self.base_url}/repos/{owner}/{name}/contributors"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def _fetch_languages(self, owner: str, name: str) -> Dict:
        """Fetch repository language statistics"""
        url = f"{self.base_url}/repos/{owner}/{name}/languages"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def _fetch_readme(self, owner: str, name: str) -> Optional[str]:
        """Fetch repository README content"""
        url = f"{self.base_url}/repos/{owner}/{name}/readme"
        try:
            resp = self.session.get(url)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", "")
            if content:
                return base64.b64decode(content).decode('utf-8')
        except:
            logger.debug(f"No README found for {owner}/{name}")
        return None

    def user_repos(
        self,
        usernames: List[str],
        fetch_public: bool = True,
        fetch_private: bool = False,
        extra: bool = False
    ) -> List[Dict]:
        """Fetch repositories for given usernames.
        
        Args:
            usernames: List of GitHub usernames
            fetch_public: Whether to fetch public repos
            fetch_private: Whether to fetch private repos (requires auth)
            extra: Whether to fetch additional metadata
        """
        all_repos = []
        
        for username in usernames:
            logger.debug(f"Fetching repositories for user '{username}'...")
            
            try:
                # Fetch public repos
                if fetch_public:
                    public_repos = self._fetch_user_repos(
                        username, 
                        visibility='public'
                    )
                    all_repos.extend(public_repos)
                    logger.debug(f"Fetched {len(public_repos)} public repos")

                # Fetch private repos
                if fetch_private:
                    if not self.auth_token:
                        logger.warning("Auth token required for private repos")
                        continue
                        
                    private_repos = self._fetch_user_repos(
                        username, 
                        visibility='private'
                    )
                    all_repos.extend(private_repos)
                    logger.debug(f"Fetched {len(private_repos)} private repos")

                # Fetch extra metadata if requested
                if extra:
                    for repo in all_repos:
                        logger.debug(f"Fetching extra metadata for {username}/{repo['name']}")
                        owner = repo['owner']['login']
                        name = repo['name']
                        extra_data = self.fetch_extra(owner, name)
                        repo.update(extra_data)

            except Exception as e:
                logger.error(f"Failed to fetch repos for {username}: {str(e)}")
                continue

        return all_repos

    def _fetch_user_repos(
        self, 
        username: str, 
        visibility: str = 'all'
    ) -> List[Dict]:
        """Fetch repositories for a user with pagination."""
        url = f"{self.base_url}/users/{username}/repos"
        params = {
            'type': visibility,
            'per_page': 100,
            'sort': 'updated'
        }
        
        repos = []
        page = 1
        
        while True:
            logger.debug(f"Fetching page {page} of {username}'s repos")
            params['page'] = page
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            
            data = resp.json()
            if not data:
                break
                
            repos.extend(data)
            page += 1
            
        return repos