"""
Unit tests for the utils module.
"""
import unittest
from unittest.mock import patch

from src.spotify_playlist_generator.utils import (
    format_playlist_name,
    validate_spotify_uri,
    truncate_description,
    filter_playlists_by_owner,
    get_env_var
)


class TestUtils(unittest.TestCase):
    """Test cases for the utils module."""

    def test_format_playlist_name(self):
        """Test formatting playlist names."""
        # Test removing special characters
        self.assertEqual(format_playlist_name("My Playlist!@#$%^&*()"), "My Playlist")
        
        # Test stripping whitespace
        self.assertEqual(format_playlist_name("  My Playlist  "), "My Playlist")
        
        # Test truncating long names
        long_name = "This is a very long playlist name that should be truncated because it exceeds the limit"
        self.assertEqual(format_playlist_name(long_name), "This is a very long playlist name that should b...")
        
        # Test empty name
        self.assertEqual(format_playlist_name(""), "")
        
        # Test name with only special characters
        self.assertEqual(format_playlist_name("!@#$%^&*()"), "")

    def test_validate_spotify_uri(self):
        """Test validating Spotify URIs."""
        # Valid URIs
        self.assertTrue(validate_spotify_uri("spotify:track:1Uj0QobxhxpJQjjJbPNaIJ"))
        self.assertTrue(validate_spotify_uri("spotify:album:5HRPZQnY2Z18nvMmcyOvUy"))
        self.assertTrue(validate_spotify_uri("spotify:artist:1snhtMLeb2DYoMOcVbb8iB"))
        self.assertTrue(validate_spotify_uri("spotify:playlist:37i9dQZF1DWWGFQLoP9qlv"))
        
        # Invalid URIs
        self.assertFalse(validate_spotify_uri("spotify:track:invalid_id"))
        self.assertFalse(validate_spotify_uri("spotify:unknown:1Uj0QobxhxpJQjjJbPNaIJ"))
        self.assertFalse(validate_spotify_uri("not_a_spotify_uri"))
        self.assertFalse(validate_spotify_uri(""))
        
        # URI with correct format but not enough characters
        self.assertFalse(validate_spotify_uri("spotify:track:1Uj0QobxhxpJQjjJbPNaI"))
        
        # URI with correct format but too many characters
        self.assertFalse(validate_spotify_uri("spotify:track:1Uj0QobxhxpJQjjJbPNaIJK"))

    def test_truncate_description(self):
        """Test truncating descriptions."""
        # Short description (no truncation needed)
        self.assertEqual(truncate_description("This is a short description"), "This is a short description")
        
        # Long description (needs truncation)
        long_desc = "This is a very long description that exceeds the default maximum length of 100 characters and should be truncated with ellipsis."
        self.assertEqual(truncate_description(long_desc), "This is a very long description that exceeds the default maximum length of 100 characters and sho...")
        
        # Empty description
        self.assertEqual(truncate_description(""), "")
        
        # None description
        self.assertEqual(truncate_description(None), "")
        
        # Custom max length
        self.assertEqual(truncate_description("This is a test description", 10), "This is...")

    def test_filter_playlists_by_owner(self):
        """Test filtering playlists by owner."""
        # Sample playlist data
        playlists = [
            {"name": "Playlist 1", "owner": {"id": "user1", "display_name": "User 1"}},
            {"name": "Playlist 2", "owner": {"id": "user2", "display_name": "User 2"}},
            {"name": "Playlist 3", "owner": {"id": "user1", "display_name": "User 1"}},
            {"name": "Playlist 4", "owner": {"id": "user3", "display_name": "User 3"}},
        ]
        
        # Filter by user1
        user1_playlists = filter_playlists_by_owner(playlists, "user1")
        self.assertEqual(len(user1_playlists), 2)
        self.assertEqual(user1_playlists[0]["name"], "Playlist 1")
        self.assertEqual(user1_playlists[1]["name"], "Playlist 3")
        
        # Filter by user2
        user2_playlists = filter_playlists_by_owner(playlists, "user2")
        self.assertEqual(len(user2_playlists), 1)
        self.assertEqual(user2_playlists[0]["name"], "Playlist 2")
        
        # Filter by non-existent user
        nonexistent_user_playlists = filter_playlists_by_owner(playlists, "nonexistent")
        self.assertEqual(len(nonexistent_user_playlists), 0)
        
        # Empty playlist list
        empty_result = filter_playlists_by_owner([], "user1")
        self.assertEqual(len(empty_result), 0)
        
        # Playlist with missing owner information
        malformed_playlists = [
            {"name": "Malformed Playlist"},
            {"name": "Correct Playlist", "owner": {"id": "user1"}}
        ]
        filtered_malformed = filter_playlists_by_owner(malformed_playlists, "user1")
        self.assertEqual(len(filtered_malformed), 1)
        self.assertEqual(filtered_malformed[0]["name"], "Correct Playlist")

    @patch('os.environ')
    def test_get_env_var(self, mock_environ):
        """Test getting environment variables."""
        # Set up mock environment variable
        mock_environ.get.side_effect = lambda key, default=None: {
            'EXISTING_VAR': 'value',
        }.get(key, default)
        
        # Test getting existing variable
        self.assertEqual(get_env_var('EXISTING_VAR'), 'value')
        
        # Test getting non-existent variable with default
        self.assertEqual(get_env_var('NON_EXISTENT_VAR', 'default_value'), 'default_value')
        
        # Test getting non-existent variable without default
        self.assertIsNone(get_env_var('NON_EXISTENT_VAR'))


if __name__ == '__main__':
    unittest.main() 