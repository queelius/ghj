import jmespath
from typing import List, Dict, Any
from .utils import console

# Example queries for documentation/help
FILTER_EXAMPLES = [
    ("Python repos", "language == 'Python'"),
    ("Repos with >50 stars", "stargazers_count > `50`"),
    ("Non-fork repos", "fork == `false`"),
    ("Python repos with >50 stars", "language == 'Python' && stargazers_count > `50`"),
    ("Recently updated", "contains(updated_at, '2024')"),
    ("Complex query", "language == 'Python' && stargazers_count > `50` && (language == 'Python' || language == 'JavaScript')"),
    ("Contains topic", "contains(topics, 'data-science')")
]

class FilterError(Exception):
    """Custom exception for filter operations"""
    pass

def filter_repos(repos: List[Dict], query: str) -> List[Dict]:
    """Filter repositories using JMESPath query.
    
    Args:
        repos: List of repository dictionaries
        query: JMESPath query string
        
    Returns:
        List of repositories matching the query
        
    Raises:
        FilterError: If query is invalid or evaluation fails
    """
    try:
        return [repo for repo in repos if jmespath.search(query, repo)]
    except jmespath.exceptions.JMESPathError as e:
        raise FilterError(f"Invalid query: {str(e)}")

def print_examples():
    """Display common filter examples using rich console."""
    console.print("\n[bold yellow]Filter Examples:[/bold yellow]")
    
    for desc, query in FILTER_EXAMPLES:
        console.print(f"[bold green]{desc}[/bold green]:")
        console.print(f"  ghj filter repos.json --query '{query}'\n")
    
    console.print("[bold blue]Tips:[/bold blue]")
    console.print("• Use backticks for numbers: [cyan]`50`[/cyan]")
    console.print("• Use quotes for strings: [cyan]'Python'[/cyan]")
    console.print("• Combine conditions with [cyan]&&[/cyan]")