import json
import requests
import base64
import logging
from typing import List, Dict, Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

theme = Theme({
    "error": "bold red",
    "warning": "yellow",
    "info": "cyan",
    "success": "bold green"
})

console = Console(theme=theme, highlight=True, stderr=True)


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("ghj")


def sort_repos(repos: List[Dict], sort_key: Optional[str]) -> List[Dict]:
    """
    Sort repositories by a specified key if available.
    """
    if not sort_key:
        return repos
    return sorted(repos, key=lambda r: r.get(sort_key, ''))

def load_json(file):
    with open(file) as f:
        return json.load(f)

def save_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)
