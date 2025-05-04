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
        self.playlist_tabs = None
        self.playlist_tab_panels = None
        self.selected_playlist = None
        self.created_tabs = set()  # Track which tabs have been created
        self.playlist_tracks_cache = {}  # Cache tracks for each playlist
        
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
                PlaylistComponents.render_playlist_card(playlist, on_click=self._open_playlist_detail)
    
    def _render_list_view(self):
        """Render playlists in a list layout."""
        for playlist in self.playlists:
            PlaylistComponents.render_playlist_list_item(playlist, on_click=self._open_playlist_detail)
    
    def _open_playlist_detail(self, playlist):
        """Open the playlist detail view in a new tab."""
        self.selected_playlist = playlist
        
        # Switch to the playlist detail tab
        self._create_playlist_detail_tab(playlist)
        self.playlist_tabs.value = f"playlist-{playlist['id']}"
    
    def _create_playlist_detail_tab(self, playlist):
        """Create a new tab for the playlist detail view if it doesn't exist."""
        tab_id = f"playlist-{playlist['id']}"
        
        # Check if the tab already exists using our tracking set
        if tab_id not in self.created_tabs:
            with self.playlist_tabs:
                ui.tab(tab_id)
                self.created_tabs.add(tab_id)  # Track that we've created this tab
            
            # First load the tracks in the background
            playlist_id = playlist['id']
            print(f"[DEBUG APP] Auto-loading tracks for playlist: {playlist['name']} (ID: {playlist_id})")
            
            # Check if we already have cached tracks for this playlist
            if playlist_id in self.playlist_tracks_cache:
                tracks = self.playlist_tracks_cache[playlist_id]
                print(f"[DEBUG APP] Using {len(tracks)} cached tracks")
            else:
                # Load tracks from Spotify API if available
                tracks = []
                if self.is_authenticated and self.spotify_service:
                    try:
                        # Get total number of tracks to load all of them
                        total_tracks = playlist.get('tracks', {}).get('total', 0)
                        print(f"[DEBUG APP] Playlist has {total_tracks} tracks total")
                        
                        # Load all tracks with proper handling of pagination
                        all_tracks = []
                        offset = 0
                        limit = 100  # API limit per request
                        
                        while offset < total_tracks:
                            print(f"[DEBUG APP] Loading tracks batch: offset={offset}, limit={limit}")
                            batch = self.spotify_service.get_playlist_tracks(playlist_id, limit=limit, offset=offset)
                            if not batch:
                                print(f"[DEBUG APP] No tracks returned for offset {offset}, stopping pagination")
                                break
                                
                            print(f"[DEBUG APP] Got {len(batch)} tracks in this batch")
                            all_tracks.extend(batch)
                            offset += limit
                            
                            # Safety check - stop if we've loaded all tracks or API returned fewer than requested
                            if len(batch) < limit:
                                break
                        
                        tracks = all_tracks
                        print(f"[DEBUG APP] Total tracks loaded: {len(tracks)}")
                        
                        # Cache tracks for future use
                        if tracks:
                            self.playlist_tracks_cache[playlist_id] = tracks
                    except Exception as e:
                        print(f"[DEBUG APP] Error auto-loading tracks: {str(e)}")
                        # Fall back to test tracks if API fails
                        tracks = self._get_test_tracks()
                        print(f"[DEBUG APP] Using {len(tracks)} test tracks as fallback")
                else:
                    # Use test tracks if not authenticated
                    tracks = self._get_test_tracks()
                    print(f"[DEBUG APP] Using {len(tracks)} test tracks (not authenticated)")
            
            # Now render the playlist detail with the tracks
            with self.playlist_tab_panels:
                with ui.tab_panel(tab_id):
                    print(f"[DEBUG APP] Rendering playlist detail with {len(tracks)} tracks")
                    PlaylistComponents.render_playlist_detail(
                        playlist, 
                        tracks=tracks,  # Pass the tracks directly
                        on_back=self._back_to_playlists
                    )
        else:
            # Tab already exists, just update it if needed
            print(f"[DEBUG APP] Tab for playlist {playlist['name']} already exists")
    
    def _back_to_playlists(self):
        """Go back to the playlists list view."""
        # Switch to the main tab
        self.playlist_tabs.value = "playlists-main"
        
        # Clear the selected playlist
        self.selected_playlist = None
    
    def _change_view(self, view):
        """Change the playlist view mode and refresh the display."""
        self.current_view = view
        if hasattr(self, 'playlist_container'):
            self.playlist_container.clear()
            self._render_playlists()
    
    def _setup_playlists_tab(self):
        """Set up the content for the playlists tab."""
        with ui.card().classes('w-full'):
            # Create hidden tabs for playlists
            with ui.tabs().classes('w-full hidden-tabs') as self.playlist_tabs:
                # Apply custom styling to hide tabs
                CustomStyles.add_hidden_tabs_style()
                ui.tab('playlists-main')
                # Add initial tab to our set of created tabs
                self.created_tabs.add('playlists-main')
            
            # Create tab panels for playlists
            with ui.tab_panels(self.playlist_tabs, value='playlists-main').classes('w-full') as self.playlist_tab_panels:
                with ui.tab_panel('playlists-main'):
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
    
    def _load_playlist_tracks(self, playlist_id):
        """Load tracks for a playlist and update the UI."""
        if not self.is_authenticated or not self.spotify_service:
            ui.notify('Please log in to view tracks', color='warning')
            return
        
        ui.notify('Loading tracks...', color='info')
        print(f"[DEBUG APP] Loading tracks for playlist ID: {playlist_id}")
        print(f"[DEBUG APP] Authentication status: {self.is_authenticated}")
        print(f"[DEBUG APP] Spotify service initialized: {self.spotify_service is not None}")
        
        # Check if we already have cached tracks for this playlist
        if playlist_id in self.playlist_tracks_cache:
            print(f"[DEBUG APP] Using cached tracks for playlist {playlist_id}")
            tracks = self.playlist_tracks_cache[playlist_id]
            print(f"[DEBUG APP] Found {len(tracks)} cached tracks")
        else:
            try:
                # Get tracks from Spotify API
                print(f"[DEBUG APP] Calling spotify_service.get_playlist_tracks({playlist_id})")
                tracks = self.spotify_service.get_playlist_tracks(playlist_id)
                print(f"[DEBUG APP] Retrieved {len(tracks)} tracks from Spotify API")
                
                # Cache the tracks for future use
                if tracks:
                    self.playlist_tracks_cache[playlist_id] = tracks
                    print(f"[DEBUG APP] Cached {len(tracks)} tracks for playlist {playlist_id}")
                else:
                    print("[DEBUG APP] No tracks returned from API, trying fallback")
                    # Create test tracks as fallback for debugging
                    tracks = self._get_test_tracks()
                    print(f"[DEBUG APP] Created {len(tracks)} test tracks as fallback")
                
                # Dump full raw data of the first few tracks for debugging
                if tracks:
                    print("[DEBUG APP] ======= RAW TRACK DATA SAMPLE ========")
                    import json
                    for i, track in enumerate(tracks[:2]):  # Show first 2 tracks
                        try:
                            print(f"[DEBUG APP] Track {i+1} raw data:")
                            print(json.dumps(track, indent=2))
                        except Exception as json_error:
                            print(f"[DEBUG APP] Error serializing track to JSON: {str(json_error)}")
                            print(f"[DEBUG APP] Track {i+1} type: {type(track)}")
                            print(f"[DEBUG APP] Track {i+1} keys: {track.keys() if hasattr(track, 'keys') else 'No keys method'}")
                    print("[DEBUG APP] ======= END RAW TRACK DATA ========")
                
            except Exception as e:
                ui.notify(f'Error loading tracks: {str(e)}', color='negative')
                print(f"[DEBUG APP] Error loading tracks: {str(e)}")
                import traceback
                print(f"[DEBUG APP] Error traceback: {traceback.format_exc()}")
                
                # Create test tracks as fallback for debugging
                tracks = self._get_test_tracks()
                print(f"[DEBUG APP] Created {len(tracks)} test tracks as fallback after error")
        
        # Find the tab panel to update
        tab_id = f"playlist-{playlist_id}"
        found_panel = False
        print(f"[DEBUG APP] Looking for tab panel with ID: {tab_id}")
        print(f"[DEBUG APP] Available tab panels: {[child.value if hasattr(child, 'value') else 'No value attr' for child in self.playlist_tab_panels.children]}")
        
        for child in self.playlist_tab_panels.children:
            if hasattr(child, 'value') and child.value == tab_id:
                found_panel = True
                print(f"[DEBUG APP] Found panel with ID: {tab_id}")
                # Clear the tab panel and redraw with tracks
                child.clear()
                with child:
                    # Get the playlist data from our list
                    playlist = next((p for p in self.playlists if p['id'] == playlist_id), None)
                    if playlist:
                        print(f"[DEBUG APP] Found playlist in cache, rendering with {len(tracks)} tracks")
                        print(f"[DEBUG APP] Calling PlaylistComponents.render_playlist_detail")
                        PlaylistComponents.render_playlist_detail(
                            playlist,
                            tracks=tracks,
                            on_back=self._back_to_playlists
                        )
                    else:
                        print(f"[DEBUG APP] Could not find playlist with ID {playlist_id} in the loaded playlists")
                        print(f"[DEBUG APP] Available playlist IDs: {[p.get('id') for p in self.playlists]}")
        
        if not found_panel:
            print(f"[DEBUG APP] Could not find tab panel with ID {tab_id}")
        
        # Show success message
        if tracks:
            ui.notify(f'Loaded {len(tracks)} tracks', color='positive')
        else:
            ui.notify('No tracks found in this playlist', color='warning')
    
    def _get_test_tracks(self):
        """Create test track data for debugging purposes."""
        print("[DEBUG APP] Creating test tracks for debugging")
        
        # Simple test tracks with minimal required fields
        test_tracks = [
            {
                "track": {
                    "id": "test1",
                    "name": "Test Track 1",
                    "uri": "spotify:track:test1",
                    "artists": [{"name": "Test Artist 1"}],
                    "album": {
                        "name": "Test Album 1",
                        "images": [{"url": "https://via.placeholder.com/300"}]
                    },
                    "external_urls": {"spotify": "https://open.spotify.com/track/test1"}
                }
            },
            {
                "track": {
                    "id": "test2",
                    "name": "Test Track 2",
                    "uri": "spotify:track:test2",
                    "artists": [{"name": "Test Artist 2"}],
                    "album": {
                        "name": "Test Album 2",
                        "images": [{"url": "https://via.placeholder.com/300"}]
                    },
                    "external_urls": {"spotify": "https://open.spotify.com/track/test2"}
                }
            },
            {
                "track": {
                    "id": "test3",
                    "name": "Test Track 3",
                    "uri": "spotify:track:test3",
                    "artists": [{"name": "Test Artist 3"}],
                    "album": {
                        "name": "Test Album 3",
                        "images": [{"url": "https://via.placeholder.com/300"}]
                    },
                    "external_urls": {"spotify": "https://open.spotify.com/track/test3"}
                }
            }
        ]
        
        return test_tracks 