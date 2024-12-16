# filter_lang.py

from typing import List, Dict, Any, Union
import re
import logging
from lark import Lark, Transformer, v_args, exceptions

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class FilterError(Exception):
    """Custom exception for filter operations."""
    pass


class Condition:
    """Represents a single condition in the filter query."""

    comparison_operators = {'eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'contains', 'regex', 'startswith', 'endswith'}

    def __init__(self, field: str, operator: str, value: Any):
        if not isinstance(operator, str):
            raise FilterError(f"Invalid operator type: {type(operator)} in condition.")
        operator_lower = operator.lower()
        if operator_lower not in self.comparison_operators:
            raise FilterError(f"Unsupported comparison operator: {operator_lower}")
        self.field = field
        self.operator = operator_lower
        self.value = self.parse_value(value)

    @staticmethod
    def parse_value(value: Any) -> Any:
        """Parse the value into an appropriate type."""
        if isinstance(value, str):
            if re.fullmatch(r'^-?\d+$', value):
                return int(value)
            elif re.fullmatch(r'^-?\d+\.\d+$', value):
                return float(value)
            elif value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
        return value

    def get_nested_value(self, obj: Dict, key: str) -> Any:
        """Retrieve a nested value from a dictionary using dot notation."""
        parts = key.split('.')
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part)
                if obj is None:
                    return None
            else:
                return None
        return obj

    def evaluate(self, repo: Dict) -> bool:
        """Evaluate the condition against a repository."""
        repo_value = self.get_nested_value(repo, self.field)

        # Handle missing fields
        if repo_value is None:
            if self.operator == 'neq':
                return True  # None != any value except None
            elif self.operator == 'eq':
                return self.value is None
            else:
                return False  # For other operators, treat missing as False

        try:
            if self.operator == 'eq':
                return repo_value == self.value
            elif self.operator == 'neq':
                return repo_value != self.value
            elif self.operator == 'gt':
                return repo_value > self.value
            elif self.operator == 'gte':
                return repo_value >= self.value
            elif self.operator == 'lt':
                return repo_value < self.value
            elif self.operator == 'lte':
                return repo_value <= self.value
            elif self.operator == 'in':
                return self.value in repo_value if isinstance(repo_value, list) else False
            elif self.operator == 'contains':
                return self.value in repo_value if isinstance(repo_value, str) else False
            elif self.operator == 'regex':
                return re.search(self.value, repo_value) is not None if isinstance(repo_value, str) else False
            elif self.operator == 'startswith':
                return repo_value.startswith(self.value) if isinstance(repo_value, str) else False
            elif self.operator == 'endswith':
                return repo_value.endswith(self.value) if isinstance(repo_value, str) else False
            else:
                raise FilterError(f"Unsupported operator: {self.operator}")
        except TypeError as e:
            raise FilterError(f"Type error in condition: {e}")


class LogicalOperation:
    """Represents a logical operation (AND/OR/NOT) in the filter query."""

    logical_operators = {'and', 'or', 'not'}

    def __init__(self, operator: str, operands: List[Any]):
        if not isinstance(operator, str):
            raise FilterError(f"Invalid logical operator type: {type(operator)}")
        operator_lower = operator.lower()
        if operator_lower not in self.logical_operators:
            raise FilterError(f"Unsupported logical operator: {operator_lower}")
        self.operator = operator_lower
        self.operands = operands

        # Validate operand count for 'not' operator
        if self.operator == 'not' and len(self.operands) != 1:
            raise FilterError(f"'not' operator requires exactly one operand, got {len(self.operands)}")
        if self.operator in {'and', 'or'} and len(self.operands) < 1:
            raise FilterError(f"'{self.operator}' operator requires at least one operand, got {len(self.operands)}")

    def evaluate(self, repo: Dict) -> bool:
        """Evaluate the logical operation against a repository."""
        if self.operator == 'and':
            return all(operand.evaluate(repo) for operand in self.operands)
        elif self.operator == 'or':
            return any(operand.evaluate(repo) for operand in self.operands)
        elif self.operator == 'not':
            return not self.operands[0].evaluate(repo)
        else:
            raise FilterError(f"Unsupported logical operator: {self.operator}")


class FilterQuery:
    """Class to parse and evaluate filter queries represented as an AST."""

    def __init__(self, query: Union[List, Dict, str], is_dsl: bool = False):
        """
        Initialize the FilterQuery.

        Args:
            query: The filter query, either as a list/dict AST or a DSL string.
            is_dsl: Indicates if the query is a DSL string.
        """
        self.query = query
        if is_dsl:
            self.ast = self.parse_dsl(query)
        else:
            self.ast = self.parse_ast(query)

    def parse_ast(self, query: Union[List, Dict]) -> Any:
        """Parse the query AST into internal AST objects."""
        if isinstance(query, list):
            if not query:
                raise FilterError("Empty query list.")
            operator = query[0]
            if isinstance(operator, str):
                operator_lower = operator.lower()
                if operator_lower in LogicalOperation.logical_operators:
                    operands = [self.parse_ast(subquery) for subquery in query[1:]]
                    return LogicalOperation(operator_lower, operands)
            # If not a logical operator, treat as condition
            if len(query) != 3:
                raise FilterError(f"Invalid condition format: {query}")
            field, operator, value = query
            if not isinstance(operator, str):
                raise FilterError(f"Invalid operator type: {type(operator)} in condition.")
            return Condition(field, operator.lower(), value)
        elif isinstance(query, dict):
            # Only allow one key in the dictionary (the operator)
            if not query:
                raise FilterError("Empty query dictionary.")
            if len(query) != 1:
                raise FilterError("Query dictionary must have exactly one key (the operator).")
            operator, operands = next(iter(query.items()))
            if not isinstance(operator, str):
                raise FilterError(f"Invalid logical operator type: {type(operator)}")
            operator_lower = operator.lower()
            if operator_lower not in LogicalOperation.logical_operators:
                raise FilterError(f"Unsupported logical operator in dict: {operator_lower}")
            if not isinstance(operands, list):
                raise FilterError(f"Operands must be a list for operator '{operator_lower}'.")
            parsed_operands = [self.parse_ast(subquery) for subquery in operands]
            return LogicalOperation(operator_lower, parsed_operands)
        else:
            raise FilterError(f"Invalid query type: {type(query)}")

    def parse_dsl(self, query: str) -> Any:
        """Parse the DSL string into internal AST objects."""
        # Define the Lark grammar
        dsl_grammar = r"""
            ?start: expr

            ?expr: expr "AND" term   -> and_op
                 | expr "OR" term    -> or_op
                 | term

            ?term: "NOT" term        -> not_op
                 | "(" expr ")"
                 | condition

            ?condition: field COMPARATOR value   -> condition

            field: CNAME ("." CNAME)*

            COMPARATOR: "eq" | "neq" | "gt" | "gte" | "lt" | "lte" | "in" | "contains" | "regex" | "startswith" | "endswith"

            value: ESCAPED_STRING      -> string
                 | SIGNED_NUMBER       -> number
                 | "true"              -> true
                 | "false"             -> false

            %import common.CNAME
            %import common.ESCAPED_STRING
            %import common.SIGNED_NUMBER
            %import common.WS
            %ignore WS
        """

        # Initialize the parser
        parser = Lark(dsl_grammar, parser='lalr', transformer=DSLTransformer())

        try:
            ast = parser.parse(query)
            return ast
        except exceptions.LarkError as e:
            logger.error(f"Failed to parse DSL query: {e}")
            raise FilterError(f"Failed to parse DSL query: {e}")

    def evaluate(self, repo: Dict) -> bool:
        """Evaluate the parsed AST against a repository."""
        return self.ast.evaluate(repo)


@v_args(inline=True)
class DSLTransformer(Transformer):
    """Transformer to convert Lark parse trees to AST objects."""

    def and_op(self, left, right):
        return LogicalOperation(operator='and', operands=[left, right])

    def or_op(self, left, right):
        return LogicalOperation(operator='or', operands=[left, right])

    def not_op(self, operand):
        return LogicalOperation(operator='not', operands=[operand])

    def condition(self, field, comparator, value):
        return Condition(field=field, operator=str(comparator), value=value)

    def field(self, *items):
        # Concatenate nested fields with dots
        return '.'.join(items)

    # Removed the 'comparator' method to prevent the TypeError

    def string(self, s):
        # Remove surrounding quotes
        return str(s)[1:-1]

    def number(self, n):
        num_str = n
        if '.' in num_str or 'e' in num_str.lower():
            return float(num_str)
        return int(num_str)

    def true(self):
        return True

    def false(self):
        return False


def filter_repos(repos: List[Dict], query: Union[List, Dict, str], is_dsl: bool = False) -> List[Dict]:
    """
    Filter repositories based on custom conditions using an AST-based or DSL query.

    Args:
        repos: List of repository dictionaries.
        query: Nested list/dict AST or a DSL string representing the filter conditions and logical operators.
        is_dsl: If True, treat the query as a DSL string.

    Returns:
        List of repositories matching the query.

    Raises:
        FilterError: If query is invalid or evaluation fails.
    """
    if not query:
        raise FilterError("No query provided.")

    try:
        filter_query = FilterQuery(query, is_dsl=is_dsl)
    except FilterError as e:
        logger.error(f"Failed to parse query: {e}")
        raise

    filtered_repos = []

    for repo in repos:
        try:
            if filter_query.evaluate(repo):
                filtered_repos.append(repo)
        except FilterError as e:
            logger.error(f"Error evaluating repo {repo.get('id', 'unknown')}: {e}")
            # Depending on requirements, you might choose to continue or halt
            continue

    return filtered_repos
