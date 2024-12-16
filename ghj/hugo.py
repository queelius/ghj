from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
import json
import shutil
import yaml
from datetime import datetime

class HugoRenderer:
    """Renders GitHub repository data as Hugo content pages"""
    
    def __init__(self, 
                 content_dir: str = "content/projects",
                 static_dir: str = "static/images",
                 template_dir: str = "ghj/templates"):
        self.content_dir = Path(content_dir)
        self.static_dir = Path(static_dir)
        self.template_dir = Path(template_dir)
        self.console = Console()

    def render_repos(self, repos: List[Dict], download_images: bool = True) -> None:
        """Render multiple repositories as Hugo content pages"""
        self.content_dir.mkdir(parents=True, exist_ok=True)
        if download_images:
            self.static_dir.mkdir(parents=True, exist_ok=True)

        for repo in repos:
            try:
                self.render_repo(repo, download_images)
            except Exception as e:
                self.console.print(f"[red]Error rendering {repo.get('full_name')}: {str(e)}[/red]")

    def render_repo(self, repo: Dict, download_images: bool = True) -> None:
        """Render a single repository as a Hugo content page"""
        # Create slug from repo name
        slug = repo.get('name', '').lower().replace(' ', '-')
        repo_dir = self.content_dir / slug
        repo_dir.mkdir(parents=True, exist_ok=True)

        # Prepare front matter
        front_matter = {
            'title': repo.get('name', ''),
            'date': repo.get('created_at', datetime.now().isoformat()),
            'description': repo.get('description', ''),
            'tags': repo.get('topics', []),
            'categories': [repo.get('language', 'Other')],
            'repository': repo.get('html_url', ''),
            'stars': repo.get('stargazers_count', 0),
            'forks': repo.get('forks_count', 0),
            'draft': False
        }

        # Handle images if present and requested
        if download_images and 'images' in repo:
            image_dir = self.static_dir / slug
            image_dir.mkdir(parents=True, exist_ok=True)
            
            images = []
            for idx, image_url in enumerate(repo['images']):
                try:
                    image_path = self._download_image(image_url, image_dir, f"image_{idx}")
                    if image_path:
                        images.append(str(image_path.relative_to(self.static_dir)))
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Failed to download image {image_url}: {e}[/yellow]")
            
            if images:
                front_matter['images'] = images

        # Generate content
        content = self._generate_content(repo, front_matter)
        
        # Write the file
        output_path = repo_dir / "index.md"
        output_path.write_text(content)
        self.console.print(f"[green]Generated Hugo content for {slug}[/green]")

    def _generate_content(self, repo: Dict, front_matter: Dict) -> str:
        """Generate the content of the Hugo markdown file"""
        # Convert front matter to YAML
        yaml_front_matter = yaml.dump(front_matter, default_flow_style=False)
        
        # Prepare content sections
        content_parts = [
            "---",
            yaml_front_matter.strip(),
            "---\n",
            f"# {repo.get('name', 'Untitled Repository')}\n",
        ]

        if repo.get('description'):
            content_parts.append(f"{repo['description']}\n")

        if repo.get('readme_content'):
            content_parts.append("## README\n")
            content_parts.append(repo['readme_content'])

        return "\n".join(content_parts)

    def _download_image(self, url: str, target_dir: Path, filename: str) -> Optional[Path]:
        """Download an image from URL to target directory"""
        # Implementation would go here
        # Returns relative path to the image from static directory
        pass
