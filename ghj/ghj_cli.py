#!/usr/bin/env python3
import sys
import argparse
import json
from typing import Optional, List, Dict, Any, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler

import os

# Import your internal modules
from .utils import console, logger
from .fetch import GitHubFetcher
from .stats import get_statistics, display_main_metrics, display_nested_metrics
from .set import set_diff_from_files, set_union_from_files, set_intersect_from_files
import jaf

def main():
    parser = argparse.ArgumentParser(
        prog="ghj",
        description="GitHub JSON (ghj) - A toolkit for working with GitHub repository metadata",
        epilog="""Examples:
  ghj sort repos.json -s stargazers_count -s name
  ghj fetch users octocat torvalds
  ghj sets diff file1.json file2.json file3.json
  ghj filter repos.json language eq? Python OR stargazers_count > 500
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--log-level", default="INFO", help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- sort command ---
    sort_parser = subparsers.add_parser(
        "sort",
        help="Sort repositories by one or more keys",
        epilog="""If no input file is provided, reads from stdin, which can be either a JSON object or a filename.
Multiple sort keys can be provided; their order determines priority.
Example:
  ghj sort repos.json -s stargazers_count -s name
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sort_parser.add_argument("input_file", nargs="?", help="Input file with repositories")
    sort_parser.add_argument("-s", "--sort-by", action="append", default=[], help="Sort keys (multiple allowed). Default is stargazers_count")
    sort_parser.add_argument("-r", "--reverse", action="store_true", help="Reverse sort")
    sort_parser.add_argument("-l", "--limit", type=int, help="Limit results")
    sort_parser.set_defaults(func=handle_sort)

    # --- stats command ---
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show statistics about the GitHub repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    stats_parser.add_argument("input_file", nargs="?", help="Input file or list of repositories (JSON)")
    stats_parser.add_argument("--json", action="store_true", help="Output statistics as JSON")
    stats_parser.set_defaults(func=handle_stats)

    # --- fetch group ---
    fetch_parser = subparsers.add_parser(
        "fetch",
        help="Fetch repository data from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    fetch_subparsers = fetch_parser.add_subparsers(dest="subcommand", required=True)

    # fetch users
    fetch_users_parser = fetch_subparsers.add_parser(
        "users",
        help="Fetch repositories for GitHub users",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  ghj fetch users torvalds octocat
  echo "torvalds guido" | ghj fetch users
"""
    )

    fetch_users_parser.add_argument("usernames", nargs="*", help="List of GitHub usernames")
    
    # let's by default fetch from environment variable GITHUB_TOKEN
    fetch_users_parser.add_argument("--auth-token", help="GitHub API token (or set GITHUB_TOKEN env var)",
                                    default=os.environ.get("GITHUB_TOKEN"))
    # Using mutually exclusive options for extra
    extra_group = fetch_users_parser.add_mutually_exclusive_group()
    extra_group.add_argument("--extra", dest="extra", action="store_true", default=True, help="Fetch extra data")
    extra_group.add_argument("--no-extra", dest="extra", action="store_false", help="Do not fetch extra data")
    public_group = fetch_users_parser.add_mutually_exclusive_group()
    public_group.add_argument("--public", dest="public", action="store_true", default=True, help="Fetch public repositories")
    public_group.add_argument("--no-public", dest="public", action="store_false", help="Do not fetch public repositories")
    fetch_users_parser.add_argument("--private", action="store_true", default=False, help="Fetch private repositories")
    fetch_users_parser.add_argument("-o", "--output", help="Output file (defaults to stdout)")
    fetch_users_parser.set_defaults(func=handle_fetch_users)

    # fetch repos
    fetch_repos_parser = fetch_subparsers.add_parser(
        "repos",
        help="Fetch a repository's data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj fetch repos owner1/repo1 owner2/repo2
"""
    )
    fetch_repos_parser.add_argument("repos", nargs="*", help="Repository names (e.g., owner/repo)")
    fetch_repos_parser.add_argument("--auth-token", help="GitHub API token")
    fetch_repos_parser.add_argument("--extra", action="store_true", default=False, help="Fetch extra data")
    fetch_repos_parser.add_argument("-o", "--output", help="Output file (defaults to stdout)")
    fetch_repos_parser.set_defaults(func=handle_fetch_repos)

    # --- sets group ---
    sets_parser = subparsers.add_parser(
        "sets",
        help="Set operations on repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sets_subparsers = sets_parser.add_subparsers(dest="subcommand", required=True)

    # sets diff
    diff_parser = sets_subparsers.add_parser(
        "diff",
        help="Get repositories in the first file that are not in the others",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj sets diff file1.json file2.json file3.json
  cat repos.txt | ghj sets diff
"""
    )
    diff_parser.add_argument("files", nargs="+", help="List of repository JSON files")
    diff_parser.add_argument("-o", "--output", help="Output file (defaults to stdout)")
    diff_parser.set_defaults(func=handle_sets_diff)

    # sets union
    union_parser = sets_subparsers.add_parser(
        "union",
        help="Get unique repositories from multiple files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj sets union file1.json file2.json file3.json
  cat repos.txt | ghj sets union
"""
    )
    union_parser.add_argument("files", nargs="+", help="List of repository JSON files")
    union_parser.add_argument("-o", "--output", help="Output file (defaults to stdout)")
    union_parser.set_defaults(func=handle_sets_union)

    # sets intersect
    intersect_parser = sets_subparsers.add_parser(
        "intersect",
        help="Get repositories common to all files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj sets intersect file1.json file2.json file3.json
  cat repos.txt | ghj sets intersect
"""
    )
    intersect_parser.add_argument("files", nargs="+", help="List of repository JSON files")
    intersect_parser.add_argument("-o", "--output", help="Output file (defaults to stdout)")
    intersect_parser.set_defaults(func=handle_sets_intersect)

    # --- filter command ---
    filter_parser = subparsers.add_parser(
        "filter",
        help="Filter repositories based on provided conditions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj filter repos.json language eq? Python OR stargazers_count > 500
"""
    )
    filter_parser.add_argument("input_file", nargs="?", help="Input JSON file with repositories")
    filter_parser.add_argument("query", nargs="+", help="Query string for filtering")
    filter_parser.set_defaults(func=handle_filter)

    # --- dash command ---
    dash_parser = subparsers.add_parser(
        "dash",
        help="Launch the repository dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj dash repos.json --port 8501 --host 0.0.0.0
"""
    )
    dash_parser.add_argument("json_file", nargs="?", help="JSON file with repository data")
    dash_parser.add_argument("--port", "-p", type=int, default=8501, help="Port to run dashboard on")
    dash_parser.add_argument("--host", default="localhost", help="Host to run dashboard on (use 0.0.0.0 for network access)")
    dash_parser.set_defaults(func=handle_dash)

    # --- hugo command ---
    hugo_parser = subparsers.add_parser(
        "hugo",
        help="Generate Hugo content from repository data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  ghj hugo repos.json --content-dir content/projects --static-dir static/images --download-images
"""
    )
    hugo_parser.add_argument("input_file", help="Input JSON file with repository data")
    hugo_parser.add_argument("--content-dir", default="content/projects", help="Hugo content directory")
    hugo_parser.add_argument("--static-dir", default="static/images", help="Hugo static directory")
    hugo_parser.add_argument("--download-images", dest="download_images", action="store_true", default=True, help="Download repository images")
    hugo_parser.add_argument("--no-images", dest="download_images", action="store_false", help="Do not download repository images")
    hugo_parser.set_defaults(func=handle_hugo)

    # Parse arguments and dispatch
    args = parser.parse_args()
    logger.setLevel(args.log_level.upper())
    args.func(args)


# -------------------------
# HANDLER FUNCTIONS BELOW
# -------------------------

def handle_sort(args):
    try:
        # Input source: file or stdin
        if not args.input_file:
            if sys.stdin.isatty():
                console.print("[red]Error:[/red] No input provided", style="red")
                sys.exit(1)
            data = sys.stdin.read().strip()
            try:
                repos = json.loads(data)
            except json.JSONDecodeError:
                with open(data) as f:
                    repos = json.load(f)
        else:
            with open(args.input_file) as f:
                repos = json.load(f)

        # Default sort key if none provided
        sort_keys = args.sort_by or ['stargazers_count']

        def get_sort_key(repo: Dict) -> Tuple:
            def get_nested_value(obj: Dict, key: str) -> Any:
                for part in key.split('.'):
                    if not isinstance(obj, dict):
                        return None
                    val = obj.get(part)
                    return val if isinstance(val, (int, float)) else str(val) if val is not None else ''
                return obj
            return tuple(get_nested_value(repo, key) for key in sort_keys)

        repos = sorted(repos, key=get_sort_key, reverse=args.reverse)
        if args.limit:
            repos = repos[:args.limit]

        repos = json.dumps(repos, indent=2, ensure_ascii=True)
        from rich.json import JSON
        console.print(JSON(repos))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_stats(args):
    try:
        if not args.input_file:
            if sys.stdin.isatty():
                console.print("[red]Error:[/red] No input provided", style="red")
                sys.exit(1)
            data = sys.stdin.read().strip()
            try:
                repos = json.loads(data)
            except json.JSONDecodeError:
                with open(data) as f:
                    repos = json.load(f)
        else:
            with open(args.input_file) as f:
                repos = json.load(f)
        if isinstance(repos, dict):
            repos = [repos]

        stats = get_statistics(repos)
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            display_main_metrics(stats, console)
            for category in [
                "languages", "topics", "licenses", "activity",
                "owner_stats", "url_stats", "repo_characteristics",
                "git_stats", "history", "contributors", "branches", "collaboration"
            ]:
                data = stats.get(category, {})
                if data:
                    display_nested_metrics(category.replace('_', ' ').title(), data, console)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_fetch_users(args):
    try:
        fetcher = GitHubFetcher(args.auth_token)
        # If no usernames provided, try reading from stdin
        usernames = args.usernames or (sys.stdin.read().strip().split() if not sys.stdin.isatty() else [])
        if not usernames:
            console.print("[red]Error:[/red] No usernames provided", style="red")
            sys.exit(1)
        with console.status("Fetching user repos..."):
            results = fetcher.user_repos(
                usernames,
                fetch_public=args.public,
                fetch_private=args.private,
                extra=args.extra,
            )
        console.print(Panel(f"[green]Successfully fetched {len(results)} repositories for {usernames}"))
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
        else:
            print(json.dumps(results, indent=2))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_fetch_repos(args):
    try:
        fetcher = GitHubFetcher(args.auth_token)
        repos = args.repos or (sys.stdin.read().strip().split() if not sys.stdin.isatty() else [])
        if not repos:
            console.print("[red]Error:[/red] No repository names provided", style="red")
            sys.exit(1)
        with console.status("Fetching repositories..."):
            result = fetcher.repos(repos, extra=args.extra)
        console.print(f"[green]Successfully fetched {len(result)} out of {len(repos)} repositories")
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_sets_diff(args):
    try:
        if not args.files:
            console.print("[red]Error:[/red] No files provided", style="red")
            sys.exit(1)
        with console.status("Taking set-difference of first file from the rest..."):
            repos = set_diff_from_files(args.files)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(repos, f, indent=2)
            console.print(f"[green]Successfully wrote difference to {args.output}")
        else:
            print(json.dumps(repos, indent=2))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_sets_union(args):
    try:
        if not args.files:
            console.print("[red]Error:[/red] No files provided", style="red")
            sys.exit(1)
        with console.status("Taking union of repositories..."):
            repos = set_union_from_files(args.files)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(repos, f, indent=2)
            console.print(f"[green]Successfully wrote merged repositories to {args.output}")
        else:
            print(json.dumps(repos, indent=2))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_sets_intersect(args):
    try:
        if not args.files:
            console.print("[red]Error:[/red] No files provided", style="red")
            sys.exit(1)
        with console.status("Taking intersection of repositories..."):
            repos = set_intersect_from_files(args.files)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(repos, f, indent=2)
            console.print(f"[green]Successfully wrote intersection to {args.output}")
        else:
            print(json.dumps(repos, indent=2))
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_filter(args):
    try:
        if not args.input_file:
            if sys.stdin.isatty():
                console.print("[red]Error:[/red] No input provided", style="red")
                sys.exit(1)
            repos = json.load(sys.stdin)
        else:
            with open(args.input_file) as f:
                repos = json.load(f)
        if isinstance(repos, dict):
            repos = [repos]

        query = " ".join(args.query)
        print(query)  # For debugging purposes
        ast_query = jaf.dsl.parse.parse_dsl(query)
        console.print(ast_query)
        filtered_repos = jaf.jaf(repos, ast_query)
        console.print(json.dumps(filtered_repos, indent=2))
    except jaf.jafError as je:
        console.print(f"[red]Filter Error:[/red] {str(je)}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_dash(args):
    try:
        from ghj.dash import launch_dashboard
        if args.host != "localhost":
            console.print("[yellow]Warning: Exposing dashboard to network - ensure you trust your network")
        if args.json_file:
            launch_dashboard(args.json_file, port=args.port, host=args.host)
        else:
            console.print("[yellow]No JSON file provided - dashboard will start in upload mode")
            launch_dashboard(None, port=args.port, host=args.host)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


def handle_hugo(args):
    try:
        from ghj.hugo import HugoRenderer
        with console.status("[bold green]Loading repository data..."):
            with open(args.input_file) as f:
                repos = json.load(f)
            if isinstance(repos, dict):
                repos = [repos]
        renderer = HugoRenderer(
            content_dir=args.content_dir,
            static_dir=args.static_dir,
        )
        with console.status("[bold green]Generating Hugo content..."):
            renderer.render_repos(repos, download_images=args.download_images)
        console.print("[bold green]✓ Hugo content generation complete!")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
