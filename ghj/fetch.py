#!/usr/bin/env python3

import argparse
import json
from typing import Optional
import requests
from .utils import (
    set_logging_level, logger, fetch_extra_repo_metadata
)

BASE_API_URL = "https://api.github.com"

def fetch_single_repo(username: str, repo_name: str, auth_token: Optional[str] = None) -> dict:
    headers = {"Authorization": f"token {auth_token}"} if auth_token else {}
    url = f"{BASE_API_URL}/repos/{username}/{repo_name}"

    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(f"Failed to fetch repo {username}/{repo_name}: {resp.status_code}")
        logger.error(f"Response: {resp.text}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Fetch a single GitHub repository's JSON data.")
    parser.add_argument("username", type=str, help="GitHub username")
    parser.add_argument("repo_name", type=str, help="Name of the repository")
    parser.add_argument("--auth-token", type=str, help="Personal access token for private repositories")
    parser.add_argument("--extra-metadata", action="store_true", default=False, help="Fetch extra metadata")
    parser.add_argument("--output-file", type=str, help="Path to write the final JSON output to (defaults to stdout)")
    parser.add_argument("--quiet", action="store_true", default=False, help="Suppress informational logs")
    parser.add_argument("--verbose", action="store_true", default=False, help="Show debug-level logs")

    args = parser.parse_args()
    set_logging_level(quiet=args.quiet, verbose=args.verbose)

    repo_data = fetch_single_repo(args.username, args.repo_name, auth_token=args.auth_token)
    if not repo_data:
        logger.error("No data fetched. Exiting.")
        return

    if args.extra_metadata:
        logger.info(f"Fetching extra metadata for {args.username}/{args.repo_name}")
        metadata = fetch_extra_repo_metadata(args.username, args.repo_name, auth_token=args.auth_token)
        repo_data.update(metadata)

    output_data = json.dumps(repo_data, indent=4)
    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(output_data)
        logger.info(f"Written final JSON output to {args.output_file}")
    else:
        print(output_data)

if __name__ == "__main__":
    main()
