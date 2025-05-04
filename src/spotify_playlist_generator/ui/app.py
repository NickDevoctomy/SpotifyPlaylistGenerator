"""
Main application UI for the Spotify Playlist Generator.
"""
from nicegui import ui, app
import asyncio
import webbrowser
import traceback
from fastapi.responses import HTMLResponse, PlainTextResponse
from src.spotify_playlist_generator.services.auth_service import SpotifyAuthService
from src.spotify_playlist_generator.services.spotify_service import SpotifyService
from src.spotify_playlist_generator.ui.template_loader import TemplateLoader
from src.spotify_playlist_generator.ui.ui_components import PlaylistComponents, CustomStyles

class AppUI:
    """Main UI class that handles the application interface."""
    
    def __init__(self):
        """Initialize the UI components."""
        self.auth_service = SpotifyAuthService()
        self.spotify_service = None
        self.is_authenticated = False
        self.user_info = None
        self.playlists = []
        self.current_view = "Tiled"  # Default view mode
        
        # Initialize template loader
        self.template_loader = TemplateLoader()
        
        # Set up the callback route for Spotify OAuth
        self._setup_callback_route()
        
        # Check if already authenticated
        if self.auth_service.check_token():
            self.is_authenticated = True
            self.user_info = self.auth_service.get_user_info()
            self.spotify_service = SpotifyService(self.auth_service.get_spotify_client())
        
        # Set up the main page
        self._setup_main_page()
    
    def _setup_main_page(self):
        """Set up the main application page."""
        @ui.page('/')
        def main_page():
            self.setup_header()
            self.setup_tabs()
    
    def _setup_callback_route(self):
        """Set up the callback route for Spotify OAuth."""
        @app.get('/callback')
        async def callback(code: str = ''):
            if code:
                # Process the authentication in a regular function
                try:
                    print("Callback received with code, attempting authentication...")
                    success = self.auth_service.authenticate(code)
                    
                    if success:
                        self.is_authenticated = True
                        self.user_info = self.auth_service.get_user_info()
                        # Initialize Spotify service with the authenticated client
                        self.spotify_service = SpotifyService(self.auth_service.get_spotify_client())
                        
                        # Load the success template
                        html_content = self.template_loader.load_template('auth_success.html')
                        return HTMLResponse(content=html_content)
                    else:
                        # Load the error template
                        error_html = self.template_loader.load_template('auth_error.html')
                        return HTMLResponse(content=error_html)
                except Exception as e:
                    print(f"Exception in callback handler: {str(e)}")
                    print(traceback.format_exc())
                    
                    # Return a plain text response for unexpected errors
                    return PlainTextResponse(
                        content=f"Unexpected error during authentication: {str(e)}\n\n"
                                f"Please restart the application and try again."
                    )
            else:
                # Load the no-code template
                no_code_html = self.template_loader.load_template('no_code.html')
                return HTMLResponse(content=no_code_html)
    
    def setup_header(self):
        """Set up the application header with login button."""
        with ui.header().classes('items-center'):
            ui.label('Spotify Playlist Generator').classes('text-h5 flex-grow')
            
            # Create login button
            self.login_button = ui.button('Login', icon='login').classes('bg-green-600 text-white')
            
            # Set the button action based on authentication status
            if self.is_authenticated:
                self.login_button.text = f"Logged in as {self.user_info.get('display_name', 'User')}"
                self.login_button.icon = 'person'
                self.login_button.on('click', self._handle_logout)
            else:
                self.login_button.on('click', self._handle_login)
    
    def _handle_login(self):
        """Handle login button click."""
        try:
            # Get the authorization URL
            auth_url = self.auth_service.get_auth_url()
            # Open the browser to the authorization URL
            webbrowser.open(auth_url)
            ui.notify('Opening Spotify login in your browser...', color='info')
        except Exception as e:
            ui.notify(f'Error starting authentication: {str(e)}', color='negative')
    
    def _handle_logout(self):
        """Handle logout button click."""
        self.auth_service.logout()
        self.is_authenticated = False
        self.user_info = None
        self.spotify_service = None
        self.playlists = []
        
        # Update the login button
        if hasattr(self, 'login_button'):
            self.login_button.text = 'Login'
            self.login_button.icon = 'login'
            self.login_button.on('click', self._handle_login)
        
        ui.notify('Successfully logged out', color='info')
        
        # Refresh the page to update UI
        ui.navigate.reload()
    
    def setup_tabs(self):
        """Set up the main tabs interface."""
        # Create tabs with left alignment
        with ui.tabs().classes('w-full items-start') as tabs:
            # Apply custom styling for left alignment
            CustomStyles.add_left_aligned_tabs_style()
            ui.tab('My Playlists', icon='format_list_bulleted')
            ui.tab('Settings', icon='settings')
        
        with ui.tab_panels(tabs, value='My Playlists').classes('w-full'):
            with ui.tab_panel('My Playlists'):
                self._setup_playlists_tab()
            
            with ui.tab_panel('Settings'):
                self._setup_settings_tab()
    
    def _fetch_playlists(self):
        """Fetch user's playlists from Spotify."""
        if not self.is_authenticated or not self.spotify_service:
            return
        
        ui.notify('Fetching your playlists...', color='info')
        
        # Clear existing playlists
        self.playlists = []
        
        # Get playlists from Spotify
        self.playlists = self.spotify_service.get_user_playlists()
        
        # Update UI
        if hasattr(self, 'playlist_container'):
            self.playlist_container.clear()
            self._render_playlists()
            
        # Show success message
        if self.playlists:
            ui.notify(f'Found {len(self.playlists)} playlists', color='positive')
        else:
            ui.notify('No playlists found', color='warning')
    
    def _render_playlists(self):
        """Render the playlists in the UI based on current view."""
        if not hasattr(self, 'playlist_container'):
            return
            
        with self.playlist_container:
            if not self.playlists:
                ui.label('No playlists found').classes('text-subtitle1')
                return
            
            # Render based on selected view
            if self.current_view == "Tiled":
                self._render_tiled_view()
            else:  # List view
                self._render_list_view()
    
    def _render_tiled_view(self):
        """Render playlists in a grid tile layout."""
        with ui.grid(columns=3).classes('w-full gap-4'):
            for playlist in self.playlists:
                PlaylistComponents.render_playlist_card(playlist)
    
    def _render_list_view(self):
        """Render playlists in a list layout."""
        for playlist in self.playlists:
            PlaylistComponents.render_playlist_list_item(playlist)
    
    def _change_view(self, view):
        """Change the playlist view mode and refresh the display."""
        self.current_view = view
        if hasattr(self, 'playlist_container'):
            self.playlist_container.clear()
            self._render_playlists()
    
    def _setup_playlists_tab(self):
        """Set up the content for the playlists tab."""
        with ui.card().classes('w-full'):
            ui.label('My Playlists').classes('text-h6')
            
            # Show a message if user is not authenticated
            if not self.is_authenticated:
                ui.label('Please log in to view your playlists').classes('text-subtitle1')
                ui.button('Login', icon='login').classes('bg-green-600 text-white').on('click', self._handle_login)
            else:
                # Top row with controls
                with ui.row().classes('w-full justify-end items-center mb-4'):
                    with ui.row().classes('items-center'):
                        # View switcher
                        ui.label('View:').classes('mr-2')
                        view_select = ui.select(
                            ['Tiled', 'List'], 
                            value=self.current_view,
                            on_change=lambda e: self._change_view(e.value)
                        ).classes('min-w-[100px]')
                        
                        # Refresh button
                        ui.button('Refresh', icon='refresh').classes('ml-4').on('click', self._fetch_playlists)
                
                # Create container for playlists
                self.playlist_container = ui.element('div').classes('w-full mt-4')
                
                # Initial load of playlists
                self._fetch_playlists()
    
    def _setup_settings_tab(self):
        """Set up the content for the settings tab."""
        with ui.card().classes('w-full'):
            ui.label('Settings Content').classes('text-h6')
            
            # Display environment variables status
            ui.label('Spotify API Configuration').classes('text-subtitle1 mt-4')
            with ui.row():
                ui.label('Client ID:').classes('text-bold')
                ui.label('✓ Configured' if self.auth_service.client_id else '✗ Not configured').classes(
                    'text-green-600' if self.auth_service.client_id else 'text-red-600')
            
            with ui.row():
                ui.label('Client Secret:').classes('text-bold')
                ui.label('✓ Configured' if self.auth_service.client_secret else '✗ Not configured').classes(
                    'text-green-600' if self.auth_service.client_secret else 'text-red-600')
            
            with ui.row():
                ui.label('Redirect URI:').classes('text-bold')
                ui.label(self.auth_service.redirect_uri or 'Not configured').classes(
                    'text-green-600' if self.auth_service.redirect_uri else 'text-red-600') 