from .utils import load_json, console
from typing import List, Dict

# Example queries for documentation/help
SET_EXAMPLES = [
    ("Set Union", "ghj set union file1.json file2.json file3.json"),
    ("Set Intersection", "ghj set intersect file1.json file2.json file3.json"),
    ("Set Difference", "ghj set diff file1.json file2.json file3.json"),
    ("Piping commands", "ghj set union file1.json file2.json | ghj set diff - file3.json")
]


def set_union(files: List[str]) -> List[Dict]:
    sets = []
    for file in files:
        data = load_json(file)
        repo_ids = {repo['id']: repo for repo in data}
        sets.append(repo_ids)

    result = {}
    for s in sets:
        result.update(s)
    return list(result.values())

def set_intersect(files: List[str]) -> List[Dict]:
    sets = []
    data1 = load_json(files[0])
    sets.append(set([repo['id'] for repo in data1]))
    for file in files[1:]:
        sets.append(set([repo['id'] for repo in load_json(file)]))

    # Find common repo ids
    common_ids = sets[0].intersection(*sets[1:])

    # Look at the first file to get the repos in common_ids
    return [repo for repo in data1 if repo['id'] in common_ids]

def set_diff(files: List[str]) -> List[Dict]:
    data1 = load_json(files[0])
    set2 = []
    for file in files[1:]:
        data = load_json(file)
        set2.extend([repo['id'] for repo in data])
        
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