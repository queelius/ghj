# GitHub to Hugo Integration Tool

This project provides a two-step pipeline for fetching GitHub repository metadata as JSON and then converting it into Hugo-compatible content for a static site.

## Overview

1. **GitHub Fetch User**:
   A Python script `gh_fetch_user.py` fetches user repositories from GitHub’s API and outputs their metadata as a JSON file. This tool:
   - Uses a GitHub personal access token (optional) for private repos.
   - Fetches basic repo metadata and (optionally) extra metadata like contributors, README content, images, etc.
   - Outputs a single JSON file to standard output.

2. **GitHub Fetch Repo**:
   A Python script `gh_fetch_repo.py` fetches a single repository’s metadata from GitHub’s API and outputs it as JSON. This tool:
   - Fetches basic repo metadata and (optionally) extra metadata like contributors, README content, images, etc.
   - Outputs a single JSON file to standard output.

3. **JSON Tools**:
   A Python script (e.g., `gh_json.py`) provides utilities for working with GitHub JSON data:
   - Merging multiple JSON files into a single file.
   - Filtering JSON data by tags, languages, etc.
   - Sorting JSON data by stars, forks, etc.

4. **Hugo Render**:
   Another Python script (`gh_hugo.py`) takes the JSON file and converts each repository into a Hugo content page under `content/projects/`.
   - Optionally downloads a featured image for each repo if an image URL is provided.
   - Generates a `index.md` file with Hugo front matter, referencing the repo’s metadata, and places images in `static/images/<repo_name>/`.
   - Also supports a simple Markdown listing mode if you don’t want Hugo front matter.

3. **Hugo Layouts**:  
   The included Hugo layout files (`listings.html` and `ghproject.html`) define how these project pages are displayed on your Hugo site.
   - `listings.html` shows an overview of all projects.
   - `ghproject.html` displays a single project’s details, including featured image, links, tags, etc.
   
   These layouts are meant to be used with a Hugo project (e.g., using the Ananke theme) and placed in `layouts/ghprojects/`.

## Prerequisites

- **Python 3.6+**
- **Hugo** static site generator (installed and configured)
- **GitHub Personal Access Token (optional)** if you need private repositories or higher rate limits.

## Installation

1. **Python Tools:**
   Install the Python package:
   ```bash
   pip install .
   ```
   This installs the `gh_hugo_toolkit` and console scripts.

2. **Hugo Setup:**
   - Create a new Hugo site if you haven’t already:
     ```bash
     hugo new site myhugosite
     ```
   - Add the Ananke theme (or ensure it’s already present):
     ```bash
     cd myhugosite
     git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
     ```
   - Place the `listings.html` and `ghproject.html` files into `myhugosite/layouts/ghprojects/`.

## Usage

### Step 1: Fetch GitHub Repositories as JSON

Run the fetch tool to get all public repos from a user:

```bash
gh_fetch_user username > pub-repos.json
```

Or with private repos and extra metadata:

```bash
gh_fetch_user username --auth-token <YOUR_TOKEN> --no-public --private --extra-metadata > priv-repos.json
```

### Step 2: Render JSON to Hugo Content

Once you have `pub-repos.json`, run the renderer:

```bash
gh-hugo pub-repos.json
```

This will:
- Create `content/projects/<repo-name>/index.md` for each repo.
- Download the first image as `static/images/<repo-name>/featured.png` if available.

### Integrating with Hugo

Run Hugo to build your site:

```bash
hugo server
```

Navigate to `http://localhost:1313/` to see your projects listed.

- The `listings.html` layout works with `_index.md` in `content/projects/`.
- Each project page uses `ghproject.html` to display details.

## Requirements & Assumptions

- The `gh_hugo.py` script expects JSON from `gh_fetch_user.py` or `gh_fetch_repo.py`.
- The JSON should contain `name`, `description`, `stargazers_count`, `open_issues_count`, `languages`, `readme_content`, and optionally `images`.
- `gh_hugo.py` will try to download images if provided as absolute URLs.
- The Hugo layouts assume `featured.png` as a featured image. This is created by `gh_hugo.py` if an image is available.
- The Ananke theme may be customized; the provided layouts are minimal and may be adapted as needed.

## Contributing

Feel free to open issues or submit PRs to improve the scripts or Hugo layouts.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
