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
import os

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
        self.selected_track = None
        self.created_tabs = set()  # Track which tabs have been created
        self.playlist_tracks_cache = {}  # Cache tracks for each playlist
        self.initial_load_complete = False  # Flag to track if initial load has happened
        
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
            print("[DEBUG APP] Not authenticated or no spotify service, cannot fetch playlists")
            return
        
        print("[DEBUG APP] Fetching playlists from Spotify...")
        ui.notify('Fetching your playlists...', color='info')
        
        # Clear existing playlists
        self.playlists = []
        
        try:
            # Get playlists from Spotify
            self.playlists = self.spotify_service.get_user_playlists()
            print(f"[DEBUG APP] Retrieved {len(self.playlists)} playlists from Spotify")
            
            # Update UI
            if hasattr(self, 'playlist_container'):
                print("[DEBUG APP] Clearing and updating playlist container")
                self.playlist_container.clear()
                self._render_playlists()
            else:
                print("[DEBUG APP] No playlist container found to update")
                
            # Show success message
            if self.playlists:
                ui.notify(f'Found {len(self.playlists)} playlists', color='positive')
            else:
                ui.notify('No playlists found', color='warning')
                
        except Exception as e:
            print(f"[DEBUG APP] Error fetching playlists: {str(e)}")
            ui.notify(f'Error fetching playlists: {str(e)}', color='negative')
            import traceback
            print(f"[DEBUG APP] Error traceback: {traceback.format_exc()}")
    
    def _render_playlists(self):
        """Render the playlists in the UI based on current view."""
        if not hasattr(self, 'playlist_container'):
            print("[DEBUG APP] No playlist container exists to render playlists")
            return
            
        print(f"[DEBUG APP] Rendering {len(self.playlists)} playlists in {self.current_view} view")
        with self.playlist_container:
            if not self.playlists:
                print("[DEBUG APP] No playlists to render, showing empty message")
                ui.label('No playlists found').classes('text-subtitle1')
                return
            
            # Render based on selected view
            if self.current_view == "Tiled":
                print("[DEBUG APP] Rendering tiled view")
                self._render_tiled_view()
            else:  # List view
                print("[DEBUG APP] Rendering list view")
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
                        # Simply log the error and return empty tracks
                        tracks = []
                        print(f"[DEBUG APP] Using empty track list due to error")
                else:
                    # Not authenticated, empty tracks
                    tracks = []
                    print(f"[DEBUG APP] Using empty track list (not authenticated)")
            
            # Now render the playlist detail with the tracks
            with self.playlist_tab_panels:
                with ui.tab_panel(tab_id):
                    print(f"[DEBUG APP] Rendering playlist detail with {len(tracks)} tracks")
                    PlaylistComponents.render_playlist_detail(
                        playlist, 
                        tracks=tracks,  # Pass the tracks directly
                        on_back=self._back_to_playlists,
                        on_track_click=self._open_track_detail
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
                        
                        # Initial load of playlists - ensure we load playlists if authenticated
                        if self.is_authenticated:
                            if not self.playlists or not self.initial_load_complete:
                                print("[DEBUG APP] Scheduling initial playlist fetch...")
                                # Use a short timer to ensure UI is fully initialized
                                ui.timer(0.2, lambda: self._fetch_playlists(), once=True)
                                self.initial_load_complete = True
                            else:
                                # If we already have playlists, just render them
                                print(f"[DEBUG APP] Using {len(self.playlists)} existing playlists")
                                self._render_playlists()
    
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
                    
            # Last.fm API Configuration
            ui.label('Last.fm API Configuration').classes('text-subtitle1 mt-4')
            with ui.row():
                ui.label('API Key:').classes('text-bold')
                lastfm_api_key = os.environ.get("LASTFM_API_KEY")
                ui.label('✓ Configured' if lastfm_api_key else '✗ Not configured').classes(
                    'text-green-600' if lastfm_api_key else 'text-red-600')
            
            with ui.row():
                ui.label('Shared Secret:').classes('text-bold')
                lastfm_shared_secret = os.environ.get("LASTFM_SHARED_SECRET")
                ui.label('✓ Configured' if lastfm_shared_secret else '✗ Not configured').classes(
                    'text-green-600' if lastfm_shared_secret else 'text-red-600')
            
            # Test LastFM API button
            with ui.row().classes('mt-4'):
                ui.button('Test Last.fm API', icon='api').classes('bg-blue-500 text-white').on('click', self._test_lastfm_api)
    
    def _test_lastfm_api(self):
        """Test the Last.fm API connection."""
        try:
            # Import LastFMService here to avoid circular imports
            from src.spotify_playlist_generator.services.lastfm_service import LastFMService
            
            # Show loading notification
            ui.notify('Testing Last.fm API connection...', color='info')
            
            # Initialize and test the LastFM service
            lastfm_service = LastFMService()
            result = lastfm_service.test_connection()
            
            # Log full result for debugging
            print(f"[DEBUG APP] LastFM test result: {result}")
            
            if result['success']:
                # Show success and the similar artists in a dialog
                ui.notify(result['message'], color='positive')
                
                # Create a dialog to show the similar artists
                with ui.dialog() as dialog, ui.card().classes('p-6 max-w-3xl'):
                    ui.label('Last.fm API Test Results').classes('text-h6 mb-4')
                    ui.label(result['message']).classes('text-body1 mb-4')
                    
                    # Display the similar artists
                    if result.get('data') and isinstance(result['data'], list) and len(result['data']) > 0:
                        ui.label('Similar Artists:').classes('text-subtitle1 mt-2 mb-3')
                        with ui.grid(columns=3).classes('w-full gap-4'):
                            for artist in result['data']:
                                with ui.card().classes('p-3 hover:bg-gray-50'):
                                    artist_name = artist.get('name', 'Unknown Artist')
                                    artist_url = artist.get('url')
                                    
                                    # Layout structure for consistent appearance
                                    with ui.column().classes('w-full items-center gap-2'):
                                        # Artist image placeholder (Last.fm doesn't provide images)
                                        with ui.element('div').classes('w-full aspect-square bg-gray-200 flex items-center justify-center rounded-full'):
                                            ui.icon('person').classes('text-gray-400')
                                        
                                        # Artist name 
                                        if artist_url:
                                            with ui.link(target=artist_url, new_tab=True).classes('no-underline'):
                                                ui.label(artist_name).classes('text-center text-sm font-bold text-blue-600 hover:underline mt-1')
                                        else:
                                            ui.label(artist_name).classes('text-center text-sm font-bold mt-1')
                                        
                                        # Match score with visual indicator
                                        if 'match' in artist:
                                            try:
                                                match_value = float(artist.get('match', 0))
                                                if match_value > 0:
                                                    # Show as percentage with progress bar
                                                    match_percent = int(match_value * 100)
                                                    ui.label(f"Match: {match_percent}%").classes('text-xs text-center w-full')
                                                    with ui.linear_progress(value=match_value).classes('w-full'):
                                                        pass
                                            except (ValueError, TypeError):
                                                # Skip match display if value is invalid
                                                pass
                                        
                                        # Note about Last.fm data
                                        ui.label("(Last.fm data)").classes('text-xs text-gray-500 mt-1')
                    else:
                        ui.label('No similar artists data returned').classes('text-body1 text-orange-500')
                    
                    # Close button
                    ui.button('Close', icon='close').on('click', dialog.close).classes('mt-4')
                    
                # Open the dialog
                dialog.open()
            else:
                # Show error
                error_msg = result.get('message', 'Unknown error')
                ui.notify(f"Last.fm API test failed: {error_msg}", color='negative')
                
                # Show error details in a dialog for better visibility
                with ui.dialog() as error_dialog, ui.card().classes('p-6'):
                    ui.label('Last.fm API Test Failed').classes('text-h6 text-red-500 mb-4')
                    ui.label(error_msg).classes('text-body1 mb-4')
                    
                    # Environment check
                    api_key = os.environ.get("LASTFM_API_KEY")
                    secret = os.environ.get("LASTFM_SHARED_SECRET")
                    
                    ui.label('Environment Check:').classes('text-subtitle1 mt-2')
                    ui.label(f"API Key: {'Configured' if api_key else 'Not configured'}").classes(
                        'text-body2 text-green-600' if api_key else 'text-body2 text-red-600')
                    ui.label(f"Shared Secret: {'Configured' if secret else 'Not configured'}").classes(
                        'text-body2 text-green-600' if secret else 'text-body2 text-red-600')
                    
                    ui.button('Close', icon='close').on('click', error_dialog.close).classes('mt-4')
                    
                error_dialog.open()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[DEBUG APP] Error testing Last.fm API: {error_details}")
            ui.notify(f'Error testing Last.fm API: {str(e)}', color='negative')
            
            # Show detailed error in dialog
            with ui.dialog() as exception_dialog, ui.card().classes('p-6'):
                ui.label('Last.fm API Test Error').classes('text-h6 text-red-500 mb-4')
                ui.label(f"Error: {str(e)}").classes('text-body1 mb-4')
                
                # Show traceback in a pre-formatted block with scrolling
                with ui.element('pre').classes('bg-gray-100 p-4 rounded max-h-64 overflow-y-auto text-xs'):
                    ui.label(error_details)
                
                ui.button('Close', icon='close').on('click', exception_dialog.close).classes('mt-4')
                
            exception_dialog.open()
    
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
                    print("[DEBUG APP] No tracks returned from API")
                    tracks = []
                
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
                tracks = []
        
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
                            on_back=self._back_to_playlists,
                            on_track_click=self._open_track_detail
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
    
    def _open_track_detail(self, track_data):
        """Open the track detail view in a new tab."""
        if not track_data:
            ui.notify('Unable to open track: No track data provided', color='negative')
            return
            
        print(f"[DEBUG APP] Opening track detail: {type(track_data)}")
        
        # Dump track data for debugging
        import json
        print("\n[DEBUG APP] ======= TRACK DATA DUMP ========")
        try:
            print(json.dumps(track_data, indent=2))
        except:
            print(f"[DEBUG APP] Unable to JSON serialize track_data")
        print("[DEBUG APP] ======= END TRACK DATA DUMP ========\n")
        
        # Extract track data
        track = track_data.get('track', {}) if 'track' in track_data else track_data
        track_id = track.get('id', '')
        
        if not track_id:
            ui.notify('Unable to open track: Missing track ID', color='negative')
            return
        
        # Store selected track for reference
        self.selected_track = track_data
        
        # Create the tab ID
        tab_id = f"track-{track_id}"
        
        # Basic info
        track_name = track.get('name', 'Unknown Track')
        artist_display = self._get_artist_display(track)
        album = track.get('album', {})
        album_name = album.get('name', 'Unknown Album') if isinstance(album, dict) else 'Unknown Album'
        
        # Get album image
        album_image = None
        if isinstance(album, dict) and 'images' in album and album['images']:
            images = album.get('images', [])
            if images and len(images) > 0 and isinstance(images[0], dict):
                album_image = images[0].get('url')
        
        # Get track URL
        track_url = None
        ext_urls = track.get('external_urls', {})
        if isinstance(ext_urls, dict) and 'spotify' in ext_urls:
            track_url = ext_urls.get('spotify')
        elif track_id:
            track_url = f"https://open.spotify.com/track/{track_id}"
        
        # Duration calculation
        duration_ms = int(track.get('duration_ms', 0))
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        duration = f"{minutes}:{seconds:02d}"
        
        # Check if the tab already exists and remove it if it does
        if tab_id in self.created_tabs:
            # Find and remove the existing tab
            print(f"[DEBUG APP] Tab {tab_id} already exists, removing it")
            # Remove from UI tabs
            tabs_to_keep = []
            for tab in self.playlist_tabs.children:
                if hasattr(tab, 'value') and tab.value == tab_id:
                    continue
                tabs_to_keep.append(tab)
                
            # Clear and rebuild tabs
            self.playlist_tabs.clear()
            with self.playlist_tabs:
                for tab in tabs_to_keep:
                    ui.component(tab)
                # Re-create the tab
                ui.tab(tab_id, track_name).props('no-caps')
                
            # Remove from tab panels
            for child in self.playlist_tab_panels.children:
                if hasattr(child, 'value') and child.value == tab_id:
                    child.clear()
        else:
            # Create new tab if it doesn't exist
            with self.playlist_tabs:
                ui.tab(tab_id, track_name).props('no-caps')
                self.created_tabs.add(tab_id)
        
        # Create tab panel with full content
        with self.playlist_tab_panels:
            with ui.tab_panel(tab_id).classes('p-4'):
                # Track header with album art and details
                with ui.row().classes('w-full justify-between items-start mb-6'):
                    # Left side: Back button
                    back_text = "Back to Playlist" if self.selected_playlist else "Back"
                    ui.button(back_text, icon='arrow_back').on('click', self._handle_back_from_track).classes('bg-blue-500 text-white')
                    
                    # Right side: Action buttons
                    with ui.row().classes('gap-2'):
                        if track_url:
                            with ui.link(target=track_url, new_tab=True).classes('no-underline'):
                                ui.button('Open in Spotify', icon='open_in_new').classes('bg-green-600 text-white')
                
                # Track content with album art and details
                with ui.row().classes('w-full gap-6 mb-6 items-start'):
                    # Album image - larger size
                    if album_image:
                        ui.image(album_image).classes('w-56 h-56 object-cover rounded-lg shadow')
                    else:
                        with ui.element('div').classes('w-56 h-56 bg-gray-200 flex items-center justify-center rounded-lg shadow'):
                            ui.icon('music_note', size='xl').classes('text-gray-400')
                    
                    # Track details
                    with ui.column().classes('flex-grow gap-2 ml-2'):
                        ui.label(track_name).classes('text-h4 font-bold')
                        ui.label(f"Artist: {artist_display}").classes('text-h6')
                        ui.label(f"Album: {album_name}").classes('text-lg')
                        ui.label(f"Duration: {duration}").classes('text-body1')
                        
                        # Optional popularity badge if available
                        if 'popularity' in track:
                            ui.label(f"Popularity: {track.get('popularity')}/100").classes('text-body2 text-gray-700')
                        
                        # Optional release date if available
                        if isinstance(album, dict) and 'release_date' in album:
                            ui.label(f"Released: {album.get('release_date')}").classes('text-body2 text-gray-700')
                
                # Audio features section if available
                audio_features = None
                if track_id:
                    audio_features = self._get_track_audio_features(track_id)
                    
                if audio_features:
                    ui.separator().classes('my-4')
                    ui.label("Audio Features").classes('text-h6 mb-4')
                    
                    # Display audio features in a grid of cards
                    with ui.grid(columns=4).classes('w-full gap-4 mb-6'):
                        # Features to display
                        features = [
                            ('Danceability', audio_features.get('danceability', 0), 'emoji_emotions'),
                            ('Energy', audio_features.get('energy', 0), 'bolt'),
                            ('Acousticness', audio_features.get('acousticness', 0), 'acoustic_detector'),
                            ('Instrumentalness', audio_features.get('instrumentalness', 0), 'piano'),
                            ('Liveness', audio_features.get('liveness', 0), 'mic'),
                            ('Valence', audio_features.get('valence', 0), 'sentiment_satisfied'),
                            ('Speechiness', audio_features.get('speechiness', 0), 'record_voice_over'),
                            ('Tempo', audio_features.get('tempo', 0), 'speed', False)
                        ]
                        
                        for feature in features:
                            name, value, icon, *args = feature
                            is_percent = len(args) == 0 or args[0]  # Default is True if not specified
                            
                            with ui.card().classes('p-4 bg-gray-50'):
                                with ui.row().classes('items-center w-full gap-2'):
                                    ui.icon(icon).classes('text-blue-500')
                                    ui.label(name).classes('text-sm font-bold')
                                
                                if is_percent:
                                    # For percentage values (0-1)
                                    percentage = int(value * 100)
                                    with ui.linear_progress(value=value).classes('w-full my-2'):
                                        pass
                                    ui.label(f"{percentage}%").classes('text-right w-full text-sm')
                                else:
                                    # For non-percentage values (like tempo)
                                    ui.label(f"{value:.1f}").classes('text-xl font-bold mt-2')
                
                # Related Artists section - fetch from LastFM API
                ui.separator().classes('my-4')
                
                # Track whether we're using real or dummy data
                using_real_data = False
                
                with ui.row().classes('items-center justify-between mb-2'):
                    ui.label("Related Artists").classes('text-h6')
                    
                    # Add data source indicator with tooltip
                    with ui.tooltip('Artist similarity data powered by Last.fm API'):
                        ui.badge(
                            "Data from Last.fm", 
                            color="green"
                        ).props('outline').classes('text-xs')
                
                # Get artist name from track for LastFM lookup
                primary_artist = None
                if 'artists' in track and isinstance(track['artists'], list) and len(track['artists']) > 0:
                    primary_artist = track['artists'][0].get('name') if isinstance(track['artists'][0], dict) else None
                
                # Try to get similar artists from LastFM if we have an artist name
                lastfm_artists = []
                if primary_artist:
                    try:
                        # Import LastFMService here to avoid circular imports
                        from src.spotify_playlist_generator.services.lastfm_service import LastFMService
                        
                        # Initialize LastFM service
                        lastfm_service = LastFMService()
                        # Fetch 10 related artists to have extras if some aren't found on Spotify
                        lastfm_artists = lastfm_service.get_similar_artists(primary_artist, limit=10)
                        using_real_data = True
                        
                        print(f"[DEBUG APP] Found {len(lastfm_artists)} related artists for {primary_artist} from LastFM API")
                    except Exception as e:
                        print(f"[DEBUG APP] Error fetching related artists from LastFM: {str(e)}")
                        # Fall back to dummy data if LastFM fails
                        lastfm_artists = []
                
                # Cross-reference with Spotify to get high-quality artist data and images
                related_artists = []
                spotify_artists_count = 0
                max_displayed_artists = 5
                
                if lastfm_artists and self.spotify_service:
                    for artist in lastfm_artists:
                        if spotify_artists_count >= max_displayed_artists:
                            break
                            
                        artist_name = artist.get('name', '')
                        if not artist_name:
                            continue
                            
                        try:
                            # Search for the artist on Spotify
                            spotify_artist = self.spotify_service.search_artist(artist_name)
                            if spotify_artist:
                                # Combine LastFM match score with Spotify artist data
                                spotify_artist['match'] = artist.get('match', 0)
                                related_artists.append(spotify_artist)
                                spotify_artists_count += 1
                                print(f"[DEBUG APP] Found Spotify data for artist: {artist_name}")
                            else:
                                print(f"[DEBUG APP] No Spotify data found for artist: {artist_name}")
                        except Exception as e:
                            print(f"[DEBUG APP] Error searching Spotify for artist '{artist_name}': {str(e)}")
                
                # If we couldn't find any artists on Spotify or LastFM failed, use dummy data
                if not related_artists:
                    related_artists = self._get_dummy_similar_artists('any-id')
                    using_real_data = False
                    print(f"[DEBUG APP] Using dummy related artists (no Spotify artists found)")
                
                # Update the badge color if we're using dummy data
                if not using_real_data:
                    # Find the badge and update its properties
                    for child in ui.current.children:
                        if hasattr(child, 'props') and hasattr(child, 'text') and child.text == "Data from Last.fm":
                            child.text = "Demo Data"
                            child.color = "orange"
                            break
                
                if related_artists:
                    with ui.grid(columns=5).classes('w-full gap-4'):
                        for artist in related_artists[:5]:
                            if not isinstance(artist, dict):
                                continue
                                
                            with ui.card().classes('p-3 hover:bg-gray-50'):
                                artist_name = artist.get('name', 'Unknown')
                                
                                # Get Spotify URL for the artist
                                artist_url = None
                                if 'external_urls' in artist and isinstance(artist['external_urls'], dict):
                                    artist_url = artist['external_urls'].get('spotify')
                                elif 'id' in artist:
                                    artist_id = artist.get('id', '')
                                    if artist_id:
                                        artist_url = f"https://open.spotify.com/artist/{artist_id}"
                                
                                # Layout structure for consistent appearance
                                with ui.column().classes('w-full items-center gap-2'):
                                    # Artist image from Spotify
                                    artist_image = None
                                    if 'images' in artist and isinstance(artist['images'], list) and len(artist['images']) > 0:
                                        img = artist['images'][0]
                                        if isinstance(img, dict) and 'url' in img:
                                            artist_image = img.get('url')
                                    
                                    if artist_image:
                                        # Use try-except to handle any image loading errors
                                        try:
                                            ui.image(artist_image).classes('w-full aspect-square object-cover rounded-full')
                                        except Exception as img_error:
                                            print(f"[DEBUG APP] Error loading artist image: {str(img_error)}")
                                            with ui.element('div').classes('w-full aspect-square bg-gray-200 flex items-center justify-center rounded-full'):
                                                ui.icon('person').classes('text-gray-400')
                                    else:
                                        with ui.element('div').classes('w-full aspect-square bg-gray-200 flex items-center justify-center rounded-full'):
                                            ui.icon('person').classes('text-gray-400')
                                    
                                    # Artist name 
                                    if artist_url:
                                        with ui.link(target=artist_url, new_tab=True).classes('no-underline'):
                                            ui.label(artist_name).classes('text-center text-sm font-bold text-blue-600 hover:underline mt-1')
                                    else:
                                        ui.label(artist_name).classes('text-center text-sm font-bold mt-1')
                                    
                                    # Match score from LastFM with visual indicator
                                    if 'match' in artist:
                                        try:
                                            match_value = float(artist.get('match', 0))
                                            if match_value > 0:
                                                # Show as percentage with progress bar
                                                match_percent = int(match_value * 100)
                                                ui.label(f"Match: {match_percent}%").classes('text-xs text-center w-full')
                                                with ui.linear_progress(value=match_value).classes('w-full'):
                                                    pass
                                        except (ValueError, TypeError):
                                            # Skip match display if value is invalid
                                            pass
                else:
                    ui.label("No related artists available").classes('text-gray-500')
        
        # Now switch to the tab
        self.playlist_tabs.set_value(tab_id)
        print(f"[DEBUG APP] Track detail tab created and populated")
    
    def _get_artist_display(self, track):
        """Helper to get artist display string from track data."""
        artists = track.get('artists', [])
        artist_names = [a.get('name', '') for a in artists if isinstance(a, dict) and 'name' in a]
        return ', '.join(artist_names) if artist_names else 'Unknown Artist'
    
    def _handle_back_from_track(self):
        """Go back to the playlist detail view."""
        if self.selected_playlist:
            # Switch back to the playlist tab
            self.playlist_tabs.value = f"playlist-{self.selected_playlist['id']}"
            # Clear the selected track
            self.selected_track = None
        else:
            # If no playlist context, go back to the main playlists view
            self._back_to_playlists()
    
    def _get_dummy_similar_artists(self, artist_id):
        """
        Return hard-coded dummy related artists instead of calling the Spotify API.
        
        Args:
            artist_id (str): Artist ID (unused, just for interface compatibility)
            
        Returns:
            list: A list of dummy artist objects
        """
        print(f"[DEBUG APP] Generating dummy related artists (artist_id: {artist_id})")
        
        try:
            # Hard-coded dummy data with the same structure as Spotify API response
            dummy_artists = [
                {
                    "id": "4tZwfgrHOc3mvqYlEYSvVi",
                    "name": "Daft Punk",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab6761610000e5eb8b9b5ce15d72215db8e35fbd",
                            "width": 640,
                            "height": 640
                        }
                    ]
                },
                {
                    "id": "5INjqkS1o8h1imAzPqGZBb",
                    "name": "Tame Impala",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab6761610000e5eb5d2b407da59dcc18e7c04c04", 
                            "width": 640, 
                            "height": 640
                        }
                    ]
                },
                {
                    "id": "7dGJo4pcD2V6oG8kP0tJRR",
                    "name": "Eminem",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab6761610000e5eba00b11c129b27a88fc72f36b",
                            "width": 640,
                            "height": 640
                        }
                    ]
                },
                {
                    "id": "1dfeR4HaWDbWqFHLkxsg1d",
                    "name": "Queen",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/b040846ceba13c3e9c125d68389491094e7f2982",
                            "width": 640,
                            "height": 640
                        }
                    ]
                },
                {
                    "id": "53XhwfbYqKCa1cC15pYq2q",
                    "name": "Imagine Dragons",
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab6761610000e5eb20bbcd5173599c6c8e5dbfa7",
                            "width": 640,
                            "height": 640
                        }
                    ]
                }
            ]
            
            print(f"[DEBUG APP] Returning {len(dummy_artists)} hard-coded dummy artists")
            return dummy_artists
        except Exception as e:
            print(f"[DEBUG APP] Error getting dummy similar artists: {str(e)}")
            # Return a minimal fallback list that won't cause errors
            return [
                {
                    "id": "4tZwfgrHOc3mvqYlEYSvVi",
                    "name": "Daft Punk",
                    "images": []
                },
                {
                    "id": "1dfeR4HaWDbWqFHLkxsg1d",
                    "name": "Queen",
                    "images": []
                }
            ]
            
    def _get_track_audio_features(self, track_id):
        """
        Get audio features for a track from the Spotify API.
        
        Args:
            track_id (str): The Spotify track ID
            
        Returns:
            dict: Dictionary containing audio features or None
        """
        if not self.spotify_service:
            print("[DEBUG APP] No Spotify service available for audio features fetch")
            return None
            
        try:
            audio_features = self.spotify_service.get_track_audio_features(track_id)
            return audio_features
        except Exception as e:
            print(f"[DEBUG APP] Error fetching track audio features: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None 