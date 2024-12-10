import os
import re
import requests
import json
import base64
import logging
import argparse
import time
import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def check_rate_limit(headers):
    resp = requests.get('https://api.github.com/rate_limit', headers=headers)
    if resp.status_code == 200:
        remaining = resp.json()['rate']['remaining']
        if remaining < 1:
            reset_time = resp.json()['rate']['reset']
            wait_time = max(reset_time - time.time(), 0)
            logging.info(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds")
            time.sleep(wait_time)
        return remaining
    return None

def fetch_with_retry(url, headers, params=None, max_retries=3):
    for attempt in range(max_retries):
        remaining = check_rate_limit(headers)
        if remaining:
            logging.debug(f"Rate limit remaining: {remaining}")
            
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            return resp
        elif resp.status_code == 403:
            wait_time = 2 ** attempt
            logging.info(f"Rate limited. Waiting {wait_time} seconds")
            time.sleep(wait_time)
            continue
    return resp

def get_headers(auth_token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if auth_token:
        headers["Authorization"] = f"token {auth_token}"
    return headers

def fetch_languages(username, repo_name, headers):
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    resp = fetch_with_retry(url, headers)
    if resp.status_code == 200:
        return list(resp.json().keys())
    return []

def fetch_github_repos(username, auth_token=None):
    repos = []
    page = 1
    headers = get_headers(auth_token)
    url = "https://api.github.com/user/repos" if auth_token else f"https://api.github.com/users/{username}/repos"

    while True:
        resp = fetch_with_retry(url, headers, params={'page': page, 'per_page': 10})
        if resp.status_code == 200:
            cur_repos = resp.json()
            if not cur_repos:
                break
            
            # Fetch languages for each repo
            for repo in cur_repos:
                repo['languages'] = fetch_languages(username, repo['name'], headers)
                time.sleep(0.1)
            
            repos.extend(cur_repos)
            page += 1
            time.sleep(0.1)
        else:
            logging.error(f"Error fetching repos: {resp.status_code}")
            logging.error(f"Response: {resp.json()}")
            break

    return repos

def extract_summary(readme_content):
    # For HTML comments approach
    pattern = r'<!-- summary-start -->(.*?)<!-- summary-end -->'
    match = re.search(pattern, readme_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # For YAML frontmatter approach  
    if readme_content.startswith('---'):
        parts = readme_content.split('---', 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            return front_matter.get('summary')
    
    # Default to first paragraph if no markers found
    paragraphs = readme_content.split('\n\n')
    return paragraphs[0] if paragraphs else ''

def extract_tags(readme_content):
   pattern = r'<!-- tags-start -->\s*\*\*Tags\*\*:\s*(.*?)\s*<!-- tags-end -->'
   match = re.search(pattern, readme_content, re.DOTALL)
   if match:
       tags_str = match.group(1)
       return [tag.strip() for tag in tags_str.split(',')]
   return []

def fetch_extra_repo_metadata(username, repo_name, auth_token=None):
    metadata = {}
    headers = get_headers(auth_token)

    contr_url = f"https://api.github.com/repos/{username}/{repo_name}/contributors"
    contr_resp = fetch_with_retry(contr_url, headers)
    if contr_resp.status_code == 200:
        metadata["contributors"] = [{"name": c['login'], "commits": c['contributions']} for c in contr_resp.json()]
    else:
        logging.warning(f"Failed to fetch contributors for {repo_name}: {contr_resp.status_code}")

    time.sleep(0.1)

    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    readme_resp = fetch_with_retry(readme_url, headers)
    if readme_resp.status_code == 200:
        readme_data = readme_resp.json()
        try:
            metadata["readme_content"] = base64.urlsafe_b64decode(readme_data['content']).decode('utf-8')
            metadata['summary'] = extract_summary(readme_data['content'])
            metadata['tags'] = extract_tags(readme_data['content'])

        except Exception as e:
            logging.error(f"Error decoding README for {repo_name}: {e}")
    else:
        logging.warning(f"Failed to fetch README for {repo_name}: {readme_resp.status_code}")

    return metadata

def write_hugo_project(repos, base_dir="./ghprojects"):
    os.makedirs(base_dir, exist_ok=True)

    # Sort repos by stars
    repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)

    # Create _index.md
    with open(os.path.join(base_dir, "_index.md"), "w") as f:
        f.write("---\n")
        f.write("title: GitHub Projects\n")
        f.write("layout: list\n")
        f.write("---\n")

    for repo in repos:
        logging.info(f"Writing project: {repo['name']}")
        repo_dir = os.path.join(base_dir, repo['name'])
        os.makedirs(repo_dir, exist_ok=True)
        
        frontmatter = {
            'title': repo['name'],
            'author': repo['owner']['login'],
            'email': repo['owner'].get('email', ''),
            'description': repo.get('description', ''),
            'date': repo['created_at'],
            'layout': 'project',
            'languages': repo.get('languages', []),
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'open_issues': repo.get('open_issues_count', 0),
            'links': [
                {'name': 'GitHub', 'url': repo['html_url']},
            ],
            'tags': repo.get('tags', []).extend(['GitHub', 'project']),
            'summary': repo.get('summary', '')            
        }

        if repo.get('has_pages', False):
            frontmatter['links'].append({
                'name': 'GitHub Pages',
                'url': f"https://{repo['owner']['login']}.github.io/{repo['name']}/"
            })

        # Check for featured image in repo contents
        if 'images' in repo:
            featured = next((img for img in repo['images'] if 'featured' in img.lower()), None)
            if featured:
                # Download and save featured image
                download_featured_image(featured, repo_dir)

        write_content_file(repo, repo_dir, frontmatter)

def write_content_file(repo, repo_dir, frontmatter):
   with open(os.path.join(repo_dir, "index.md"), "w") as f:
       # Write frontmatter
       f.write("---\n")
       f.write(yaml.dump(frontmatter, default_flow_style=False))
       f.write("---\n\n")
       
       # Project description at top
       if repo.get('description'):
           f.write(f"{repo['description']}\n\n")

       # Stats and metadata
       f.write(f"**Stars**: {repo['stargazers_count']} | ")
       f.write(f"**Forks**: {repo['forks_count']} | ")
       f.write(f"**Open Issues**: {repo['open_issues_count']}\n\n")
       
       if repo.get('languages'):
           f.write(f"**Languages**: {', '.join(repo['languages'])}\n\n")

       # Add contributors section if available
       if 'contributors' in repo:
           f.write("## Contributors\n")
           for contributor in repo['contributors']:
               f.write(f"- {contributor['name']} ({contributor['commits']} commits)\n")
           f.write("\n")

       # Add README content
       if 'readme_content' in repo:
           f.write(repo['readme_content'])        

def download_featured_image(url, repo_dir):
    resp = requests.get(url)
    if resp.status_code == 200:
        ext = url.split('.')[-1].lower()
        with open(os.path.join(repo_dir, f"featured.{ext}"), 'wb') as f:
            f.write(resp.content)

def fetch_extra_metadata(username, repos, auth_token=None):
    owner_data = fetch_owner_metadata(username, auth_token=auth_token)
    repos_data = []
    n = len(repos)
    for k, repo in enumerate(repos, 1):
        logging.info(f"Fetching extra metadata for {username}/{repo['name']} ({k}/{n})")
        repo_metadata = fetch_extra_repo_metadata(
            username, repo['name'], auth_token=auth_token)
        
        # Update with owner metadata. Don't override existting `owner` key
        if owner_data:
            repo['owner'] = {**owner_data, **repo.get('owner', {})}

        # why not just use repo['owner'].update(owner_data) ?
        # answer: good point, an update would be cleaner and faster
        

        repo.update(repo_metadata)
        repos_data.append(repo)
        time.sleep(0.1)

    return repos_data

def fetch_owner_metadata(username, auth_token=None):
    headers = get_headers(auth_token)
    url = f"https://api.github.com/users/{username}"
    resp = fetch_with_retry(url, headers)
    
    if resp.status_code == 200:
        data = resp.json()
        return {
            'name': data.get('name'),
            'email': data.get('email'),
            'bio': data.get('bio'),
            'company': data.get('company'),
            'blog': data.get('blog'),
            'location': data.get('location'),
            'avatar_url': data.get('avatar_url')
        }
    return {}

def main():
    parser = argparse.ArgumentParser(description="Generate detailed GitHub repository JSON data.")
    parser.add_argument("username", type=str, help="GitHub username to retrieve repositories for")
    parser.add_argument("--auth-token", type=str, help="GitHub personal access token for accessing private repositories. Defaults to GITHUB_TOKEN environment variable.")
    parser.add_argument("--extra-metadata", action="store_true", help="Fetch extra metadata for each repository", default=True)
    parser.add_argument("--output-type", type=str, choices=['json', 'hugo'], default='json', help="Output type (json or hugo)")
    parser.add_argument("--output-dir", type=str, default="ghprojects", help="Output directory for Hugo content (when output-type is hugo)")
    parser.add_argument("--input-json", type=str, help="Input JSON file to use as data source. If provided, the script will not fetch data from GitHub.")
    parser.add_argument("--owner-metadata", action="store_true", help="Fetch owner metadata for the GitHub user", default=True)
    args = parser.parse_args()

    if args.input_json:
        with open(args.input_json, "r") as f:
            repos = json.load(f)
        
        if args.output_type != 'hugo':
            logging.warning("`--input-json <filename>` is used. It will output the loaded JSON data if `--output-type` is `json`, and will generate project files if `--output-type` is `hugo`.")

        if args.extra_metadata:
            logging.warning("`--extra-metadata` flag is ignored when using input JSON.")

        if args.auth_token:
            logging.warning("`--auth-token` flag is ignored when using input JSON.")


    else:
        auth_token = args.auth_token or os.getenv('GITHUB_TOKEN')
        if not auth_token:
            logging.warning("No GitHub token provided. Rate limits will be strict.")

        repos = fetch_github_repos(username=args.username, auth_token=auth_token)

        if args.owner_metadata:
            owner_metadata = fetch_owner_metadata(args.username, auth_token=auth_token)
            
        
        if args.extra_metadata:
            repos = fetch_extra_metadata(username=args.username, repos=repos, auth_token=auth_token)


    if args.output_type == 'hugo':
        write_hugo_project(repos, args.output_dir)
    else:
        print(json.dumps(repos, indent=2))

if __name__ == "__main__":
    main()