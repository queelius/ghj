from .utils import load_json, console, logger
from typing import List, Dict
import json

# Example queries for documentation/help
SET_EXAMPLES = [
    ("Set Union", "ghj sets union file1.json file2.json file3.json"),
    ("Set Intersection", "ghj sets intersect file1.json file2.json file3.json"),
    ("Set Difference", "ghj set diff file1.json file2.json file3.json"),
    ("Piping commands", "ghj sets union file1.json file2.json | ghj set diff - file3.json")
]

def remove_dups(repos: List[Dict]) -> List[Dict]:
    """
    Remove duplicate repositories from a list of repositories.

    :param repos: List of repository dictionaries
    :return: List of unique repositories
    """
    results = {}
    for repo in repos:
        results[repo['id']] = repo
    return list(results.values())

def set_union(repo_sets: List[Dict]) -> List[Dict]:
    """
    Get the union of multiple sets of repositories.

    :param repo_sets: List of repository sets
    :return: List of the union of all repositories
    """
    results = {}
    for repo_set in repo_sets:
        for repo in repo_set:
            try:
                results[repo['id']] = repo
            except KeyError:
                if 'name' in repo:
                    logger.error(f"Repository ID not found in repo {repo.get('name', '')}")
                else:
                    logger.error(f"Repository ID not found in repo")
            except Exception as e:
                logger.error(f"Error adding repository to union: {str(e)}")
    return list(results.values())

def set_union_from_files(files: List[str]) -> List[Dict]:
    """Get unique repositories from all files."""
    repos = []
    logger.debug(f"Computing union{files}")
    for file in files:
        try:
            repos.extend(load_json(file))
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {str(e)}")
    return remove_dups(repos)

def set_interesect(repo_sets: List[Dict]) -> List[Dict]:
    """
    Get the intersection of multiple sets of repositories.

    :param repo_sets: List of repository sets
    :return: List of the intersection of all repositories
    """
    sets = []
    for repo_set in repo_sets:
        try:
            sets.append(set([repo['id'] for repo in repo_set]))
        except KeyError:
            if 'name' in repo_set:
                logger.error(f"Repository ID not found in repo {repo_set.get('name', '')}")
            else:
                logger.error(f"Repository ID not found in repo")
        except Exception as e:
            logger.error(f"Error adding repository to intersection set: {str(e)}")

    common_ids = sets[0].intersection(*sets[1:])
    return [repo for repo in repo_sets[0] if repo['id'] in common_ids]

def set_intersect_from_files(files: List[str]) -> List[Dict]:
    """
    Get repositories common to all files.
    """
    repos = []
    logger.debug(f"Computing intersection{files}")
    for file in files:
        try:
            repos.append(load_json(file))
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON file: {str(e)}")
    return set_interesect(repos)

def set_diff_from_files(files: List[str]) -> List[Dict]:
    """
    Get the difference between the first repo JSON file and the rest.
    """
    repos = []
    for file in files:
        repos.append(load_json(file))
    return set_diff(repos)

def set_diff(repo_sets: List[Dict]) -> List[Dict]:
    """
    Get the difference between the first set and the rest.
    """
    data1 = repo_sets[0]
    set2 = []
    for repo_set in repo_sets[1:]:
        set2.extend([repo['id'] for repo in repo_set])
    return [repo for repo in data1 if repo['id'] not in set2]

def print_examples():
    """Display common set examples using rich console."""
    console.print("\n[bold yellow]Set Examples:[/bold yellow]")
    
    for desc, query in SET_EXAMPLES:
        console.print(f"[bold green]{desc}[/bold green]:")
        console.print(f"  {query}\n")
    
    console.print("[bold blue]Tips:[/bold blue]")
    console.print("• Use piping to combine commands")
    console.print("• stdin and stdout are supported, so you can chain commands")