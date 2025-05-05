"""
Unit tests for LastFM service.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import pylast

from src.spotify_playlist_generator.services.lastfm_service import LastFMService

class TestLastFMService(unittest.TestCase):
    """Tests for the LastFM service."""

    def setUp(self):
        """Set up test environment."""
        # Patch environment variables to ensure they don't affect tests
        self.env_patcher = patch.dict('os.environ', {
            'LASTFM_API_KEY': 'test_api_key',
            'LASTFM_SHARED_SECRET': 'test_shared_secret'
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()

    def test_init_with_explicit_credentials(self):
        """Test initialization with explicitly provided credentials."""
        service = LastFMService(api_key='explicit_key', shared_secret='explicit_secret')
        
        self.assertEqual(service.api_key, 'explicit_key')
        self.assertEqual(service.shared_secret, 'explicit_secret')
        
    def test_init_with_environment_variables(self):
        """Test initialization using environment variables."""
        service = LastFMService()
        
        self.assertEqual(service.api_key, 'test_api_key')
        self.assertEqual(service.shared_secret, 'test_shared_secret')
    
    @patch('src.spotify_playlist_generator.services.lastfm_service.pylast.LastFMNetwork')
    def test_connect_success(self, mock_lastfm_network):
        """Test successful connection to LastFM API."""
        # Set up mock
        mock_network = MagicMock()
        mock_lastfm_network.return_value = mock_network
        
        # Create service and test connect
        service = LastFMService(api_key='test_key', shared_secret='test_secret')
        result = service.connect()
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(service.network, mock_network)
        mock_lastfm_network.assert_has_calls([
            unittest.mock.call(
                api_key='test_key',
                api_secret='test_secret'
            )
        ])
        
    @patch('src.spotify_playlist_generator.services.lastfm_service.pylast.LastFMNetwork')
    def test_connect_missing_credentials(self, mock_lastfm_network):
        """Test connection failure due to missing credentials."""
        # Create service with no credentials
        with patch.dict('os.environ', {}, clear=True):
            service = LastFMService()
            result = service.connect()
        
        # Assertions
        self.assertFalse(result)
        self.assertIsNone(service.network)
        mock_lastfm_network.assert_not_called()
        
    @patch('src.spotify_playlist_generator.services.lastfm_service.pylast.LastFMNetwork')
    def test_connect_exception(self, mock_lastfm_network):
        """Test handling of exception during connection."""
        # Set up mock to raise exception
        mock_lastfm_network.side_effect = Exception("Connection error")
        
        # Create service and test connect
        service = LastFMService(api_key='test_key', shared_secret='test_secret')
        result = service.connect()
        
        # Assertions
        self.assertFalse(result)
        self.assertIsNone(service.network)
        
    def test_get_similar_artists_no_network(self):
        """Test getting similar artists with no network connection."""
        # Create service with no network
        service = LastFMService()
        service.network = None
        
        # Call method
        result = service.get_similar_artists("Test Artist")
        
        # Assertions
        self.assertEqual(result, [])
        
    @patch('pylast.Artist')
    @patch('src.spotify_playlist_generator.services.lastfm_service.pylast.LastFMNetwork')
    def test_get_similar_artists_success(self, mock_lastfm_network, mock_artist):
        """Test getting similar artists successfully."""
        # Set up mocks
        mock_network = MagicMock()
        mock_lastfm_network.return_value = mock_network
        
        mock_network.get_artist.return_value = mock_artist
        
        # Set up similar artists
        similar_artist1 = MagicMock()
        similar_artist1.get_mbid.return_value = "mbid1"
        similar_artist1.get_name.return_value = "Similar Artist 1"
        similar_artist1.get_url.return_value = "http://example.com/artist1"
        
        similar_artist2 = MagicMock()
        similar_artist2.get_mbid.return_value = None  # Test missing MBID
        similar_artist2.get_name.return_value = "Similar Artist 2"
        similar_artist2.get_url.return_value = "http://example.com/artist2"
        
        mock_artist.get_similar.return_value = [
            (similar_artist1, 0.9),
            (similar_artist2, 0.8)
        ]
        
        # Create service
        service = LastFMService()
        
        # Call method
        result = service.get_similar_artists("Test Artist", limit=2)
        
        # Assertions
        self.assertEqual(len(result), 2)
        
        self.assertEqual(result[0]["id"], "mbid1")
        self.assertEqual(result[0]["name"], "Similar Artist 1")
        self.assertEqual(result[0]["match"], 0.9)
        self.assertEqual(result[0]["url"], "http://example.com/artist1")
        
        self.assertEqual(result[1]["id"], "")  # Empty string for missing MBID
        self.assertEqual(result[1]["name"], "Similar Artist 2")
        self.assertEqual(result[1]["match"], 0.8)
        self.assertEqual(result[1]["url"], "http://example.com/artist2")
        
        # Verify the limit was passed
        mock_artist.get_similar.assert_called_once_with(limit=2)
        
    @patch('src.spotify_playlist_generator.services.lastfm_service.pylast.LastFMNetwork')
    def test_get_similar_artists_ws_error(self, mock_lastfm_network):
        """Test handling of WSError when getting similar artists."""
        # Set up mocks
        mock_network = MagicMock()
        mock_lastfm_network.return_value = mock_network
        
        mock_artist = MagicMock()
        mock_network.get_artist.return_value = mock_artist
        
        # Make get_similar raise WSError
        mock_artist.get_similar.side_effect = pylast.WSError("API error", 400, "error details")
        
        # Create service
        service = LastFMService()
        
        # Call method
        result = service.get_similar_artists("Test Artist")
        
        # Assertions
        self.assertEqual(result, [])
        
    @patch('src.spotify_playlist_generator.services.lastfm_service.pylast.LastFMNetwork')
    def test_get_similar_artists_general_exception(self, mock_lastfm_network):
        """Test handling of general exception when getting similar artists."""
        # Set up mocks
        mock_network = MagicMock()
        mock_lastfm_network.return_value = mock_network
        
        mock_artist = MagicMock()
        mock_network.get_artist.return_value = mock_artist
        
        # Make get_similar raise Exception
        mock_artist.get_similar.side_effect = Exception("General error")
        
        # Create service
        service = LastFMService()
        
        # Call method
        result = service.get_similar_artists("Test Artist")
        
        # Assertions
        self.assertEqual(result, [])
        
    def test_test_connection_no_network(self):
        """Test connection test with no network."""
        # Create service with no network
        service = LastFMService()
        service.network = None
        
        # Call method
        result = service.test_connection()
        
        # Assertions
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Not connected to LastFM API")
        self.assertIsNone(result["data"])
        
    @patch('src.spotify_playlist_generator.services.lastfm_service.LastFMService.get_similar_artists')
    def test_test_connection_success(self, mock_get_similar):
        """Test successful connection test."""
        # Set up mock
        mock_similar_artists = [
            {"name": "Similar Artist 1"},
            {"name": "Similar Artist 2"}
        ]
        mock_get_similar.return_value = mock_similar_artists
        
        # Create service
        service = LastFMService()
        service.network = MagicMock()  # Just need a non-None value
        
        # Call method
        result = service.test_connection("Test Artist")
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Successfully retrieved 2 similar artists for Test Artist")
        self.assertEqual(result["data"], mock_similar_artists)
        mock_get_similar.assert_called_once_with("Test Artist", limit=5)
        
    @patch('src.spotify_playlist_generator.services.lastfm_service.LastFMService.get_similar_artists')
    def test_test_connection_exception(self, mock_get_similar):
        """Test handling of exception during connection test."""
        # Set up mock to raise exception
        mock_get_similar.side_effect = Exception("Test error")
        
        # Create service
        service = LastFMService()
        service.network = MagicMock()  # Just need a non-None value
        
        # Call method
        result = service.test_connection()
        
        # Assertions
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Error testing LastFM API: Test error")
        self.assertIsNone(result["data"])

if __name__ == '__main__':
    unittest.main() 