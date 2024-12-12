#!/usr/bin/env python3

import os
import json
import argparse
from typing import List, Dict, Optional
import requests
from .utils import (
    set_logging_level, logger, _paginate_github_api,
    fetch_extra_repo_metadata, filter_repos, sort_repos
)

def fetch_github_repos(
    username: str,
    auth_token: Optional[str] = None,
    fetch_public: bool = True,
    fetch_private: bool = False
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
            logger.info(f"Fetching public repositories for user '{username}'...")
            public_url = f"{BASE_API_URL}/users/{username}/repos"
            public_repos = _paginate_github_api(session, public_url, headers, params={'type': 'public'})
            logger.info(f"Fetched {len(public_repos)} public repositories.")
            repos.extend(public_repos)

        # Fetch private repos
        if fetch_private:
            if not auth_token:
                logger.warning("No auth token provided. Unable to fetch private repositories. Skipping private repos.")
            else:
                logger.info(f"Fetching private repositories for user '{username}'...")
                private_url = f"{BASE_API_URL}/user/repos"
                private_repos = _paginate_github_api(session, private_url, headers, params={'visibility': 'private'})
                logger.info(f"Fetched {len(private_repos)} private repositories.")
                repos.extend(private_repos)

    if not repos:
        logger.warning(f"No repositories found for user '{username}' with the given options.")

    # Deduplicate by full_name
    unique_repos = {r['full_name']: r for r in repos}.values()
    return list(unique_repos)


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


