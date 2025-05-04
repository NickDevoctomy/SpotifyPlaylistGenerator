"""
Unit tests for the spotify_service module.
"""
import unittest
from unittest.mock import patch, MagicMock

from src.spotify_playlist_generator.services.spotify_service import SpotifyService


class TestSpotifyService(unittest.TestCase):
    """Test cases for the SpotifyService class."""

    def test_init(self):
        """Test service initialization."""
        # Create with no client
        service = SpotifyService()
        self.assertIsNone(service.client)
        
        # Create with mock client
        mock_client = MagicMock()
        service_with_client = SpotifyService(spotify_client=mock_client)
        self.assertEqual(service_with_client.client, mock_client)
    
    @patch('src.spotify_playlist_generator.services.spotify_service.spotipy.Spotify')
    @patch('src.spotify_playlist_generator.services.spotify_service.SpotifyOAuth')
    def test_authenticate_success(self, mock_spotify_oauth, mock_spotify):
        """Test successful authentication."""
        # Set up mocks
        mock_spotify_instance = mock_spotify.return_value
        mock_auth_manager = mock_spotify_oauth.return_value
        
        # Create service
        service = SpotifyService()
        
        # Test authentication
        result = service.authenticate(
            client_id='test_client_id',
            client_secret='test_client_secret',
            redirect_uri='http://test.com/callback'
        )
        
        # Verify authentication
        self.assertTrue(result)
        mock_spotify_oauth.assert_called_once_with(
            client_id='test_client_id',
            client_secret='test_client_secret',
            redirect_uri='http://test.com/callback',
            scope="user-library-read playlist-read-private playlist-modify-private playlist-modify-public"
        )
        mock_spotify.assert_called_once_with(auth_manager=mock_auth_manager)
        mock_spotify_instance.current_user.assert_called_once()
        self.assertEqual(service.client, mock_spotify_instance)
    
    @patch('src.spotify_playlist_generator.services.spotify_service.spotipy.Spotify')
    @patch('src.spotify_playlist_generator.services.spotify_service.SpotifyOAuth')
    def test_authenticate_failure(self, mock_spotify_oauth, mock_spotify):
        """Test authentication failure."""
        # Set up mocks
        mock_spotify_instance = mock_spotify.return_value
        mock_spotify_instance.current_user.side_effect = Exception("Authentication error")
        
        # Create service
        service = SpotifyService()
        
        # Test authentication
        result = service.authenticate(
            client_id='test_client_id',
            client_secret='test_client_secret',
            redirect_uri='http://test.com/callback'
        )
        
        # Verify authentication failed
        self.assertFalse(result)
    
    def test_get_user_playlists_no_client(self):
        """Test getting playlists with no client."""
        # Create service with no client
        service = SpotifyService()
        
        # Get playlists
        playlists = service.get_user_playlists()
        
        # Verify empty list is returned
        self.assertEqual(playlists, [])
    
    def test_get_user_playlists_success(self):
        """Test getting playlists successfully."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.current_user_playlists.return_value = {
            'items': [
                {
                    'id': 'playlist1',
                    'name': 'Playlist 1',
                    'description': 'Test playlist 1',
                    'owner': {'display_name': 'Test User'},
                    'images': [{'url': 'http://example.com/image1.jpg'}],
                    'tracks': {'total': 10}
                },
                {
                    'id': 'playlist2',
                    'name': 'Playlist 2',
                    'description': 'Test playlist 2',
                    'owner': {'display_name': 'Test User'},
                    'images': [],  # Empty images
                    'tracks': {'total': 5}
                }
            ]
        }
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get playlists
        playlists = service.get_user_playlists(limit=10, offset=0)
        
        # Verify playlists are returned
        self.assertEqual(len(playlists), 2)
        self.assertEqual(playlists[0]['id'], 'playlist1')
        self.assertEqual(playlists[1]['id'], 'playlist2')
        
        # Verify missing images were handled
        self.assertIsNotNone(playlists[1]['images'])
        self.assertIsNone(playlists[1]['images'][0]['url'])
        
        # Verify client was called with correct params
        mock_client.current_user_playlists.assert_called_once_with(limit=10, offset=0)
    
    def test_get_user_playlists_with_missing_tracks(self):
        """Test getting playlists with missing tracks field."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.current_user_playlists.return_value = {
            'items': [
                {
                    'id': 'playlist1',
                    'name': 'Playlist 1',
                    'description': 'Test playlist 1',
                    'owner': {'display_name': 'Test User'},
                    'images': [{'url': 'http://example.com/image1.jpg'}]
                    # Missing 'tracks' field
                }
            ]
        }
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get playlists
        playlists = service.get_user_playlists()
        
        # Verify tracks field was added
        self.assertEqual(len(playlists), 1)
        self.assertEqual(playlists[0]['id'], 'playlist1')
        self.assertIn('tracks', playlists[0])
        self.assertEqual(playlists[0]['tracks']['total'], 0)
    
    def test_get_user_playlists_error(self):
        """Test error handling when getting playlists."""
        # Create mock client that raises exception
        mock_client = MagicMock()
        mock_client.current_user_playlists.side_effect = Exception("API error")
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get playlists
        playlists = service.get_user_playlists()
        
        # Verify empty list is returned on error
        self.assertEqual(playlists, [])
    
    def test_get_playlist_tracks_no_client(self):
        """Test getting playlist tracks with no client."""
        # Create service with no client
        service = SpotifyService()
        
        # Get tracks
        tracks = service.get_playlist_tracks('playlist1')
        
        # Verify empty list is returned
        self.assertEqual(tracks, [])
    
    def test_get_playlist_tracks_success(self):
        """Test getting playlist tracks successfully."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.playlist_tracks.return_value = {
            'items': [
                {
                    'track': {
                        'id': 'track1',
                        'name': 'Track 1',
                        'artists': [{'name': 'Artist 1'}],
                        'album': {'name': 'Album 1', 'images': []}
                    }
                },
                {
                    'track': {
                        'id': 'track2',
                        'name': 'Track 2',
                        'artists': [{'name': 'Artist 2'}],
                        'album': {'name': 'Album 2', 'images': []}
                    }
                }
            ]
        }
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get tracks
        tracks = service.get_playlist_tracks('playlist1', limit=50, offset=0)
        
        # Verify tracks are returned
        self.assertEqual(len(tracks), 2)
        self.assertEqual(tracks[0]['track']['id'], 'track1')
        self.assertEqual(tracks[1]['track']['id'], 'track2')
        
        # Verify client was called with correct params
        mock_client.playlist_tracks.assert_called_once_with(
            'playlist1',
            limit=50,
            offset=0,
            fields='items(track(id,name,artists(name),album(name,images)))'
        )
    
    def test_get_playlist_tracks_error(self):
        """Test error handling when getting playlist tracks."""
        # Create mock client that raises exception
        mock_client = MagicMock()
        mock_client.playlist_tracks.side_effect = Exception("API error")
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get tracks
        tracks = service.get_playlist_tracks('playlist1')
        
        # Verify empty list is returned on error
        self.assertEqual(tracks, [])


if __name__ == '__main__':
    unittest.main() 