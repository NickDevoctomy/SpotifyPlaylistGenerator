"""
Main application UI for the Spotify Playlist Generator.
"""
from nicegui import ui, app
import asyncio
import webbrowser
from fastapi.responses import HTMLResponse
from src.spotify_playlist_generator.services.auth_service import SpotifyAuthService

class AppUI:
    """Main UI class that handles the application interface."""
    
    def __init__(self):
        """Initialize the UI components."""
        self.auth_service = SpotifyAuthService()
        self.is_authenticated = False
        self.user_info = None
        
        # Set up the callback route for Spotify OAuth
        self._setup_callback_route()
        
        # Check if already authenticated
        if self.auth_service.check_token():
            self.is_authenticated = True
            self.user_info = self.auth_service.get_user_info()
        
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
                success = self.auth_service.authenticate(code)
                if success:
                    self.is_authenticated = True
                    self.user_info = self.auth_service.get_user_info()
                    
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
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="error-icon">✗</div>
                            <h1>Authentication Failed</h1>
                            <p>Sorry, we couldn't authenticate you with Spotify.</p>
                            <p>Please try again or check your credentials.</p>
                            <p><a href="/">Return to Application</a></p>
                        </div>
                    </body>
                    </html>
                    """
                    return HTMLResponse(content=error_html)
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
    
    def _setup_playlists_tab(self):
        """Set up the content for the playlists tab."""
        with ui.card().classes('w-full'):
            ui.label('My Playlists Content').classes('text-h6')
            
            # Show a message if user is not authenticated
            if not self.is_authenticated:
                ui.label('Please log in to view your playlists').classes('text-subtitle1')
                ui.button('Login', icon='login').classes('bg-green-600 text-white').on('click', self._handle_login)
            else:
                # Content for authenticated users will be added here
                ui.label(f"Welcome {self.user_info.get('display_name', 'User')}!").classes('text-subtitle1')
                ui.label("Your playlists will appear here").classes('text-body1')
    
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