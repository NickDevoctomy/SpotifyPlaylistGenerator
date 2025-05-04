# SpotifyPlaylistGenerator
A vibe-coded proof-of-concept tool for using AI to generate Spotify playlists.

## Project Overview
A NiceGUI-based Python application that allows users to manage their Spotify playlists.

## Features
- View your Spotify playlists
- Settings for application configuration
- Spotify OAuth authentication

## Setup and Installation

### Prerequisites
- Python 3.11
- Miniconda or Anaconda
- Spotify Developer Account

### Spotify API Setup
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Create a new application
3. Set the Redirect URI to `http://127.0.0.1:8080/callback`
4. Create a `.env` file in the project root with the following variables:
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8080/callback
```

### Installation Steps

1. Clone this repository
2. Create the conda environment:
```bash
conda create -n spotify-playlist-generator python=3.11
```
3. Activate the environment:
```bash
conda activate spotify-playlist-generator
```
4. Install required packages:
```bash
pip install -r requirements.txt
```
5. Run the application:
```bash
python app.py
```

## Project Structure
```
├── app.py                  # Main entry point
├── requirements.txt        # Python package requirements
├── src/                    # Source code
│   └── spotify_playlist_generator/ 
│       ├── ui/             # UI components
│       ├── services/       # Service layer for API interactions
│       └── models/         # Data models
```

## Technology Stack
- Python 3.11
- NiceGUI - UI framework
- Spotipy - Spotify API client
