#!/usr/bin/env python3

import click
import sys
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.logging import RichHandler
import logging
import json
from typing import Optional, List, Dict
from pathlib import Path
import click
from .utils import console
from .utils import logger
from .fetch import fetch_user_repos, fetch_repos as fr

@click.group()
@click.version_option(version="0.1.0")
@click.option('--log-level', 
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
              case_sensitive=False),
              envvar='GHJ_LOG_LEVEL',
              default='INFO',
              help='Set logging level')
def cli(log_level: str):
    """GitHub JSON (ghj) - A toolkit for working with GitHub repository metadata"""
    from .utils import logger
    logger.setLevel(log_level.upper())

@cli.group()
def fetch():
    """Fetch repository data from GitHub"""
    pass

@fetch.command("user")
@click.argument("username")
@click.option("--auth-token", envvar="GITHUB_TOKEN", help="GitHub personal access token")
@click.option("--extra/--no-extra", default=True, help="Fetch extra metadata like README")
@click.option("--public/--no-public", default=True, help="Include public repositories")
@click.option("--private/--no-private", default=False, help="Include private repositories")
@click.option("--output", "-o", help="Output file (defaults to stdout)")
def fetch_user(username: str,
               auth_token: Optional[str],
               extra: bool,
               public: bool,
               private: bool,
               output: Optional[str]):
    """Fetch repositories for a GitHub user"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Fetching repos for {username}...", total=None)
        repos = fetch_user_repos(username,
                                 auth_token,
                                 fetch_public=public,
                                 fetch_private=private,
                                 extra=extra)
        progress.update(task, completed=True)

    console.print(Panel(f"[green]Successfully fetched {len(repos)} repositories for {username}"))

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote repositories to {output}")
    else:
        print(json.dumps(repos, indent=2))

@fetch.command("repos")
@click.argument("owner-repos", nargs=-1, required=False)
@click.option("--auth-token", envvar="GITHUB_TOKEN", help="GitHub personal access token")
@click.option("--extra/--no-extra", default=True, help="Fetch extra metadata like README")
@click.option("--output", "-o", help="Output file (defaults to stdout)")
def fetch_repos(owner_repos: List[str],
                auth_token: Optional[str],
                extra: bool,
                output: Optional[str]):
    """Fetch metadata for a single repository"""

    try:
        # Handle both file and stdin
        if owner_repos:
            owner_repos = list(owner_repos)
        else:
            if sys.stdin.isatty():  # No pipe input
                console.print("[red]Error:[/red] No input provided")
                sys.exit(1)
            owner_repos = sys.stdin.read().strip().split()
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

    with console.status(f"Fetching repos..."):
        repos = fr(owner_repos, extra=extra, auth_token=auth_token)
        console.print(f"[green]Successfully fetched {len(repos)} out of {len(owner_repos)} repositories")

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote repository data to {output}")
    else:
        print(json.dumps(repos, indent=2))

@cli.group(invoke_without_command=True)
@click.option("--examples", is_flag=True, help="Show set examples")
@click.pass_context
def sets(ctx, examples: bool):
    """Perform set operations on repository JSON files"""
    if ctx.invoked_subcommand is None:
        if examples:
            from .set import print_examples
            print_examples()
        else:
            click.echo(ctx.get_help())

@sets.command()
@click.argument("files", type=click.Path(exists=True), nargs=-1)
@click.option("-o", "--output", help="Output file (defaults to stdout)")
def diff(files: List[str], output: Optional[str]):
    """Get repositories in the first file that are not in the others"""

    from .set import set_diff
    with console.status("Computing the set difference `files[0] - files[1:]`..."):
        repos = set_diff(files)

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote difference to {output}")
    else:
        print(json.dumps(repos, indent=2))

@sets.command()
@click.argument("files", type=click.Path(exists=True), nargs=-1)
@click.option("-o", "--output", help="Output file (defaults to stdout)")
def union(files, output: Optional[str]):
    """Get unique repositories from both files"""

    from .set import set_union
    with console.status("[bold green]Merging[/bold green] repositories..."):
        repos = set_union(files)

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote merged repositories to {output}")
    else:
        print(json.dumps(repos, indent=2))

@sets.command()
@click.argument("files", type=click.Path(exists=True), nargs=-1)
@click.option("-o", "--output", help="Output file (defaults to stdout)")
def intersect(files, output: Optional[str]):
    """Get repositories common to all files"""

    from .set import set_intersect
    with console.status("Computing intersection..."):
        repos = set_intersect(files)

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote intersection to {output}")
    else:
        print(json.dumps(repos, indent=2))

@cli.command()
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.option("--query", "-q", type=str, help="JMESPath query to filter repositories")
@click.option("--examples", is_flag=True, help="Show filter examples")
def filter(input_file: str, query: str, examples: bool):
    """Filter repositories using JMESPath queries"""
    from ghj.filter import filter_repos, print_examples, FilterError
    
    if examples:
        print_examples()
        return

    if not query:
        console.print("[red]Error:[/red] Query required when not showing examples")
        sys.exit(1)

    try:
        # Handle both file and stdin
        if input_file:
            with open(input_file) as f:
                repos = json.load(f)
        else:
            if sys.stdin.isatty():  # No pipe input
                console.print("[red]Error:[/red] No input provided")
                sys.exit(1)
            repos = json.load(sys.stdin)
        
        if isinstance(repos, dict):
            repos = [repos]
            
        filtered = filter_repos(repos, query)
        print(json.dumps(filtered, indent=2))
            
    except FilterError as e:
        console.print(f"[red]Query Error:[/red] {str(e)}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('json_file', type=click.Path(exists=True), required=False)
@click.option('--port', '-p', default=8501, help='Port to run dashboard on')
@click.option('--host', default='localhost', 
              help='Host to run dashboard on. Use 0.0.0.0 for network access')
def dash(json_file, port: int, host: str):
    """Launch the repository dashboard"""
    from ghj.dash import launch_dashboard

    if host != 'localhost':
        console.print("[yellow]Warning: Exposing dashboard to network - ensure you trust your network")
    
    if json_file:
        launch_dashboard(json_file, port=port, host=host)
    else:
        console.print("[yellow]No JSON file provided - dashboard will start in upload mode")
        launch_dashboard(None, port=port, host=host)

@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--base-dir", default="content/projects", help="Hugo content directory")
@click.option("--static-dir", default="static/images", help="Hugo static directory")
def hugo(input_file: str, base_dir: str, static_dir: str):
    """Generate Hugo content from repository data"""
    with console.status("[bold green]Generating Hugo content...") as status:
        # TODO: Implement Hugo generation logic
        pass
    console.print(f"[green]Successfully generated Hugo content in {base_dir}")

def main():
    """Main entry point for the ghj CLI"""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()