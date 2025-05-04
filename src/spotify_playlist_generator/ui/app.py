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

class AppUI:
    """Main UI class that handles the application interface."""
    
    def __init__(self):
        """Initialize the UI components."""
        self.auth_service = SpotifyAuthService()
        self.spotify_service = None
        self.is_authenticated = False
        self.user_info = None
        self.playlists = []
        
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
                        
                        # Create a proper HTML response
                        html_content = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authentication Successful</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    margin: 0;
                                    padding: 20px;
                                    background-color: #f5f5f5;
                                    color: #333;
                                    text-align: center;
                                }
                                .container {
                                    max-width: 600px;
                                    margin: 50px auto;
                                    padding: 20px;
                                    background-color: white;
                                    border-radius: 10px;
                                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                }
                                h1 {
                                    color: #1DB954;
                                }
                                .success-icon {
                                    font-size: 48px;
                                    color: #1DB954;
                                    margin-bottom: 20px;
                                }
                                .close-countdown {
                                    margin-top: 20px;
                                    font-style: italic;
                                    color: #666;
                                }
                            </style>
                            <script>
                                window.onload = function() {
                                    var countdown = 3;
                                    var countdownElement = document.getElementById('countdown');
                                    
                                    // Update countdown every second
                                    var interval = setInterval(function() {
                                        countdown -= 1;
                                        countdownElement.textContent = countdown;
                                        
                                        if (countdown <= 0) {
                                            clearInterval(interval);
                                            window.close();
                                            // If window doesn't close, redirect to main app
                                            setTimeout(function() {
                                                window.location.href = '/';
                                            }, 500);
                                        }
                                    }, 1000);
                                }
                            </script>
                        </head>
                        <body>
                            <div class="container">
                                <div class="success-icon">✓</div>
                                <h1>Authentication Successful!</h1>
                                <p>You have successfully logged in to Spotify.</p>
                                <p>You can close this window and return to the application.</p>
                                <p class="close-countdown">This window will close automatically in <span id="countdown">3</span> seconds...</p>
                            </div>
                        </body>
                        </html>
                        """
                        return HTMLResponse(content=html_content)
                    else:
                        error_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authentication Failed</title>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    margin: 0;
                                    padding: 20px;
                                    background-color: #f5f5f5;
                                    color: #333;
                                    text-align: center;
                                }
                                .container {
                                    max-width: 600px;
                                    margin: 50px auto;
                                    padding: 20px;
                                    background-color: white;
                                    border-radius: 10px;
                                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                }
                                h1 {
                                    color: #e74c3c;
                                }
                                .error-icon {
                                    font-size: 48px;
                                    color: #e74c3c;
                                    margin-bottom: 20px;
                                }
                                pre {
                                    text-align: left;
                                    background-color: #f8f8f8;
                                    padding: 10px;
                                    border-radius: 5px;
                                    overflow: auto;
                                    font-size: 12px;
                                }
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="error-icon">✗</div>
                                <h1>Authentication Failed</h1>
                                <p>Sorry, we couldn't authenticate you with Spotify.</p>
                                <p>Please check your Spotify credentials in the environment variables.</p>
                                <p>See application console for more details.</p>
                                <p><a href="/">Return to Application</a></p>
                            </div>
                        </body>
                        </html>
                        """
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
                error_html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>No Code Provided</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 20px;
                            background-color: #f5f5f5;
                            color: #333;
                            text-align: center;
                        }
                        .container {
                            max-width: 600px;
                            margin: 50px auto;
                            padding: 20px;
                            background-color: white;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }
                        h1 {
                            color: #f39c12;
                        }
                        .warning-icon {
                            font-size: 48px;
                            color: #f39c12;
                            margin-bottom: 20px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="warning-icon">⚠</div>
                        <h1>No Authorization Code</h1>
                        <p>No authorization code was provided.</p>
                        <p>Please try logging in again.</p>
                        <p><a href="/">Return to Application</a></p>
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(content=error_html)
    
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
            ui.add_head_html('''
            <style>
            .q-tabs--horizontal .q-tabs__content {
                justify-content: flex-start;
            }
            </style>
            ''')
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
        """Render the playlists in the UI."""
        if not hasattr(self, 'playlist_container'):
            return
            
        with self.playlist_container:
            if not self.playlists:
                ui.label('No playlists found').classes('text-subtitle1')
                return
                
            # Create a grid layout for playlists
            with ui.grid(columns=3).classes('w-full gap-4'):
                for playlist in self.playlists:
                    self._render_playlist_card(playlist)
    
    def _render_playlist_card(self, playlist):
        """Render a single playlist card."""
        # Get playlist data
        name = playlist.get('name', 'Unnamed Playlist')
        description = playlist.get('description', '')
        total_tracks = playlist.get('tracks', {}).get('total', 0)
        owner = playlist.get('owner', {}).get('display_name', 'Unknown')
        
        # Get the image URL (use the first image if available)
        image_url = None
        if playlist.get('images') and len(playlist['images']) > 0:
            image_url = playlist['images'][0].get('url')
        
        # Create a card for the playlist
        with ui.card().classes('w-full h-full'):
            if image_url:
                ui.image(image_url).classes('w-full aspect-square object-cover')
            else:
                # Placeholder for missing image
                with ui.element('div').classes('w-full aspect-square bg-gray-200 flex items-center justify-center'):
                    ui.icon('music_note', size='xl').classes('text-gray-400')
            
            with ui.card_section():
                ui.label(name).classes('font-bold text-lg truncate w-full')
                if description:
                    ui.label(description).classes('text-xs text-gray-500 h-8 overflow-hidden')
                
                with ui.row().classes('items-center justify-between w-full'):
                    ui.label(f"{total_tracks} tracks").classes('text-xs')
                    ui.label(f"By {owner}").classes('text-xs')
    
    def _setup_playlists_tab(self):
        """Set up the content for the playlists tab."""
        with ui.card().classes('w-full'):
            ui.label('My Playlists').classes('text-h6')
            
            # Show a message if user is not authenticated
            if not self.is_authenticated:
                ui.label('Please log in to view your playlists').classes('text-subtitle1')
                ui.button('Login', icon='login').classes('bg-green-600 text-white').on('click', self._handle_login)
            else:
                # Add refresh button
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label(f"Welcome {self.user_info.get('display_name', 'User')}!").classes('text-subtitle1')
                    ui.button('Refresh', icon='refresh').on('click', self._fetch_playlists)
                
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