---
date: '2024-01-30T13:16:07Z'
description: video-playlist-manager
forks: 0
languages:
- Python
- Shell
- Dockerfile
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/video-playlist-manager
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: video-playlist-manager
---

video-playlist-manager

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: Python, Shell, Dockerfile

## Contributors
- queelius (5 commits)

## README
# Video Playlist Daemon

## Overview
Video Playlist Daemon is a tool designed to serve as a backend for managing video playlists. It is designed to be used as a standalone application or as a tool for lage language models (LLM). It is built using Python and FastAPI, and uses MongoDB as the database.

## Motivation and Use Cases
1. **Language Model Integration**: Facilitates the integration of YouTube playlist data into language models for enhanced content retrieval and processing.
2. **Playlist Management Outside YouTube**: Simplifies tracking and managing educational or curated content, useful for bloggers and educators.
3. **Educational Tool**: Showcases the application development process using conversational AI, potentially including a feature to view the development chat.

## Features
- Import playlists from YouTube channels or JSON files.
- Manage playlists: add, delete, and update content.
- Manage videos: add, delete, and update content.
- Search for videos. Since it is based on Elasticsearch, it supports full-text search and ranking. We document the expressive query language in this document as well.
- API endpoints to fetch playlist and video details.

## Requirements

- Docker
- Docker Compose

## Setup

1. Clone this repository.
2. Build and run the Docker containers: `docker-compose up --build`

The application will be available at `http://localhost:8000`.

## API Endpoints

We use the following endpoints to manage playlists, videos, and import data from external sources. It is a RESTful API that uses JSON for data exchange. It is based on FastAPI and so `/docs` and `/redoc` are available for interactive documentation.

### Search

#### GET /search 
Searches for videos based on query parameters.
- **Query Parameters**:
  - `query`: The search term(s) to look for in videos. If empty, a default set of videos is returned (e.g., top 10 by views).
  - `limit` (optional, default=10): Limits the number of returned results. Useful for implementing pagination or limiting result sets.
- **Notes**: The search functionality supports full-text search on video descriptions. It employs a ranking algorithm (like BM25) to order the results by relevance. If no query is provided, it returns a default set of videos, which can be sorted by popularity, recency, or other criteria.

### Managing Playlists

#### POST /playlist
Creates a new playlist.
- **Body Parameters**:
  - `playlist_name`: Name of the new playlist.
  - `description` (optional): A brief description of the playlist.
- **Notes**: This endpoint is used to create custom playlists within the application.

#### GET /playlist/{playlist_id}
Retrieves a specific playlist. If `playlist_id` is omitted, returns a list of all playlists.
- **Path Parameters**:
  - `playlist_id` (optional): The unique identifier of the playlist to retrieve.
- **Notes**: Fetches details of a single playlist. If no `playlist_id` is provided, the endpoint lists all playlists, which can be used for browsing or administrative purposes.

#### PUT /playlist/{playlist_id}
Updates a specific playlist.
- **Path Parameters**:
  - `playlist_id`: The unique identifier of the playlist to update.
- **Body Parameters**:
  - `playlist_name` (optional): New name for the playlist.
  - `description` (optional): Updated description.
  - `video_ids` (optional): List of video IDs to add to the playlist.
- **Notes**: Allows modifications to playlist details like name and description. Can also be used to add or remove videos from the playlist.

#### DELETE /playlist/{playlist_id}
Deletes a specific playlist.
- **Path Parameters**:
  - `playlist_id`: The unique identifier of the playlist to delete.
- **Notes**: Removes a playlist from the application. This action should be irreversible and may require additional confirmation in the UI.

### Managing Videos

#### POST /videos
Adds a new video.
- **Body Parameters**:
  - `video_url`: URL of the video.
  - `description` (optional): Description of the video.
- **Notes**: This endpoint allows users to add standalone videos or videos not imported from external sources.

#### GET /videos/{video_id}
Retrieves a specific video. If `video_id` is omitted, returns a list of all videos.
- **Path Parameters**:
  - `video_id` (optional): The unique identifier of the video to retrieve.
- **Notes**: Fetches details of a single video. Similar to playlists, omitting `video_id` lists all videos in the application.

#### PUT /videos/{video_id}
Updates a specific video.
- **Path Parameters**:
  - `video_id`: The unique identifier of the video to update.
- **Body Parameters**:
  - `video_url` (optional): New URL for the video.
  - `description` (optional): Updated description of the video.
- **Notes**: Enables updating

#### DELETE /videos/{video_id}
Delete a specific video.
- **Path Parameters**:
  - `video_id`: The unique identifier of the video to delete.
- **Notes**: Removes a video from the application. This action should be irreversible and may require additional confirmation in the UI. If the video is part of a playlist, it should be removed from the playlist as well.

### Importing Data

#### POST /import/youtube-playlist
Import a playlist from YouTube.
- **Body Parameters**:
  - `youtube_playlist_id`: ID of the YouTube playlist to import.
- **Notes**: This endpoint allows users to import playlists from YouTube. The system fetches playlist data, including all associated videos, and adds them to the application's database.

#### POST /import/youtube-channel
Import a channel from YouTube.
- **Body Parameters**:
  - `youtube_channel_id`: ID of the YouTube channel to import.
- **Notes**: Similar to playlist import, this endpoint enables importing all of the visible playlists on the YouTube channel. Metadata such as channel description, original source, and any associated playlists are stored.

##### Example
To import the playlists from my YouTube channel [queelius](https://www.youtube.com/channel/UCYNVzb35O7e2GBICAYfOXDg), which has a channel ID of `UC8butISFwT-Wl7EV0hUK0BQ`, we can use the following command:

```bash
curl -X POST "http://localhost:8000/import-youtube-channel/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"youtube_channel_id\":\"UC8butISFwT-Wl7EV0hUK0BQ\"}"
```

#### POST /import/youtube-video
Import a video from YouTube.
- **Body Parameters**:
  - `youtube_video_id`: ID of the YouTube video to import.
- **Notes**: Similar to playlist import, this endpoint enables importing individual videos. Metadata such as video description, original source, and any associated playlist information are stored.

#### POST /import/video-link
Import a video from a URL.
- **Body Parameters**:
  - `video_url`: URL of the video to import.
  - `description` (optional): Description of the video.
- **Notes**: This endpoint allows users to add standalone videos or videos not imported from external sources.

#### GET /export/data
Download all the data (playlists and videos) as a JSON file.
- **Notes**: This endpoint allows users to download all the data in the application as a JSON file. This can be used to backup the data or to import it into another application.

## Data Model

### Playlist Document

Represents a playlist in the application.

- **id** (string): Unique identifier for the playlist.
- **title** (string): Title of the playlist.
- **original_playlist_url** (string, optional): URL of the original playlist (e.g., YouTube playlist).
- **original_owner_url** (string, optional): URL of the original owner (e.g., YouTube channel).
- **description** (string, optional): Description of the playlist.
- **video_ids** (array of strings, optional): List of video IDs that are part of this playlist.
- **comments** (array of strings, optional): Comments added by users.
- **likes** (integer): Number of likes the playlist has received.
- **views** (integer): Number of views for the playlist.

To create the Elasticsearch mapping for the playlist index, use the following CURL command:
```bash
curl -X PUT "localhost:9200/playlist_index" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "title": { "type": "text" },
      "original_playlist_url": { "type": "text", "index": false },
      "original_owner_url": { "type": "text", "index": false },
      "description": { "type": "text" },
      "video_ids": { "type": "keyword" },  // Array of video IDs
      "comments": { "type": "text" },      // Array of comments
      "likes": { "type": "integer" },
      "views": { "type": "integer" }
    }
  }
}'
```

### Video Document

Represents a video, which can be standalone or part of playlists.

- **id** (string): Unique identifier for the video.
- **original_playlist_url** (string, optional): URL of the original playlist (e.g., YouTube playlist).
- **original_owner_url** (string, optional): Original owner URL (e.g., YouTube channel).
- **comments** (array of strings, optional): Comments added by users.
- **likes** (integer): Number of likes the video has received.
- **views** (integer): Number of views for the video.
- **url** (string): URL where the video can be accessed.
- **title** (string, optional): Title of the video.
- **description** (string, optional): Description of the video.

To create the Elasticsearch mapping for the video index, use the following CURL command:
```bash
curl -X PUT "localhost:9200/video_index" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "original_playlist_url": { "type": "text", "index": false },
      "original_owner_url": { "type": "text", "index": false },
      "comments": { "type": "text" },      // Array of comments
      "likes": { "type": "integer" },
      "views": { "type": "integer" },
      "url": { "type": "text", "index": false },
      "title": { "type": "text" },
      "description": { "type": "text" }
    }
  }
}'
```


## Query Language

The search functionality supports full-text search on fields, like video descriptions. It employs a ranking algorithm (like BM25) to order the results by relevance. If no query is provided, it returns a default set of videos, which can be sorted by popularity, recency, or other criteria.

We support arbitrary Elasticsearch queries, which can be used to implement more complex search functionality. By default, the `/search` endpoint matches on video descriptions and video titles (if available)
and uses BM25 to rank the results.

However, *any* field, say playlist description or title, may also be used, and it can be combined with other fields using boolean operators. See the Data Model section for a list of available fields and see
the documentation for the Elasticsearch query language for more information on how to construct queries.

## Google API Setup

For the application to import channel playlists from YouTube, you need to set up Google API credentials and authenticate the application (YouTube Data API v3). This section describes the process.


### Obtaining Google API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the YouTube Data API v3 for your project.
4. Create credentials for a desktop application. This will give you a client ID and client secret.
5. Download the credentials and save them in a file named `client_secrets.json` in the root directory of this project.

### Authenticating the Application

The first time you run the application, it will attempt to authenticate with Google's API using the credentials in the `client_secrets.json` file. You will be prompted to >

If the access token expires, the application will automatically use the refresh token to obtain a new one. If the `token.pickle` file is deleted, you will need to re-authe>

## Future Work

- **Vector Database Integration**: To assist with RAG (Retrieval-Augmented Generation), integrate a vector database.
- **Function Calling**: Implement standard interfaces for LMs (language models) to use this as a tool.

## Contribution
I am open to contributions and suggestions. Please open an issue or pull request if you have any ideas.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.