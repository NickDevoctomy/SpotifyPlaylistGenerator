"""
Main application UI for the Spotify Playlist Generator.
"""
from nicegui import ui

class AppUI:
    """Main UI class that handles the application interface."""
    
    def __init__(self):
        """Initialize the UI components."""
        self.setup_tabs()
    
    def setup_tabs(self):
        """Set up the main tabs interface."""
        with ui.tabs().classes('w-full') as tabs:
            ui.tab('My Playlists', icon='format_list_bulleted')
            ui.tab('Settings', icon='settings')
        
        with ui.tab_panels(tabs, value='My Playlists').classes('w-full'):
            with ui.tab_panel('My Playlists'):
                self._setup_playlists_tab()
            
            with ui.tab_panel('Settings'):
                self._setup_settings_tab()
    
    def _setup_playlists_tab(self):
        """Set up the content for the playlists tab."""
        with ui.card().classes('w-full'):
            ui.label('My Playlists Content').classes('text-h6')
            # Content for playlists will be added here
    
    def _setup_settings_tab(self):
        """Set up the content for the settings tab."""
        with ui.card().classes('w-full'):
            ui.label('Settings Content').classes('text-h6')
            # Content for settings will be added here 