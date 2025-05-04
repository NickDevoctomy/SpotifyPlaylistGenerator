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
│       │   ├── templates/  # HTML templates
│       │   └── app.py      # Main UI application
│       ├── services/       # Service layer for API interactions
│       └── models/         # Data models
```

## Technology Stack
- Python 3.11
- NiceGUI - UI framework
- Spotipy - Spotify API client

## Guidelines for Future LLM Usage

This section provides guidance for LLMs (Large Language Models) when working with this codebase.

### SOLID Principles Enforcement

When modifying or extending this codebase, enforce the following SOLID principles:

1. **Single Responsibility Principle (SRP)**
   - Each class should have only one reason to change
   - Keep UI components separate from business logic
   - Example: The `PlaylistComponents` class handles rendering, while `AppUI` orchestrates application flow

2. **Open/Closed Principle (OCP)**
   - Software entities should be open for extension but closed for modification
   - Add new functionality by creating new classes rather than modifying existing ones
   - Example: To add a new playlist view type, extend the rendering system without changing core classes

3. **Liskov Substitution Principle (LSP)**
   - Subtypes must be substitutable for their base types
   - Ensure any class that inherits from another can be used in the same way

4. **Interface Segregation Principle (ISP)**
   - Clients should not be forced to depend on interfaces they do not use
   - Create specific, focused interfaces rather than general-purpose ones

5. **Dependency Inversion Principle (DIP)**
   - High-level modules should not depend on low-level modules; both should depend on abstractions
   - Example: `AppUI` depends on abstract interfaces (template loader, auth service) rather than concrete implementations

### Code Maintenance Guidelines

When working with this codebase:

1. **HTML Content**
   - Never embed HTML directly in Python code
   - Always place HTML in template files in the `templates/` directory
   - Use the `TemplateLoader` class to load HTML templates

2. **UI Components**
   - Place UI rendering logic in the `ui_components.py` file
   - Create static methods for reusable UI elements
   - Keep styling separate from structure

3. **Directory Structure**
   - Maintain the existing directory structure
   - Place new templates in the `templates/` directory
   - Create new modules for new functionality domains

4. **Authentication Logic**
   - Keep authentication logic in the `auth_service.py` file
   - Ensure OAuth flow is maintained when modifying authentication

5. **Style Consistency**
   - Follow the existing code style (docstrings, method naming)
   - Use type hints for function parameters and return values
   - Document complex logic with clear comments

### Adding New Features

When adding new features:

1. Identify which layer the feature belongs to (UI, service, model)
2. Create appropriate classes following SOLID principles
3. Update existing orchestration classes to use the new components
4. Add appropriate documentation
5. Update this README if the feature changes the project structure

By following these guidelines, you'll help maintain a clean, modular, and extensible codebase.
