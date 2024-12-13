from typing import List, Dict
from collections import Counter
import jmespath

def get_statistics(repos: List[Dict]) -> Dict:
    """Calculate comprehensive statistics for GitHub repositories.
    
    Stats include:
    - Basic counts (repos, stars, forks)
    - Language distribution
    - Size metrics
    - Activity metrics
    - Owner stats
    """
    basic_query = {
        "total_repos": "length(@)",
        "total_stars": "sum(@[].stargazers_count)",
        "total_forks": "sum(@[].forks_count)",
        "total_watchers": "sum(@[].watchers_count)",
        "total_size_kb": "sum(@[].size)",
        
        # Most starred
        "most_starred_repo": "max_by(@, &stargazers_count).name",
        "most_starred_repo_stars": "max_by(@, &stargazers_count).stargazers_count",
        
        # Most recent
        "most_recent_repo": "max_by(@, &updated_at).name",
        "most_recent_update": "max_by(@, &updated_at).updated_at",
        
        # Largest
        "largest_repo": "max_by(@, &size).name",
        "largest_repo_size_kb": "max_by(@, &size).size",
        
        # Most forked
        "most_forked_repo": "max_by(@, &forks_count).name",
        "most_forked_count": "max_by(@, &forks_count).forks_count",
        
        # Averages
        "avg_stars": "avg(@[].stargazers_count)",
        "avg_forks": "avg(@[].forks_count)",
        "avg_size_kb": "avg(@[].size)",
        
        # Counts by type
        "public_repos": "length([?visibility=='public'])",
        "private_repos": "length([?visibility=='private'])",
        "forks": "length([?fork==`true`])",
        "sources": "length([?fork==`false`])",
    }

    # Get basic stats
    result = {key: jmespath.search(query, repos) for key, query in basic_query.items()}
    
    # Add language stats
    languages = [repo.get('language') for repo in repos if repo.get('language')]
    lang_counter = Counter(languages)
    result.update({
        "languages": {
            "total_languages": len(lang_counter),
            "language_counts": dict(lang_counter.most_common()),
            "top_language": lang_counter.most_common(1)[0][0] if lang_counter else None,
        }
    })
    
    # Add topic stats
    topics = [topic for repo in repos 
             for topic in repo.get('topics', []) 
             if topic]
    topic_counter = Counter(topics)
    result.update({
        "topics": {
            "total_topics": len(topic_counter),
            "topic_counts": dict(topic_counter.most_common(10)),  # Top 10 topics
        }
    })
    
    # Add license stats
    licenses = [repo.get('license', {}).get('spdx_id') 
               for repo in repos 
               if repo.get('license')]
    license_counter = Counter(licenses)
    result.update({
        "licenses": {
            "total_licensed": len(licenses),
            "license_counts": dict(license_counter.most_common()),
        }
    })
    
    # Add age/activity stats
    result.update({
        "activity": {
            "has_issues": sum(1 for repo in repos if repo.get('has_issues', False)),
            "has_wiki": sum(1 for repo in repos if repo.get('has_wiki', False)),
            "has_pages": sum(1 for repo in repos if repo.get('has_pages', False)),
            "archived": sum(1 for repo in repos if repo.get('archived', False)),
            "disabled": sum(1 for repo in repos if repo.get('disabled', False)),
        }
    })

    # Owner statistics
    owner_stats = {
        "unique_owners": len(set(repo['owner']['login'] for repo in repos)),
        "owner_types": Counter(repo['owner']['type'] for repo in repos),
        "admin_count": sum(1 for repo in repos if repo['owner'].get('site_admin', False)),
    }
    result["owner_stats"] = owner_stats

    # URL availability 
    url_stats = {
        "has_wiki_url": sum(1 for repo in repos if 'wiki_url' in repo),
        "has_issues_url": sum(1 for repo in repos if 'issues_url' in repo),
        "has_downloads_url": sum(1 for repo in repos if 'downloads_url' in repo),
    }
    result["url_stats"] = url_stats

    # Repository characteristics
    repo_chars = {
        "default_branches": Counter(repo.get('default_branch', 'unknown') for repo in repos),
        "has_downloads": sum(1 for repo in repos if repo.get('has_downloads', False)),
        "allows_forking": sum(1 for repo in repos if repo.get('allow_forking', False)),
        "has_projects": sum(1 for repo in repos if repo.get('has_projects', False)),
    }
    result["repo_characteristics"] = repo_chars

    # Git access stats
    git_stats = {
        "git_types": {
            "ssh": sum(1 for repo in repos if repo.get('ssh_url')),
            "git": sum(1 for repo in repos if repo.get('git_url')),
            "clone": sum(1 for repo in repos if repo.get('clone_url')),
        }
    }
    result["git_stats"] = git_stats

    result.update({
        "history": {
            "total_commits": sum(repo.get('commits_count', 0) for repo in repos),
            "avg_commits": sum(repo.get('commits_count', 0) for repo in repos) / len(repos) if repos else 0,
            "oldest_repo": min((repo.get('created_at', '') for repo in repos), default=''),
            "newest_repo": max((repo.get('created_at', '') for repo in repos), default=''),
            "last_pushed": max((repo.get('pushed_at', '') for repo in repos), default=''),
        }
    })

    # Add contributor stats
    result.update({
        "contributors": {
            "total_contributors": sum(len(repo.get('contributors', [])) for repo in repos),
            "avg_contributors": sum(len(repo.get('contributors', [])) for repo in repos) / len(repos) if repos else 0,
            "unique_contributors": len({
                contrib['login'] 
                for repo in repos 
                for contrib in repo.get('contributors', [])
            }),
            "top_contributors": Counter(
                contrib['login']
                for repo in repos
                for contrib in repo.get('contributors', [])
            ).most_common(10),
        }
    })

    # Add branch stats
    result.update({
        "branches": {
            "total_branches": sum(len(repo.get('branches', [])) for repo in repos),
            "avg_branches": sum(len(repo.get('branches', [])) for repo in repos) / len(repos) if repos else 0,
            "default_branches": Counter(
                repo.get('default_branch', 'unknown') for repo in repos
            ).most_common(),
            "protected_branches": sum(
                sum(1 for branch in repo.get('branches', []) if branch.get('protected', False))
                for repo in repos
            ),
        }
    })

    # Add collaboration metrics
    result.update({
        "collaboration": {
            "open_issues": sum(repo.get('open_issues_count', 0) for repo in repos),
            "open_prs": sum(len(repo.get('pull_requests', [])) for repo in repos),
            "merged_prs": sum(
                sum(1 for pr in repo.get('pull_requests', []) if pr.get('merged_at'))
                for repo in repos
            ),
            "total_releases": sum(len(repo.get('releases', [])) for repo in repos),
            "avg_time_to_merge": None,  # Would need PR timeline data
        }
    })

    return result