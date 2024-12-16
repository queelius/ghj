import jmespath
from typing import List, Dict, Tuple
from .utils import console

class FilterError(Exception):
    """Custom exception for filter operations"""
    pass

def filter_repos(repos: List[Dict], query: Tuple[str]) -> List[Dict]:
    """Filter repositories using JMESPath query.
    
    Args:
        repos: List of repository dictionaries
        query: tuple containing JMESPath query
        
    Returns:
        List of repositories matching the query
        
    Raises:
        FilterError: If query is invalid or evaluation fails
    """

    # convert tuple to string
    query_str = "".join(query)
    try:
        q = jmespath.compile(query_str)  # Validate syntax
        return [repo for repo in repos if jmespath.search(q.expression, repo, options=jmespath.Options(custom_functions=jmespath.functions))]
    except jmespath.exceptions.ParseError as e:
        raise FilterError(f"Invalid query parse: {str(e)}")
    except jmespath.exceptions.JMESPathError as e:
        raise FilterError(f"Invalid query: {str(e)}")
    except Exception as e:
        raise FilterError(f"Error: {str(e)}")

