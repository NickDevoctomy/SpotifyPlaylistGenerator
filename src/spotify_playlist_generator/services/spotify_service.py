"""
Spotify API service for interacting with the Spotify Web API.
"""
import os
from typing import List, Dict, Any, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyService:
    """Service for interacting with Spotify API."""
    
    def __init__(self, spotify_client=None):
        """
        Initialize the Spotify API client.
        
        Args:
            spotify_client: An authenticated Spotipy client instance
        """
        self.client = spotify_client
    
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
            return True
        except Exception:
            return False
    
    def get_user_playlists(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get user's playlists with details.
        
        Args:
            limit: Maximum number of playlists to return (default: 50, max: 50)
            offset: Index of the first playlist to return (default: 0)
            
        Returns:
            List of playlist dictionaries with details including:
            - id: Spotify playlist ID
            - name: Playlist name
            - description: Playlist description
            - owner: Owner's display name
            - images: List of images in different sizes
            - tracks: Track info including total count
            - public: Whether the playlist is public
            - collaborative: Whether the playlist is collaborative
        """
        if not self.client:
            print("Cannot get playlists: No authenticated Spotify client")
            return []
        
        try:
            results = self.client.current_user_playlists(limit=limit, offset=offset)
            playlists = results.get('items', [])
            
            # Add additional details for each playlist if needed
            for playlist in playlists:
                # Ensure we have image info
                if not playlist.get('images'):
                    playlist['images'] = [{'url': None}]
                    
                # Ensure track count is available
                if 'tracks' not in playlist:
                    playlist['tracks'] = {'total': 0}
            
            return playlists
        except Exception as e:
            print(f"Error fetching user playlists: {str(e)}")
            return []
    
    def get_playlist_tracks(self, playlist_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get tracks from a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            limit: Maximum number of tracks to return per request (default: 100, max: 100)
            offset: Index of the first track to return (default: 0)
            
        Returns:
            List of track dictionaries
        """
        if not self.client:
            print("Cannot get tracks: No authenticated Spotify client")
            return []
        
        try:
            print(f"[DEBUG] Making Spotify API request for playlist tracks. Playlist ID: {playlist_id}")
            print(f"[DEBUG] Request parameters: limit={limit}, offset={offset}")
            
            # Request track data
            try:
                # Use a simpler fields parameter that should be more reliable
                results = self.client.playlist_tracks(
                    playlist_id, 
                    limit=limit, 
                    offset=offset,
                    fields='items(track(id,name,uri,duration_ms,artists(id,name),album(id,name,images),external_urls))'
                )
            except Exception as specific_error:
                print(f"[DEBUG] Error with specific fields, trying minimal fields: {str(specific_error)}")
                # Fall back to minimal fields if the specific request fails
                results = self.client.playlist_tracks(
                    playlist_id, 
                    limit=limit, 
                    offset=offset,
                    fields='items'
                )
            
            tracks = results.get('items', [])
            print(f"[DEBUG] Retrieved {len(tracks)} tracks from Spotify API")
            
            # Ensure each track has the needed fields
            print("[DEBUG] Processing tracks to ensure required fields...")
            valid_tracks = []
            
            for i, track_item in enumerate(tracks):
                # Skip items without track data
                if 'track' not in track_item or track_item['track'] is None:
                    print(f"[DEBUG] Track at index {i} has no track data, skipping")
                    continue
                    
                track = track_item['track']
                
                # Ensure artists is an array
                if 'artists' not in track:
                    print(f"[DEBUG] Track '{track.get('name', 'Unknown')}' has no artists field, adding empty array")
                    track['artists'] = []
                else:
                    # Validate that artist entries have proper IDs
                    for idx, artist in enumerate(track['artists']):
                        if 'id' not in artist or not artist['id']:
                            print(f"[DEBUG] Artist {idx} ({artist.get('name', 'Unknown')}) missing ID")
                        elif not isinstance(artist['id'], str) or len(artist['id']) != 22:
                            print(f"[DEBUG] Artist {idx} ({artist.get('name', 'Unknown')}) has invalid ID: {artist['id']!r}")
                
                # Ensure album has images
                if 'album' not in track:
                    print(f"[DEBUG] Track '{track.get('name', 'Unknown')}' has no album field, adding default")
                    track['album'] = {'name': 'Unknown Album', 'images': []}
                elif 'images' not in track['album']:
                    print(f"[DEBUG] Album for track '{track.get('name', 'Unknown')}' has no images, adding empty array")
                    track['album']['images'] = []
                
                # Ensure external_urls exists
                if 'external_urls' not in track:
                    track['external_urls'] = {'spotify': f"https://open.spotify.com/track/{track.get('id', '')}"}
                
                valid_tracks.append(track_item)
            
            print(f"[DEBUG] Returning {len(valid_tracks)} valid tracks")
            return valid_tracks
        except Exception as e:
            print(f"[DEBUG] Error fetching playlist tracks: {str(e)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return []

    def get_saved_tracks(self):
        """Get the current user's saved tracks."""
        return self._paginate_all_items('me/tracks')

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """
        Add tracks to a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            track_uris: List of Spotify track URIs to add to the playlist
            
        Returns:
            bool: True if the operation was successful
        """
        if not self.client:
            print("Cannot add tracks: No authenticated Spotify client")
            return False
        
        try:
            self.client.playlist_add_items(playlist_id, track_uris)
            return True
        except Exception as e:
            print(f"Error adding tracks to playlist: {str(e)}")
            return False
            
    def get_track_audio_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio features for a track.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Dictionary containing audio features or None if not available
        """
        if not self.client:
            print("Cannot get audio features: No authenticated Spotify client")
            return None
        
        try:
            # Check if token might need refreshing
            if hasattr(self.client, '_auth') and hasattr(self.client._auth, 'is_token_expired') and self.client._auth.is_token_expired():
                print("Authentication token expired, refreshing...")
                if hasattr(self.client._auth, 'refresh_access_token'):
                    self.client._auth.refresh_access_token()
                    
            # Get audio features from the API
            audio_features = self.client.audio_features(track_id)
            
            if audio_features and len(audio_features) > 0:
                return audio_features[0]
            return None
        except Exception as e:
            # Check if this is a 403 Forbidden error
            if "403" in str(e):
                print(f"Access denied (403) when fetching audio features. The app might not have the required permissions: {str(e)}")
                # Return empty features to avoid errors
                return {
                    "danceability": 0.5,
                    "energy": 0.5,
                    "acousticness": 0.5,
                    "instrumentalness": 0.5,
                    "liveness": 0.5,
                    "valence": 0.5,
                    "speechiness": 0.5,
                    "tempo": 120
                }
            else:
                print(f"Error fetching track audio features: {str(e)}")
                import traceback
                print(traceback.format_exc())
                return None
            
    def search_artist(self, artist_name: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Search for an artist by name and return the top result.
        
        Args:
            artist_name: Name of the artist to search for
            timeout: Timeout in seconds for the API call (not used currently)
            
        Returns:
            Dictionary containing artist data or None if not found
        """
        if not self.client:
            print(f"Cannot search for artist '{artist_name}': No authenticated Spotify client")
            return None
        
        try:
            # Perform a search limited to artist type
            results = self.client.search(q=f"artist:{artist_name}", type="artist", limit=1)
            
            # Extract artists from results
            artists = results.get('artists', {}).get('items', [])
            
            # Return the first artist if available
            if artists and len(artists) > 0:
                artist = artists[0]
                # Ensure we have image info
                if not artist.get('images'):
                    artist['images'] = []
                return artist
                
            return None
        except Exception as e:
            print(f"Error searching for artist '{artist_name}': {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None 