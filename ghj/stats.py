
from typing import List, Dict

def stats(repos: List[Dict]) -> Dict:
    """
    This function takes a list of repos as input and returns a dictionary
    with the following keys:
    - total_repos: the total number of repositories
    - total_stars: the total number of stars across all repositories
    - average_stars: the average number of stars per repository
    - most_starred_repo: the name of the repository with the most stars
    - most_starred_repo_stars: the number of stars of the most starred repository
    - most_recent_repo: the name of the most recently updated repository
    - most_recent_repo_stars: the number of stars of the most recently updated repository
    """
    
    # let's use JMESPath to query the data

    import jmespath

    query = {
        "total_repos": "length(@)",
        "total_stars": "sum(@[].stargazers_count)",
        "average_stars": "mean(@[].stargazers_count)",
        "most_starred_repo": "max_by(@, &stargazers_count).name",
        "most_starred_repo_stars": "max_by(@, &stargazers_count).stargazers_count",
        "most_recent_repo": "max_by(@, &updated_at).name",
        "most_recent_repo_stars": "max_by(@, &updated_at).stargazers_count",
    }

    result = {key: jmespath.search(query[key], repos) for key in query}
    return result