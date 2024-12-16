# filter.py

from typing import List, Dict, Tuple, Any
import re

class FilterError(Exception):
    """Custom exception for filter operations"""
    pass

class FilterQuery:
    """Class to parse and evaluate filter queries."""

    comparison_operators = {'eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'contains'}
    logical_operators = {'and', 'or'}

    def __init__(self, query: Tuple[str, ...]):
        self.tokens = list(query)
        self.conditions = []
        self.operators = []
        self.parse_query()

    def parse_value(self, value: str) -> Any:
        """Parse a string value into an appropriate type."""
        if re.fullmatch(r'^-?\d+$', value):
            return int(value)
        elif re.fullmatch(r'^-?\d+\.\d+$', value):
            return float(value)
        elif value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            return value  # Treat as string

    def get_nested_value(self, obj: Dict, key: str) -> Any:
        """Retrieve a nested value from a dictionary using dot notation."""
        parts = key.split('.')
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                return None
        return obj

    def evaluate_condition(self, repo: Dict, field: str, operator: str, value: Any) -> bool:
        """Evaluate a single condition against a repository."""
        repo_value = self.get_nested_value(repo, field)
        if operator == 'eq':
            return repo_value == value
        elif operator == 'neq':
            return repo_value != value
        elif operator == 'gt':
            return repo_value > value
        elif operator == 'gte':
            return repo_value >= value
        elif operator == 'lt':
            return repo_value < value
        elif operator == 'lte':
            return repo_value <= value
        elif operator == 'in':
            return value in repo_value if isinstance(repo_value, list) else False
        elif operator == 'contains':
            return value in repo_value if isinstance(repo_value, str) else False
        else:
            raise FilterError(f"Unsupported operator: {operator}")

    def parse_query(self):
        """Parse the query tokens into conditions and logical operators."""
        index = 0
        tokens = self.tokens

        while index < len(tokens):
            token = tokens[index]

            if token in self.logical_operators:
                self.operators.append(token)
                index += 1
                continue

            if index + 2 >= len(tokens):
                raise FilterError("Incomplete condition in query.")

            field = tokens[index]
            operator = tokens[index + 1]
            value = tokens[index + 2]

            if operator not in self.comparison_operators:
                raise FilterError(f"Unsupported operator: {operator}")

            parsed_value = self.parse_value(value)
            self.conditions.append((field, operator, parsed_value))

            index += 3

    def evaluate(self, repo: Dict) -> bool:
        """Evaluate all conditions against a repository."""
        result = None
        for i, condition in enumerate(self.conditions):
            field, operator, value = condition
            cond_result = self.evaluate_condition(repo, field, operator, value)

            if i == 0:
                result = cond_result
            else:
                op = self.operators[i - 1]
                if op == 'and':
                    result = result and cond_result
                elif op == 'or':
                    result = result or cond_result
                else:
                    raise FilterError(f"Unsupported logical operator: {op}")

        return result

def filter_repos(repos: List[Dict], query: Tuple[str, ...]) -> List[Dict]:
    """Filter repositories based on custom conditions.
    
    Args:
        repos: List of repository dictionaries
        query: Tuple containing filter conditions and logical operators
        
    Returns:
        List of repositories matching the query
        
    Raises:
        FilterError: If query is invalid or evaluation fails
    """
    if not query:
        raise FilterError("No query provided.")

    filter_query = FilterQuery(query)
    filtered_repos = []

    for repo in repos:
        try:
            if filter_query.evaluate(repo):
                filtered_repos.append(repo)
        except Exception as e:
            # Optionally log or handle exceptions
            pass

    return filtered_repos