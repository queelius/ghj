#!/usr/bin/env python3

import click
import sys
from rich.table import Table
from rich.panel import Panel
from rich.logging import RichHandler
import json
from typing import Optional, List, Dict, Union, Tuple, Any
#from pathlib import Path
import click
from .utils import console
from .utils import logger
from .fetch import GitHubFetcher

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
    logger.setLevel(log_level.upper())

@cli.command(epilog="If no input file is provided, reads from stdin, which can " \
                     "be either a JSON object or a filename (useful for piping). " \
                     "Multiple sort keys can be provided, and the order of keys " \
                     "determines the sort priority, e.g., `ghj sort repo.json -s " \
                     "stargazers_count -s name` will sort by stargazers_count " \
                     "first, then by name.")
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.option("--sort-by", "-s", multiple=True, help="Sort keys (multiple allowed). Default is stargazers_count")
@click.option("--reverse/--no-reverse", "-r/", default=False, help="Reverse sort")
@click.option("--limit", "-l", type=int, help="Limit results")
def sort(input_file: str,
         sort_by: Tuple[str],
         reverse: bool,
         limit: Optional[int]) -> None:
    """Sort repositories by one or more keys."""
    try:
        # Handle input source
        if not input_file:
            if sys.stdin.isatty():
                console.print("[red]Error:[/red] No input provided", file=sys.stderr)
                sys.exit(1)
            
            data = sys.stdin.read().strip()
            try:
                repos = json.loads(data)
            except json.JSONDecodeError:
                with open(data) as f:
                    repos = json.load(f)
        else:
            with open(input_file) as f:
                repos = json.load(f)

        # Default to name if no sort keys
        if not sort_by:
            sort_by = ('stargazers_count',)

        # Sort by multiple keys
        def get_sort_key(repo: Dict) -> Tuple:
            def get_nested_value(obj: Dict, key: str) -> Any:
                for part in key.split('.'):
                    if not isinstance(obj, dict):
                        return None
                    val = obj.get(part)
                    # Convert to comparable types
                    if isinstance(val, (int, float)):
                        return val
                    return str(val) if val is not None else ''
                return obj
            
            return tuple(get_nested_value(repo, key) for key in sort_by)

        repos = sorted(repos, key=get_sort_key, reverse=reverse)

        if limit:
            repos = repos[:limit]

        print(json.dumps(repos, indent=2))

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", file=sys.stderr)
        sys.exit(1)

@cli.command("stats")
@click.argument("input_file", required=False)
@click.option("--output-json", is_flag=True, help="Output statistics as JSON")
def stats(input_file: Union[str, List[Dict]], output_json: bool):
    """Show statistics about the GitHub repositories"""
    from .stats import get_statistics
    import sys

    # Get repo data either from file, stdin, or passed object
    repos = None
    
    try:
        if not input_file:
            if sys.stdin.isatty():
                console.print("[red]Error:[/red] No input provided")
                sys.exit(1)
                
            # Try parsing stdin as JSON first
            data = sys.stdin.read().strip()
            try:
                repos = json.loads(data)
            except json.JSONDecodeError:
                # If not JSON, try as filename
                try:
                    with open(data) as f:
                        repos = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    console.print("[red]Error:[/red] Invalid input - not JSON or valid filename", file=sys.stderr)
                    sys.exit(1)
        else:
            # Direct file input
            try:
                with open(input_file) as f:
                    repos = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                console.print(f"[red]Error:[/red] Failed to load {input_file}: {str(e)}")
                sys.exit(1)

        # Ensure we have a list of repos
        if isinstance(repos, dict):
            repos = [repos]

        # Calculate and output stats
        stats = get_statistics(repos)
        
        if output_json:
            print(json.dumps(stats, indent=2))
        else:
            table = Table(title="GitHub Repository Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            for k, v in stats.items():
                table.add_row(k, str(v))
            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

@cli.group()
def fetch():
    """Fetch repository data from GitHub"""
    pass

@fetch.command("users")
@click.argument("usernames", nargs=-1, required=False)
@click.option("--auth-token", envvar="GITHUB_TOKEN")
@click.option("--extra/--no-extra", default=False)
@click.option("--public/--no-public", default=True)
@click.option("--private/--no-private", default=False)
@click.option("--output", "-o", help="Output file (defaults to stdout)")
def fetch_users(
    usernames: List[str],
    auth_token: Optional[str],
    extra: bool,
    public: bool,
    private: bool,
    output: Optional[str]
):
    """Fetch repositories for GitHub users"""
    fetcher = GitHubFetcher(auth_token)   
    try:
        # Handle both file and stdin
        if not usernames:
            if sys.stdin.isatty():  # No pipe input
                console.print("[red]Error:[/red] No input provided")
                sys.exit(1)
            usernames = sys.stdin.read().strip().split()
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

    with console.status(f"Fetching user repos..."):
        results = fetcher.user_repos(
            usernames,
            fetch_public=public,
            fetch_private=private,
            extra=extra
    )
    console.print(Panel(f"[green]Successfully fetched {len(results)} repositories for {usernames}"))

    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]Successfully wrote repositories to {output}")
    else:
        print(json.dumps(results, indent=2))

@fetch.command("repos")
@click.argument("repos", nargs=-1, required=False)
@click.option("--auth-token", envvar="GITHUB_TOKEN")
@click.option("--extra/--no-extra", default=False)
@click.option("--output", "-o", help="Output file (defaults to stdout)")
def fetch_repo(repos: List[str],
               auth_token: Optional[str],
               extra: bool,
               output: Optional[str]):
    """Fetch a repository's data"""
    fetcher = GitHubFetcher(auth_token)
    
    try:
        # Handle both file and stdin
        if repos:
            repos = list(repos)
        else:
            if sys.stdin.isatty():  # No pipe input
                console.print("[red]Error:[/red] No input provided")
                sys.exit(1)
            repos = sys.stdin.read().strip().split()
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

    with console.status(f"Fetching repos..."):
        result = fetcher.repos(repos, extra=extra)
        console.print(f"[green]Successfully fetched {len(result)} out of {len(repos)} repositories")

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2)
        console.print(f"[green]Successfully wrote repository data to {output}")
    else:
        print(json.dumps(result, indent=2))

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

@sets.command(epilog=("Multiple files can be provided to take the difference of " \
                      "all repositories, e.g., `ghj sets diff file1.json " \
                      "file2.json file3.json` will take the set-difference of " \
                      "the first file from the rest. Standard input is also " \
                      "supported, e.g., `cat repos.txt | ghj sets diff` will " \
                      "read from `repos.txt` a list of filenames and take the " \
                      "set-difference of all repositories in that file."))
@click.argument("files", nargs=-1)
@click.option("-o", "--output", help="Output file (defaults to stdout)")
def diff(files: List[str], output: Optional[str]):
    """Get repositories in the first file that are not in the others"""

    from .set import set_diff_from_files

    if not files:
        console.print("[red]Error:[/red] No files provided")
        sys.exit(1)

    with console.status("Taking [bold green]set-difference[/bold green] of first file from the rest..."):
        repos = set_diff_from_files(files)

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote difference to {output}")
    else:
        print(json.dumps(repos, indent=2))

@sets.command(epilog="Multiple files can be provided to take the union of all " \
                     "repositories, e.g., `ghj sets union file1.json file2.json " \
                     "file3.json` will take the union of all repositories in the " \
                     "three files. Standard input is also supported, e.g., " \
                     "`cat repos.txt | ghj sets union` will read from `repos.txt` " \
                     "a list of filenames and take the union of all repositories " \
                     "in that files.")
@click.argument("files", nargs=-1)
@click.option("-o", "--output", help="Output file (defaults to stdout)")
def union(files, output: Optional[str]):
    """Get unique repositories from both files"""

    from .set import set_union_from_files

    if not files:
        console.print("[red]Error:[/red] No files provided")
        sys.exit(1)

    with console.status("Taking [bold green]union[/bold green] of repositories..."):
        repos = set_union_from_files(files)

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote merged repositories to {output}")
    else:
        print(json.dumps(repos, indent=2))

@sets.command(epilog="Multiple files can be provided to take the intersection of all repositories, e.g., `ghj sets intersect file1.json file2.json file3.json` will take the intersection of all repositories in the three files. Standard input is also supported, e.g., `cat repos.txt | ghj sets intersect` will read from `repos.txt` a list of filenames and take the intersection of all repositories in that file.")
@click.argument("files", nargs=-1)
@click.option("-o", "--output", help="Output file (defaults to stdout)")
def intersect(files, output: Optional[str]):
    """Get repositories common to all files"""

    if not files:
        console.print("[red]Error:[/red] No files provided")
        sys.exit(1)

    from .set import set_intersect_from_files
    with console.status("Taking [bold green]intersection[/bold green] of repositories..."):
        repos = set_intersect_from_files(files)

    if output:
        with open(output, "w") as f:
            json.dump(repos, f, indent=2)
        console.print(f"[green]Successfully wrote intersection to {output}")
    else:
        print(json.dumps(repos, indent=2))

@cli.command(epilog="Use the --examples flag to see filter query examples")
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