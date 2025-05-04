"""
Authentication service for Spotify OAuth.
"""
import os
import traceback
from typing import Optional, Dict, Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpotifyAuthService:
    """Service for handling Spotify authentication."""
    
    def __init__(self):
        """Initialize the Spotify authentication service."""
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8080/callback')
        self.scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
        self.sp_oauth = None
        self.client = None
        self.user_info = None
        self.token_info = None  # Store token in memory only
        
        # Debug info
        print(f"Auth Service initialized with: REDIRECT_URI={self.redirect_uri}")
        
        # Initialize OAuth if credentials are available
        if self.client_id and self.client_secret:
            self._initialize_oauth()
            print("OAuth initialized successfully")
        else:
            print("Warning: Missing Spotify credentials - client_id or client_secret not found in environment variables")
    
    def _initialize_oauth(self):
        """Initialize the Spotify OAuth manager."""
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            open_browser=False,
            cache_handler=None  # Disable any caching
        )
    
    def get_auth_url(self) -> str:
        """Get the Spotify authorization URL."""
        if not self.sp_oauth:
            self._initialize_oauth()
        
        if not self.sp_oauth:
            raise ValueError("Spotify OAuth could not be initialized. Check your credentials.")
        
        auth_url = self.sp_oauth.get_authorize_url()
        print(f"Generated auth URL: {auth_url[:50]}...")  # Only print first part for security
        return auth_url
    
    def authenticate(self, code: str) -> bool:
        """
        Authenticate with Spotify using the authorization code.
        
        Args:
            code: Authorization code from Spotify
            
        Returns:
            bool: True if authentication was successful
        """
        print(f"Authenticating with code: {code[:15]}...")  # Print only first part of code for security
        
        if not self.sp_oauth:
            print("Warning: OAuth manager not initialized during authenticate()")
            self._initialize_oauth()
            
        try:
            # Get the token and store it in memory only
            print("Getting access token...")
            self.token_info = self.sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
            print(f"Token received. Access token length: {len(self.token_info.get('access_token', ''))}")
            
            # Initialize Spotify client with the token
            print("Initializing Spotify client...")
            self.client = spotipy.Spotify(auth=self.token_info['access_token'])
            
            # Test the connection
            print("Testing connection by fetching user info...")
            self.user_info = self.client.current_user()
            print(f"Authentication successful. User: {self.user_info.get('display_name', 'Unknown')}")
            return True
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            print(traceback.format_exc())
            self.token_info = None
            self.client = None
            self.user_info = None
            return False
    
    def check_token(self) -> bool:
        """Check if the user is authenticated and refresh token if needed."""
        if not self.sp_oauth or not self.token_info:
            return False
        
        try:
            # Check if token needs refresh
            if self.sp_oauth.is_token_expired(self.token_info):
                print("Token expired, attempting to refresh...")
                try:
                    # Refresh token using the refresh token
                    if 'refresh_token' in self.token_info:
                        self.token_info = self.sp_oauth.refresh_access_token(self.token_info['refresh_token'])
                        # Update client with new token
                        self.client = spotipy.Spotify(auth=self.token_info['access_token'])
                        self.user_info = self.client.current_user()
                        print("Token refreshed successfully")
                        return True
                    else:
                        print("No refresh token available")
                        return False
                except Exception as e:
                    print(f"Token refresh error: {str(e)}")
                    return False
            
            # If we already have a valid token
            if self.client:
                try:
                    # Verify the token still works
                    self.user_info = self.client.current_user()
                    return True
                except Exception as e:
                    print(f"Error verifying token: {str(e)}")
                    return False
            
            return False
        except Exception as e:
            print(f"Error in check_token: {str(e)}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get the authenticated user's information."""
        return self.user_info
    
    def get_spotify_client(self) -> Optional[spotipy.Spotify]:
        """Get the authenticated Spotify client."""
        if self.check_token():
            return self.client
        return None
    
    def logout(self) -> None:
        """Log out the user by clearing the token and user info from memory."""
        print("Logging out, clearing all token data from memory")
        self.token_info = None
        self.client = None
        self.user_info = None 