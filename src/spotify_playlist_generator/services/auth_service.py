"""
Authentication service for Spotify OAuth.
"""
import os
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
        
        # Initialize OAuth if credentials are available
        if self.client_id and self.client_secret:
            self._initialize_oauth()
    
    def _initialize_oauth(self):
        """Initialize the Spotify OAuth manager."""
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=".spotify_cache"
        )
    
    def get_auth_url(self) -> str:
        """Get the Spotify authorization URL."""
        if not self.sp_oauth:
            self._initialize_oauth()
        
        if not self.sp_oauth:
            raise ValueError("Spotify OAuth could not be initialized. Check your credentials.")
            
        return self.sp_oauth.get_authorize_url()
    
    def authenticate(self, code: str) -> bool:
        """
        Authenticate with Spotify using the authorization code.
        
        Args:
            code: Authorization code from Spotify
            
        Returns:
            bool: True if authentication was successful
        """
        if not self.sp_oauth:
            self._initialize_oauth()
            
        try:
            token_info = self.sp_oauth.get_access_token(code)
            self.client = spotipy.Spotify(auth=token_info['access_token'])
            self.user_info = self.client.current_user()
            return True
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def check_token(self) -> bool:
        """Check if the user is authenticated."""
        if not self.sp_oauth:
            return False
        
        token_info = self.sp_oauth.get_cached_token()
        if not token_info:
            return False
        
        # Check if token needs refresh
        if self.sp_oauth.is_token_expired(token_info):
            token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
        
        self.client = spotipy.Spotify(auth=token_info['access_token'])
        try:
            self.user_info = self.client.current_user()
            return True
        except:
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
        """Log out the user by clearing the cache."""
        if os.path.exists(".spotify_cache"):
            os.remove(".spotify_cache")
        self.client = None
        self.user_info = None 