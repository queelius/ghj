# `ghj`: GitHub JSON

NOTE: This is incomplete. Consider it an early alpha.

This project provides a pipeline for fetching GitHub repository metadata as JSON
along with a set of tools to filter, sort, query, merge, and render this data into a Hugo
content. Additionally, it comes with a dashboard `ghj dash` to visualize and
query the data, including an LLM (Large Language Model) for asking questions
about the repositories.

## Overview

The `ghj` toolkit consists of several tools. Optionally, a GitHub personal access token for private repos and higher rate limits.

- **Fetch User**: `ghj fetch user` fetches all the repository metadata for a particular user.
  - Fetches basic repo metadata and (optionally) extra metadata like contributors, README content, images, etc.
  - Outputs JSON to standard output.
- **Fetch Repo**: `ghj fetch repo` fetches a single repository’s metadata.
  - Fetches basic repo metadata and (optionally) extra metadata like contributors, README content, images, etc.
  - Outputs JSON to standard output.
- **Repo Sets**: `ghj sets diff`, `ghj sets union`, `ghj sets intersect` for set-like operations on JSON files.
  - Merging multiple JSON repos.
  - Set-difference between JSON repos, e.g., `ghj diff repo1.json repo2.json repo3.json` to get repos in `repo1.json` but not in `repo2.json` and `repo3.json`.
  - Intersection of JSON repos, e.g., `ghj intersect repo1.json repo2.json repo3.json repo4.json` to get repos that are common to `repo1.json`, `repo2.json`, `repo3.json`, and `repo4.json`.
- **Dashboard**: `ghj dash` is a dashboard for visualizing and querying the repository data.
  - A web-based dashboard for querying and visualizing the repository data.
  - Includes a Large Language Model (LLM) for asking questions about the repositories.
- **Filter**: `ghj filter` is an advanced filter of repositories. See `jaf` (JSON Array FIlter),
  - E.g., `ghj filter :starscount gt? 1000 AND forks gt? 100 AND (lower-case :owner.login) eq? alex` to filter repositories with stars greater than 1000, forks greater than 100, and owned by `alex` (case-insensitive).
  - It  also supports a programmatic filter query based on nested lists:
    - `['and', ['?gt', ['path', 'starscount'], 1000], ['gt?', ['path', 'forks'], 100], ['eq?', ['lower-case', ['path','owner.login'], 'alex']]`
- **`gh_repo_filter`**: A command-line tool designed to filter GitHub repository JSON data using [JMESPath](https://jmespath.org/) queries. (Details below)
- **Stats**: `ghj stats` provides basic statistics about the repositories.
  - E.g., total number of repositories, average stars, forks, etc.
- **Sort**: `ghj sort` sorts repositories by stars, forks, etc.
- **LLM**: `ghj llm` for asking an LLM about the repositories.
- **Hugo**: `ghj hugo` takes the JSON file and converts each repository into a Hugo content page under `content/projects/`.
  - Optionally downloads a featured image for each repo if an image array `images` is contained in the JSON data for that repo.
  - Generates a `index.md` file with Hugo front matter, referencing the repo’s metadata, and places images in `static/images/<repo_name>/`.
  - Also supports a simple Markdown listing mode if you don’t want Hugo front matter.
  - The included Hugo layout files (`listings.html` and `ghproject.html`) define how these project pages are displayed on your Hugo site.
    - `listings.html` shows an overview of all projects.
    - `ghproject.html` displays a single project’s details, including featured image, links, tags, etc.

## Prerequisites

- **Python 3.6+**
- **GitHub Personal Access Token (optional)** if you need private repositories or higher rate limits.

## Installation

- **Python Tools:** Install the Python package:
  
  ```bash
  pip install ghj
  ```

  This installs the `ghj` Python package and its command-line tool `ghj`.

- **Hugo Setup:** Add the Ananke theme (or ensure it’s already present):

   ```bash
   cd myhugosite
   git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke.git themes/ananke
   ```

   Place the `listings.html` and `project.html` files into `myhugosite/layouts/projects/`.

## `gh_repo_filter`: Filter GitHub Repositories with JMESPath

### Motivation

`gh_repo_filter` is a command-line tool designed to filter GitHub repository JSON data using [JMESPath](https://jmespath.org/) queries. It allows you to efficiently search and extract repositories that meet specific criteria without the need to write additional code. This tool is especially helpful when working with large datasets fetched from GitHub's API.

By leveraging JMESPath, you can perform complex filtering operations directly from the command line, making data analysis and processing more streamlined.

### Installation

Ensure you have Python 3 installed. You can install `gh_repo_filter` via PyPI:

```bash
pip install gh_repo_filter
```

This will install the `gh_repo_filter` command-line tool accessible from your terminal.

### Usage

```bash
gh_repo_filter [input_file] <query> [-o output_file]
```

- `input_file`: (Optional) Path to the input JSON file. Use `-` or omit to read from stdin.
- `<query>`: JMESPath query string to filter the data.
- `-o output_file`: (Optional) Write output to a file. Defaults to stdout if not provided.

#### Reading from stdin and stdout

The tool supports reading input from stdin and writing output to stdout, enabling easy integration with other command-line tools via pipelines.

### Examples

#### Example 1: Filter repositories by language

Filter repositories where the primary language is Python.

```bash
gh_repo_filter repos.json "language == 'Python'" > python_repos.json
```

Using stdin:

```bash
cat repos.json | gh_repo_filter 'language == "Python"' > python_repos.json
```

#### Example 2: Filter repositories with more than 50 stars

```bash
gh_repo_filter repos.json 'stargazers_count > `50`' > popular_repos.json
```

#### Example 3: Filter repositories updated after a specific date

```bash
gh_repo_filter repos.json 'updated_at > "2023-01-01T00:00:00Z"'
```

#### Example 4: Filter repositories where the name contains "tool"

```bash
gh_repo_filter repos.json "contains(name, 'tool')"
```

#### Example 5: Filter repositories that are not forks

```bash
gh_repo_filter repos.json 'fork == `false`'
```

#### Example 6: Combine multiple filters

Filter repositories that are in Python and have more than 50 stars.

```bash
gh_repo_filter repos.json 'language == "Python" && stargazers_count > `50`'
```

Equivalently, we could have piped the output of the first filter to the second filter:

```bash
gh_repo_filter repos.json 'language == "Python"' | gh_repo_filter 'stargazers_count > `50`'
```

#### Example 7: Filter repositories with a specific topic

Assuming your repository data includes a `topics` list, filter repositories that contain the topic "data-science".

```bash
gh_repo_filter repos.json "contains(topics, 'data-science')"
```

#### Example 8: Using stdin and stdout in a pipeline

Fetch repositories from the GitHub API and filter them on the fly.

```bash
curl 'https://api.github.com/users/username/repos' | gh_repo_filter - "language == 'JavaScript'" > js_repos.json
```

#### Example 9: More complex queries

Filter repositories where the language is either Python or JavaScript and have more than 100 stars.

```bash
gh_repo_filter repos.json '(language == "Python" || language == "JavaScript") && stargazers_count > `100`'
```

### Notes

- The input JSON data should be an array of repository objects, as returned by GitHub API endpoints like `/users/{username}/repos`. We
provide a custom tools like `gh_repo_user` to fetch repository data from GitHub API endpoints, augmented with additional metadata.
- **Numeric literals**: Enclose numeric values in backticks (e.g., `` `50` ``) when used in comparisons.
- **String literals**: Enclose strings in quotes (e.g., `'Python'` or `"Python"`). Use single quotes to avoid needing to escape backticks.
- **Logical operators**:
  - `&&` for logical AND
  - `||` for logical OR
  - `!` for logical NOT
- **Comparison operators**:
  - `==` equal
  - `!=` not equal
  - `>` greater than
  - `>=` greater than or equal to
  - `<` less than
  - `<=` less than or equal to

### Additional Resources

- **JMESPath Tutorial**: [https://jmespath.org/tutorial.html](https://jmespath.org/tutorial.html)  
  Learn how to craft complex queries to manipulate and extract JSON data.
- [`gh_repo_json`](./GH_REPO_JSON.md): Information on the structure of the JSON repository data fetched by tools like `gh_repo_user` or just using the GitHub endpoints directly.

## Hugo Usage

### Step 1: Fetch GitHub Repositories as JSON

Run the fetch tool to get all public repos from a user:

```bash
ghj fetch user <USER>> > pub-repos.json
```

Or with private repos and extra metadata:

```bash
ghj fetch user <USER> --auth-token <YOUR_TOKEN> --no-public --private --extra > priv-repos.json
```

### Step 2: Render JSON to Hugo Content

Once you have `pub-repos.json`, run the renderer:

```bash
ghj hugo pub-repos.json --images --output myhugosite/content/projects/
```

This will:

- Create `content/projects/<repo-name>/index.md` for each repo.
- Download either `featured.png` or the first image in the root of the repo as `static/images/<repo-name>/featured.png` if available.

### Integrating with Hugo

Run Hugo to build your site:

```bash
hugo server
```

Navigate to `http://localhost:1313/` to see your projects listed.

- The `listings.html` layout works with `_index.md` in `content/projects/`.
- Each project page uses `project.html` to display details. Feel free to customize these layouts as needed.

## Dashboard Usage

The dashboard is a web-based tool for querying and visualizing the repository data.

```bash
ghj dash
```

This is a streamlit app that runs in your browser. It includes:

- A dialog for selectting one or more JSON repo files to load.
- A search bar for querying the repositories.
- A Large Language Model (LLM) for asking questions about the repositories.
- A table view of the repositories with sorting and filtering options.
- Various visualizations like a scatter plot of stars vs. forks, a histogram of stars, etc.
