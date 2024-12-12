# `gh_repo_filter`: Filter GitHub Repositories with JMESPath

## Motivation

`gh_repo_filter` is a command-line tool designed to filter GitHub repository JSON data using [JMESPath](https://jmespath.org/) queries. It allows you to efficiently search and extract repositories that meet specific criteria without the need to write additional code. This tool is especially helpful when working with large datasets fetched from GitHub's API.

By leveraging JMESPath, you can perform complex filtering operations directly from the command line, making data analysis and processing more streamlined.

## Installation

Ensure you have Python 3 installed. You can install `gh_repo_filter` via PyPI:

```bash
pip install gh_repo_filter
```

This will install the `gh_repo_filter` command-line tool accessible from your terminal.

## Usage

```bash
gh_repo_filter [input_file] <query> [-o output_file]
```

- input_file: (Optional) Path to the input JSON file. Use `-` or omit to read from stdin.
- `<query>`: JMESPath query string to filter the data.
- `-o output_file`: (Optional) Write output to a file. Defaults to stdout if not provided.

### Reading from stdin and stdout

The tool supports reading input from stdin and writing output to stdout, enabling easy integration with other command-line tools via pipelines.

## Examples

### Example 1: Filter repositories by language

Filter repositories where the primary language is Python.

```bash
gh_repo_filter repos.json "language == 'Python'" > python_repos.json
```

Using stdin:

```bash
cat repos.json | gh_repo_filter 'language == "Python"' > python_repos.json
```

### Example 2: Filter repositories with more than 50 stars

```bash
gh_repo_filter repos.json 'stargazers_count > `50`' > popular_repos.json
```

### Example 3: Filter repositories updated after a specific date

```bash
gh_repo_filter repos.json 'updated_at > "2023-01-01T00:00:00Z"'
```

### Example 4: Filter repositories where the name contains "tool"

```bash
gh_repo_filter repos.json "contains(name, 'tool')"
```

### Example 5: Filter repositories that are not forks

```bash
gh_repo_filter repos.json 'fork == `false`'
```

### Example 6: Combine multiple filters

Filter repositories that are in Python and have more than 50 stars.

```bash
gh_repo_filter repos.json 'language == "Python" && stargazers_count > `50`'
```

Equivalently, we could have piped the output of the first filter to the second filter:

```bash
gh_repo_filter repos.json 'language == "Python"' | gh_repo_filter 'stargazers_count > `50`'
```

### Example 7: Filter repositories with a specific topic

Assuming your repository data includes a `topics` list, filter repositories that contain the topic "data-science".

```bash
gh_repo_filter repos.json "contains(topics, 'data-science')"
```

### Example 8: Using stdin and stdout in a pipeline

Fetch repositories from the GitHub API and filter them on the fly.

```bash
curl 'https://api.github.com/users/username/repos' | gh_repo_filter - "language == 'JavaScript'" > js_repos.json
```

### Example 9: More complex queries

Filter repositories where the language is either Python or JavaScript and have more than 100 stars.

```bash
gh_repo_filter repos.json '(language == "Python" || language == "JavaScript") && stargazers_count > `100`'
```

## Notes

- The input JSON data should be an array of repository objects, as returned by GitHub API endpoints like `/users/{username}/repos`. We
provide a custom tools like `gh_repo_user` to fetch repository data from GitHub API endpoints, augmented with additional metadata.
- **Numeric literals**: Enclose numeric values in backticks (e.g., `50`) when used in comparisons.
- **String literals**: Enclose strings in quotes (e.g., `'Python'` or `"Python"`. Use single quotes to avoid needing to escape backticks.
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

## Additional Resources

- **JMESPath Tutorial**: [https://jmespath.org/tutorial.html](https://jmespath.org/tutorial.html)  
  Learn how to craft complex queries to manipulate and extract JSON data.
- [`gh_repo_json`](./GH_REPO_JSON.md): Information on the structure of the JSON repository data fetched by tools like `gh_repo_user` or just using the GitHub endpoints directly.
  