# tmp.py

from ghj.filter_lang import filter_repos, FilterError

sample_repos = [
    {
        'id': 1,
        'name': 'DataScienceRepo',
        'language': 'Python',
        'stars': 150,
        'forks': 30,
        'description': 'A repository for data science projects.',
        'owner': {
            'name': 'alice',
            'active': True
        }
    },
    {
        'id': 2,
        'name': 'WebDevRepo',
        'language': 'JavaScript',
        'stars': 80,
        'forks': 45,
        'description': 'Repository for web development.',
        'owner': {
            'name': 'bob',
            'active': False
        }
    },
    {
        'id': 3,
        'name': 'MachineLearning',
        'language': 'Python',
        'stars': 200,
        'forks': 60,
        'description': 'Machine learning algorithms and models.',
        'owner': {
            'name': 'carol',
            'active': True
        }
    },
    {
        'id': 4,
        'name': 'DataVisualization',
        'language': 'R',
        'stars': 120,
        'forks': 20,
        'description': 'Tools for data visualization.',
        'owner': {
            'name': 'dave',
            'active': True
        }
    },
    {
        'id': 5,
        'name': 'EmptyRepo',
        'language': None,
        'stars': 0,
        'forks': 0,
        'description': '',
        'owner': {
            'name': 'eve',
            'active': False
        }
    }
]

def main():
    try:
        # Add repository 6
        sample_repos.append({
            'id': 6,
            'name': 'FullFeatureRepo',
            'language': ['Python', 'JavaScript'],
            'stars': 250,
            'forks': 80,
            'description': 'A repository with full feature set.',
            'owner': {
                'name': 'frank',
                'active': True
            }
        })

        # AST-based Query
        query_ast = ['language', 'eq', 'Python']
        filtered_ast = filter_repos(sample_repos, query_ast)
        print("AST-based Query Result:", [repo['id'] for repo in filtered_ast])

        # DSL Query
        query_dsl = 'language eq "Python" AND stars gt 100'
        filtered_dsl = filter_repos(sample_repos, query_dsl, is_dsl=True)
        print("DSL Query Result:", [repo['id'] for repo in filtered_dsl])

        # Complex DSL Query with NOT and Parentheses
        query_dsl_complex = 'NOT language eq "R" AND (stars gt 100 OR forks gt 50)'
        filtered_dsl_complex = filter_repos(sample_repos, query_dsl_complex, is_dsl=True)
        print("Complex DSL Query Result:", [repo['id'] for repo in filtered_dsl_complex])

        # DSL Query with 'in' operator
        query_dsl_in = 'language in "Python"'
        filtered_dsl_in = filter_repos(sample_repos, query_dsl_in, is_dsl=True)
        print("DSL 'in' Operator Query Result:", [repo['id'] for repo in filtered_dsl_in])
        # Expected Output: [6] since 'language' is a list containing "Python"

        # DSL Query with 'NOT'
        query_dsl_not = 'NOT language eq "JavaScript" AND stars gt 100'
        filtered_dsl_not = filter_repos(sample_repos, query_dsl_not, is_dsl=True)
        print("DSL 'NOT' Operator Query Result:", [repo['id'] for repo in filtered_dsl_not])
        # Expected Output: [1, 3, 4, 6] (excluding repository 2 and 5)

        # DSL Query with 'contains' operator
        query_dsl_contains = 'description contains "data"'
        filtered_dsl_contains = filter_repos(sample_repos, query_dsl_contains, is_dsl=True)
        print("DSL 'contains' Operator Query Result:", [repo['id'] for repo in filtered_dsl_contains])
        # Expected Output: [1, 4]

    except FilterError as e:
        print(f"Filter Error: {e}")

if __name__ == "__main__":
    main()
