"""
Main entry point for the Spotify Playlist Generator application.
"""
from nicegui import ui
from src.spotify_playlist_generator.ui.app import AppUI


def main():
    """Main entry point for the application."""
    # Initialize the UI
    app_ui = AppUI()
    
    # Start the NiceGUI application
    ui.run(title="Spotify Playlist Generator", port=8080, reload=False)


if __name__ in {"__main__", "__mp_main__"}:
    main() 