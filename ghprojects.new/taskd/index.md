---
date: '2024-01-27T16:35:06Z'
description: '`taskd`: Task Daemon for Decentralized Task Execution for Long-Running
  Tasks'
forks: 0
languages:
- Python
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/taskd
- name: GitHub Pages
  url: https://queelius.github.io/taskd/
open_issues: 0
stars: 1
tags:
- GitHub
- project
title: taskd
---

`taskd`: Task Daemon for Decentralized Task Execution for Long-Running Tasks

**Stars**: 1 | **Forks**: 0 | **Open Issues**: 0

**Languages**: Python

## Contributors
- queelius (5 commits)

## README
# `taskd`: Task Daemon for Decentralized Task Execution for Long-Running Tasks

The project `taskd` is a web service for script execution environment with workspace management. It allows you to create a workspace, upload a script, execute the script, and delete the workspace.

## Workflow

1. Create a workspace
2. Upload a script
3. Execute a script
4. Delete a workspace

## Getting Started

To get the server up and running, follow these steps:

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Install and run `redis-server`:
    - On Linux, you can install Redis using `apt-get install redis-server` and run it using `sudo systemctl start redis-server`
3. Install and run `rq worker`:
    - On Linux, you can install RQ using `pip install rq` and run it using `rq worker`
4. Run `rq-dashboard`:
    - On Linux, you can install RQ Dashboard using `pip install rq-dashboard` and run it using `rq-dashboard`
5. Run `uvicorn main:app --reload`:
    - On Linux, you can install Uvicorn using `pip install uvicorn` and run it using `uvicorn main:app --reload`
6. Open `http://localhost:8000/docs` for the docs

## API Endpoints

The application provides several API endpoints for managing workspaces and executing scripts. These are defined in [`routes.py`](routes.py).

## Script Execution

Scripts are executed in their respective workspaces. The output of the script execution is logged to a file in the workspace. This is handled by the `execute_script` function in [`utils.py`](utils.py).

## Documentation

For more detailed information about the application and its usage, refer to the [docs](docs/index.md).