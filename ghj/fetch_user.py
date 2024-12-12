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
        logger.info(f"Fetched {len(repos)} repositories from GitHub.")

    # Apply filtering
    if args.filter:
        original_count = len(repos)
        repos = filter_repos(repos, args.filter)
        logger.info(f"Filtered repositories by '{args.filter}', {len(repos)} remain out of {original_count}.")

    # If extra-metadata is requested, fetch it
    if args.extra_metadata and repos:
        repos = fetch_extra_metadata(username=args.username,
                                     repos=repos,
                                     auth_token=args.auth_token)

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
