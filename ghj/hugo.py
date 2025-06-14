from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json
import shutil
import yaml
import requests
from jinja2 import Environment, FileSystemLoader, Template
from rich.console import Console

# A simple slugify helper (you might replace this with a library like python-slugify)
def slugify(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in text).strip("-")

class HugoRenderer:
    """Renders GitHub repository data as Hugo content pages."""

    def __init__(
        self, 
        content_dir: str = "content/projects",
        static_dir: str = "static/images",
        template_dir: str = "ghj/templates"
    ):
        self.content_dir = Path(content_dir)
        self.static_dir = Path(static_dir)
        self.template_dir = Path(template_dir)
        self.console = Console()

        # Prepare the Jinja2 environment.
        if self.template_dir.exists():
            self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        else:
            # Fallback template if no template directory exists.
            self.env = Environment(loader=FileSystemLoader("."))

    def render_repos(self, repos: List[Dict], download_images: bool = True) -> None:
        """Render multiple repositories as Hugo content pages."""
        self.content_dir.mkdir(parents=True, exist_ok=True)
        if download_images:
            self.static_dir.mkdir(parents=True, exist_ok=True)

        for repo in repos:
            try:
                self.render_repo(repo, download_images)
            except Exception as e:
                self.console.print(f"[red]Error rendering {repo.get('full_name')}: {str(e)}[/red]")

    def render_repo(self, repo: Dict, download_images: bool = True) -> None:
        """Render a single repository as a Hugo content page."""
        slug = slugify(repo.get("name", ""))
        repo_dir = self.content_dir / slug
        repo_dir.mkdir(parents=True, exist_ok=True)

        # Prepare front matter. You can expand these fields as needed.
        front_matter = {
            "title": repo.get("name", ""),
            "date": self._format_date(repo.get("created_at")),
            "updated": self._format_date(repo.get("updated_at", datetime.now().isoformat())),
            "description": repo.get("description", ""),
            "tags": repo.get("topics", []),
            "categories": [repo.get("language", "Other")],
            "repository": repo.get("html_url", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "draft": False,
            # You can add more fields like 'license', 'issues', etc.
        }

        # Handle images if requested.
        if download_images and "images" in repo:
            image_dir = self.static_dir / slug
            image_dir.mkdir(parents=True, exist_ok=True)
            images = []
            for idx, image_url in enumerate(repo["images"]):
                try:
                    image_path = self._download_image(image_url, image_dir, f"image_{idx}")
                    if image_path:
                        # Store path relative to static directory
                        images.append(str(image_path.relative_to(self.static_dir)))
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Failed to download image {image_url}: {e}[/yellow]")
            if images:
                front_matter["images"] = images

        # Render content using a template.
        content = self._generate_content(repo, front_matter)

        # Write to file.
        output_path = repo_dir / "index.md"
        output_path.write_text(content, encoding="utf-8")
        self.console.print(f"[green]Generated Hugo content for {slug}[/green]")

    def _format_date(self, date_str: Optional[str]) -> str:
        """Format the date in a standard format for Hugo."""
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.rstrip("Z"))
                return dt.isoformat()
            except Exception:
                pass
        return datetime.now().isoformat()

    def _generate_content(self, repo: Dict, front_matter: Dict) -> str:
        """Generate the content of the Hugo markdown file using Jinja2."""
        # Convert front matter to YAML.
        yaml_front = yaml.dump(front_matter, default_flow_style=False, sort_keys=False)
        # Try to load a template file from the template_dir; fallback to a default.
        try:
            template: Template = self.env.get_template("repo_template.md")
        except Exception:
            default_template = (
                "---\n"
                "{{ front_matter }}\n"
                "---\n\n"
                "{% if repo.description %}{{ repo.description }}\n\n{% endif %}"
                "{% if repo.readme %}{{ repo.readme }}\n{% endif %}"
            )
            template = self.env.from_string(default_template)
        # Render the template.
        content = template.render(front_matter=yaml_front, repo=repo)
        return content

    def _download_image(self, url: str, target_dir: Path, filename: str) -> Optional[Path]:
        """Download an image from URL to target directory using requests."""
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                ext = url.split('.')[-1].split('?')[0]  # crude extension extraction
                target_path = target_dir / f"{filename}.{ext}"
                with open(target_path, "wb") as f:
                    shutil.copyfileobj(response.raw, f)
                return target_path
            else:
                raise Exception(f"HTTP status {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to download {url}: {e}")
