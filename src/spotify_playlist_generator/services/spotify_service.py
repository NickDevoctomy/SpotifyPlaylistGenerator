"""
Spotify API service for interacting with the Spotify Web API.
"""
import os
from typing import List, Dict, Any, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyService:
    """Service for interacting with Spotify API."""
    
    def __init__(self):
        """Initialize the Spotify API client."""
        self.client = None
        self.is_authenticated = False
    
    def authenticate(self, client_id: str, client_secret: str, redirect_uri: str) -> bool:
        """
        Authenticate with Spotify API.
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            redirect_uri: Redirect URI for OAuth flow
            
        Returns:
            bool: True if authentication was successful
        """
        try:
            scope = "user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
            self.client = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=scope
                )
            )
            # Test the connection
            self.client.current_user()
            self.is_authenticated = True
            return True
        except Exception:
            self.is_authenticated = False
            return False
    
    def get_user_playlists(self) -> List[Dict[str, Any]]:
        """
        Get user's playlists.
        
        Returns:
            List of playlist dictionaries
        """
        if not self.is_authenticated or not self.client:
            return []
        
        try:
            results = self.client.current_user_playlists()
            return results.get('items', [])
        except Exception:
            return [] 