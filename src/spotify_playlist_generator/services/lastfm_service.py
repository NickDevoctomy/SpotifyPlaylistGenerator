"""
Service for interacting with the Last.fm API.
"""
import os
import logging
import pylast
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class LastFMService:
    """Service for interacting with the Last.fm API."""
    
    def __init__(self, api_key: Optional[str] = None, shared_secret: Optional[str] = None):
        """
        Initialize the LastFM service.
        
        Args:
            api_key: Last.fm API key. If None, will try to get from environment variable.
            shared_secret: Last.fm API shared secret. If None, will try to get from environment variable.
        """
        self.api_key = api_key or os.environ.get("LASTFM_API_KEY")
        self.shared_secret = shared_secret or os.environ.get("LASTFM_SHARED_SECRET")
        self.network = None
        self.connect()
    
    def connect(self) -> bool:
        """
        Connect to the Last.fm API.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self.api_key or not self.shared_secret:
            logger.error("LastFM API key or shared secret not provided")
            return False
        
        try:
            # Connect to LastFM using web service session auth
            self.network = pylast.LastFMNetwork(
                api_key=self.api_key,
                api_secret=self.shared_secret,
            )
            logger.info("Successfully connected to LastFM API")
            return True
        except Exception as e:
            logger.error(f"Error connecting to LastFM API: {str(e)}")
            self.network = None
            return False
    
    def get_similar_artists(self, artist_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get artists similar to the given artist.
        
        Args:
            artist_name: Name of the artist to find similar artists for
            limit: Maximum number of similar artists to return
            
        Returns:
            List of similar artists with their details
        """
        if not self.network:
            logger.error("Not connected to LastFM API")
            return []
        
        try:
            logger.info(f"Getting similar artists for {artist_name}")
            artist = self.network.get_artist(artist_name)
            similar_artists = artist.get_similar(limit=limit)
            
            # Process the result into a structured format
            result = []
            for similar_artist, match_value in similar_artists:
                artist_data = {
                    "id": similar_artist.get_mbid() or "",
                    "name": similar_artist.get_name(),
                    "match": float(match_value),
                    "url": similar_artist.get_url(),
                    "images": []  # Initialize with empty images list by default
                }
                result.append(artist_data)
            
            return result
        except pylast.WSError as e:
            logger.error(f"LastFM API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting similar artists: {str(e)}")
            return []
    
    def _get_artist_images(self, artist: pylast.Artist) -> List[Dict[str, str]]:
        """
        Get images for an artist.
        
        Args:
            artist: pylast Artist object
            
        Returns:
            List of image dictionaries compatible with Spotify API format
        """
        # Note: Currently not used since direct access to get_info() causes errors
        # Returning an empty list for now to avoid errors
        # The API structure seems to have changed from what was expected
        return []
    
    def test_connection(self, test_artist: str = "Queen") -> Dict[str, Any]:
        """
        Test the LastFM API connection by getting similar artists for a test artist.
        
        Args:
            test_artist: Artist name to use for the test
            
        Returns:
            Dictionary with test result information
        """
        if not self.network:
            return {
                "success": False,
                "message": "Not connected to LastFM API",
                "data": None
            }
        
        try:
            similar_artists = self.get_similar_artists(test_artist, limit=5)
            return {
                "success": True,
                "message": f"Successfully retrieved {len(similar_artists)} similar artists for {test_artist}",
                "data": similar_artists
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error testing LastFM API: {str(e)}",
                "data": None
            } 