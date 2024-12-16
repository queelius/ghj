import sys
import os
import json
import yaml
import argparse
import requests
from .utils import logger

def write_hugo_projects(repos, base_dir="content/projects", static_dir="static/images"):
    """
    Writes each repository as a Hugo-compatible Markdown file in `content/projects/<repo_name>/index.md`.
    Images are downloaded into `static/images/<repo_name>/` if `images` field is present.
    """
    os.makedirs(base_dir, exist_ok=True)
    # Write _index.md for Hugo section listing
    index_path = os.path.join(base_dir, "_index.md")
    if not os.path.exists(index_path):
        with open(index_path, "w") as f:
            f.write("---\n")
            f.write("title: GitHub Projects\n")
            f.write("layout: list\n")
            f.write("---\n")

    for repo in repos:
        repo_name = repo.get("name")
        if not repo_name:
            logger.warning("Skipping a repository without a 'name' field.")
            continue

        repo_dir = os.path.join(base_dir, repo_name)
        os.makedirs(repo_dir, exist_ok=True)

        # Prepare front matter
        frontmatter = {
            'title': repo_name,
            'author': repo.get('owner', {}).get('login', ''),
            'description': repo.get('description', ''),
            'date': repo.get('created_at', ''),
            'layout': 'project',
            'languages': repo.get('languages', []),
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'open_issues': repo.get('open_issues_count', 0),
            'links': [
                {'name': 'GitHub', 'url': repo.get('html_url', '')},
            ],
            'tags': repo.get('tags', ['GitHub', 'project']),
            'summary': repo.get('summary', '')
        }

        # Add GitHub Pages link if available
        if repo.get('has_pages', False):
            frontmatter['links'].append({
                'name': 'GitHub Pages',
                'url': f"https://{repo.get('owner', {}).get('login', '')}.github.io/{repo_name}/"
            })

        # Attempt to download images if available
        images = repo.get('images', [])
        featured_image_path = None
        if images:
            # Just handle first image as "featured" for demonstration
            first_image = images[0]
            # Ensure full image URL or skip if not a valid URL
            if first_image.startswith('http://') or first_image.startswith('https://'):
                featured_image_path = download_image(first_image, static_dir, repo_name)
            else:
                logger.warning(f"Image '{first_image}' is not a URL. Skipping image download.")

        if featured_image_path:
            rel_image_path = os.path.relpath(featured_image_path, start=os.getcwd())
            # Hugo static files are referenced from '/', remove 'static/' prefix
            rel_image_web_path = '/' + '/'.join(rel_image_path.split(os.sep)[1:])
            frontmatter['featured_image'] = rel_image_web_path

        # Write the content file
        write_repo_markdown(repo, repo_dir, frontmatter)

def write_repo_markdown(repo, repo_dir, frontmatter):
    """
    Writes a single repo as a Markdown file (with frontmatter) suitable for Hugo.
    """
    index_path = os.path.join(repo_dir, "index.md")
    with open(index_path, "w") as f:
        f.write("---\n")
        yaml.dump(frontmatter, f, default_flow_style=False)
        f.write("---\n\n")

        # Basic repo info
        desc = repo.get('description', '')
        if desc:
            f.write(f"{desc}\n\n")

        f.write(f"**Stars**: {repo.get('stargazers_count',0)} | ")
        f.write(f"**Forks**: {repo.get('forks_count',0)} | ")
        f.write(f"**Open Issues**: {repo.get('open_issues_count',0)}\n\n")

        # Languages
        langs = repo.get('languages', [])
        if langs:
            f.write(f"**Languages**: {', '.join(langs)}\n\n")

        # Contributors
        contributors = repo.get('contributors', [])
        if contributors:
            f.write("## Contributors\n")
            for c in contributors:
                f.write(f"- {c['name']} ({c['commits']} commits)\n")
            f.write("\n")

        # README content
        readme_content = repo.get('readme_content', '')
        if readme_content:
            f.write(readme_content)

def download_image(url, static_dir, repo_name):
    """
    Downloads an image from a URL and saves it into `static/images/<repo_name>/`.
    Returns the local file path if successful, or None otherwise.
    """
    repo_img_dir = os.path.join(static_dir, repo_name)
    os.makedirs(repo_img_dir, exist_ok=True)
    filename = os.path.basename(url)
    local_path = os.path.join(repo_img_dir, filename)

    logger.info(f"Downloading image {url} -> {local_path}")
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(local_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return local_path
    else:
        logger.warning(f"Failed to download image: {url} (status {resp.status_code})")
        return None

