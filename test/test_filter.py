# test_filter.py

import unittest
from ghj.filter_lang import filter_repos, FilterError
from sample_repos import sample_repos

class TestFilterRepos(unittest.TestCase):
    def setUp(self):
        """Initialize common variables for tests."""
        # Create a deep copy to prevent modifications affecting other tests
        import copy
        self.repos = copy.deepcopy(sample_repos)

    # -------------------
    # Test Basic Conditions
    # -------------------

    def test_eq_operator(self):
        """Test equality operator 'eq'."""
        query = ['language', 'eq', 'Python']
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_neq_operator(self):
        """Test not equal operator 'neq'."""
        query = ['language', 'neq', 'Python']
        result = filter_repos(self.repos, query)
        expected_ids = [2, 4, 5, 6]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_gt_operator(self):
        """Test greater than operator 'gt'."""
        query = ['stars', 'gt', 100]
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3, 4]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_gte_operator(self):
        """Test greater than or equal operator 'gte'."""
        query = ['forks', 'gte', 45]
        result = filter_repos(self.repos, query)
        expected_ids = [2, 3]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_lt_operator(self):
        """Test less than operator 'lt'."""
        query = ['stars', 'lt', 100]
        result = filter_repos(self.repos, query)
        expected_ids = [2, 5, 6]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_lte_operator(self):
        """Test less than or equal operator 'lte'."""
        query = ['forks', 'lte', 24]
        result = filter_repos(self.repos, query)
        expected_ids = [4, 5]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_in_operator(self):
        """Test 'in' operator for list membership."""
        query = ['language', 'in', 'Python']
        result = filter_repos(self.repos, query)
        expected_ids = [6]  # Only id=6 has 'language' as a list containing 'Python'
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_contains_operator(self):
        """Test 'contains' operator for substring in string fields."""
        query = ['name', 'contains', 'Data']
        result = filter_repos(self.repos, query)
        expected_ids = [1, 4]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_regex_operator(self):
        """Test 'regex' operator for pattern matching."""
        query = ['description', 'regex', '^A.*']
        result = filter_repos(self.repos, query)
        expected_ids = [1]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_startswith_operator(self):
        """Test 'startswith' operator."""
        query = ['name', 'startswith', 'Data']
        result = filter_repos(self.repos, query)
        expected_ids = [1, 4]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_endswith_operator(self):
        """Test 'endswith' operator."""
        query = ['name', 'endswith', 'Repo']
        # According to sample_repos.py:
        # id=1: 'DataScienceRepo' ends with 'Repo'
        # id=2: 'WebDevRepo' ends with 'Repo'
        # id=5: 'EmptyRepo' ends with 'Repo'
        expected_ids = [1, 2, 5, 6]
        result = filter_repos(self.repos, query)
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    # -------------------
    # Test Logical Operations
    # -------------------

    def test_and_operator(self):
        """Test 'and' logical operator."""
        query = [
            'and',
            ['stars', 'gt', 100],
            ['language', 'eq', 'Python']
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_or_operator(self):
        """Test 'or' logical operator."""
        query = [
            'or',
            ['language', 'eq', 'R'],
            ['forks', 'gt', 50]
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [3, 4]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_nested_logical_operators(self):
        """Test nested 'and'/'or' logical operators."""
        query = [
            'and',
            ['owner.active', 'eq', True],
            [
                'or',
                ['language', 'eq', 'Python'],
                ['language', 'eq', 'R']
            ],
            ['stars', 'gte', 120]
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3, 4]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    # -------------------
    # Test Dictionary-Based Queries
    # -------------------

    def test_dictionary_based_and_query(self):
        """Test 'and' logical operator using dictionary-based query."""
        query = {
            'and': [
                ['stars', 'gt', 100],
                ['language', 'eq', 'Python']
            ]
        }
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_dictionary_based_or_query(self):
        """Test 'or' logical operator using dictionary-based query."""
        query = {
            'or': [
                ['language', 'eq', 'JavaScript'],
                ['forks', 'gt', 50]
            ]
        }
        result = filter_repos(self.repos, query)
        expected_ids = [2, 3]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_dictionary_based_nested_query(self):
        """Test nested logical operators using dictionary-based query."""
        query = {
            'or': [
                {
                    'and': [
                        ['stars', 'gt', 100],
                        ['language', 'eq', 'Python']
                    ]
                },
                {
                    'and': [
                        ['forks', 'gt', 50],
                        ['language', 'eq', 'JavaScript']
                    ]
                }
            ]
        }
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3]  # Repo 2 has forks=45, which is not >50, hence excluded
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    # -------------------
    # Test Error Handling
    # -------------------

    def test_invalid_comparison_operator(self):
        """Test query with unsupported comparison operator."""
        query = ['stars', 'invalid_op', 100]
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    def test_invalid_logical_operator(self):
        """Test query with unsupported logical operator."""
        query = [
            'not',
            ['stars', 'gt', 100],
            ['language', 'eq', 'Python']
        ]
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    def test_incomplete_condition(self):
        """Test query with incomplete condition (missing value)."""
        query = ['stars', 'gt']
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    def test_empty_query(self):
        """Test empty query."""
        query = []
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    def test_non_list_non_dict_query(self):
        """Test query that is neither a list nor a dict."""
        query = "stars gt 100"
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    def test_type_mismatch(self):
        """Test condition with type mismatch (e.g., string vs int)."""
        query = ['stars', 'gt', 'one hundred']
        # Since 'stars' is an integer and 'one hundred' is a string, it should skip all repos due to TypeError
        result = filter_repos(self.repos, query)
        expected_ids = []  # No repos should match
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_unsupported_comparison_operator(self):
        """Test using an unsupported comparison operator."""
        query = ['stars', 'foo_op', 100]
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Edge Cases
    # -------------------

    def test_missing_field(self):
        """Test condition with a field that does not exist in repos."""
        query = ['nonexistent_field', 'eq', 'value']
        result = filter_repos(self.repos, query)
        self.assertEqual(len(result), 0)

    def test_null_field_value(self):
        """Test condition where the field value is None."""
        query = ['language', 'eq', None]
        result = filter_repos(self.repos, query)
        expected_ids = [5]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_empty_string_field(self):
        """Test condition where the field value is an empty string."""
        query = ['description', 'eq', '']
        result = filter_repos(self.repos, query)
        expected_ids = [5]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_boolean_field(self):
        """Test condition on a boolean field."""
        query = ['owner.active', 'eq', True]
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3, 4, 6]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_in_operator_with_non_list_field(self):
        """Test 'in' operator where the field is not a list."""
        # Add repositories where 'language' is not a list
        # For this test, ensure only repositories with 'language' as a list are matched
        query = ['language', 'in', 'Python']
        result = filter_repos(self.repos, query)
        expected_ids = [6]  # Only id=6 has 'language' as a list containing 'Python'
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_contains_operator_with_non_string_field(self):
        """Test 'contains' operator where the field is not a string."""
        query = ['stars', 'contains', '1']
        result = filter_repos(self.repos, query)
        # Since 'stars' is an integer, 'contains' should return False for all
        self.assertEqual(len(result), 0)

    # -------------------
    # Test Complex Queries
    # -------------------

    def test_complex_query_multiple_logical_operators(self):
        """Test a complex query with multiple nested logical operators."""
        query = [
            'and',
            [
                'or',
                ['language', 'eq', 'Python'],
                ['language', 'eq', 'JavaScript']
            ],
            ['stars', 'gt', 100],
            [
                'or',
                ['forks', 'gt', 50],
                ['owner.active', 'eq', True]
            ]
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_query_with_all_operators(self):
        """Test a query that uses all supported comparison operators."""
        # Add a repository that satisfies all conditions
        modified_repo = {
            'id': 6,
            'name': 'FullFeatureRepo',
            'language': ['Python', 'R'],
            'stars': 300,
            'forks': 100,
            'description': 'A repository with full feature set.',
            'owner': {
                'name': 'frank',
                'active': True
            }
        }
        self.repos.append(modified_repo)
        query = [
            'and',
            ['language', 'in', 'Python'],          # id=6
            ['name', 'contains', 'Repo'],           # id=1,2,5,6
            ['description', 'regex', '.*feature.*'],# id=6
            ['stars', 'gte', 100],                  # id=1,3,4,6
            ['forks', 'lte', 100],                  # id=1,2,3,4,5,6
            ['owner.active', 'eq', True]            # id=1,3,4,6
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [6]
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    # -------------------
    # Test Unsupported Operators
    # -------------------

    def test_unsupported_comparison_operator(self):
        """Test using an unsupported comparison operator."""
        query = ['stars', 'foo_op', 100]
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Multiple Conditions Without Logical Operators
    # -------------------

    def test_multiple_conditions_without_logical_operator(self):
        """Test multiple conditions without specifying a logical operator."""
        query = ['stars', 'gt', 100, 'language', 'eq', 'Python']
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Condition with Extra Elements
    # -------------------

    def test_condition_with_extra_elements(self):
        """Test a condition list with more than three elements."""
        query = ['stars', 'gt', 100, 'extra']
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Condition with Insufficient Elements
    # -------------------

    def test_condition_with_insufficient_elements(self):
        """Test a condition list with less than three elements."""
        query = ['stars', 'gt']
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Query with Non-List/Dictonary
    # -------------------

    def test_query_as_integer(self):
        """Test passing an integer as a query."""
        query = 12345
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    def test_query_as_none(self):
        """Test passing None as a query."""
        query = None
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Query with Empty List
    # -------------------

    def test_query_empty_list(self):
        """Test passing an empty list as a query."""
        query = []
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Query with Empty Dictionary
    # -------------------

    def test_query_empty_dict(self):
        """Test passing an empty dictionary as a query."""
        query = {}
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Query with Multiple Keys in Dictionary
    # -------------------

    def test_query_dict_with_multiple_keys(self):
        """Test passing a dictionary with multiple keys."""
        query = {
            'and': [
                ['stars', 'gt', 100]
            ],
            'or': [
                ['language', 'eq', 'Python']
            ]
        }
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

    # -------------------
    # Test Query with Non-List Operands in Dictionary
    # -------------------

    def test_query_dict_with_non_list_operands(self):
        """Test passing non-list operands in a dictionary-based query."""
        query = {
            'and': ['stars', 'gt', 100]
        }
        with self.assertRaises(FilterError):
            filter_repos(self.repos, query)

# -------------------
    # Test `not` Operator
    # -------------------

    def test_not_operator_basic(self):
        """Test 'not' operator on a simple condition."""
        query = [
            'not',
            ['language', 'eq', 'Python']
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [2, 4, 5, 6]  # Repositories not using 'Python'
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_not_operator_with_and(self):
        """Test 'not' operator combined with 'and'."""
        query = [
            'and',
            ['stars', 'gt', 100],
            [
                'not',
                ['language', 'eq', 'Python']
            ]
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [4]  # No repository has stars > 100 and language not 'Python'
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_not_operator_with_or(self):
        """Test 'not' operator combined with 'or'."""
        query = [
            'or',
            ['language', 'eq', 'R'],
            [
                'not',
                ['stars', 'gt', 100]
            ]
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [2, 4, 5, 6]  # Repositories with language 'R' or stars <= 100
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_not_operator_nested(self):
        """Test nested 'not' operators."""
        query = [
            'not',
            [
                'not',
                ['language', 'eq', 'Python']
            ]
        ]
        result = filter_repos(self.repos, query)
        expected_ids = [1, 3]  # Double negation cancels out
        self.assertEqual([repo['id'] for repo in result], expected_ids)

    def test_not_operator_with_logical_operations(self):
        """Test 'not' operator with combined logical operations."""
        query = [
            'and',
            ['stars', 'gt', 100],
            [
                'or',
                ['language', 'eq', 'Python'],
                [
                    'not',
                    ['forks', 'gt', 50]
                ]
            ]
        ]
        result = filter_repos(self.repos, query)
        # Expected:
        # Repository must have stars > 100
        # AND (language == Python OR NOT forks > 50)
        # Repositories:
        # id=1: stars=150 >100, language=Python, forks=30 <=50 → included
        # id=3: stars=200 >100, language=Python, forks=60 >50 → included
        # id=4: stars=120 >100, language=R, forks=20 <=50 → included
        expected_ids = [1, 3, 4]
        self.assertEqual([repo['id'] for repo in result], expected_ids)


# -------------------
# Run the Tests
# -------------------

if __name__ == '__main__':
    unittest.main()
