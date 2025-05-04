"""
Unit tests for the playlist model.
"""
import unittest
from src.spotify_playlist_generator.models.playlist import Track, Playlist


class TestTrack(unittest.TestCase):
    """Test cases for the Track class."""

    def test_track_init(self):
        """Test Track initialization with direct parameters."""
        track = Track(
            id="1234567890",
            name="Test Track",
            artist="Test Artist",
            album="Test Album",
            uri="spotify:track:1234567890"
        )
        
        self.assertEqual(track.id, "1234567890")
        self.assertEqual(track.name, "Test Track")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(track.uri, "spotify:track:1234567890")

    def test_track_from_spotify_track(self):
        """Test Track creation from Spotify API data."""
        # Test with complete data
        spotify_data = {
            "id": "1234567890",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "uri": "spotify:track:1234567890"
        }
        
        track = Track.from_spotify_track(spotify_data)
        
        self.assertEqual(track.id, "1234567890")
        self.assertEqual(track.name, "Test Track")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(track.uri, "spotify:track:1234567890")
        
    def test_track_from_spotify_track_nested(self):
        """Test Track creation from nested Spotify API data."""
        # Test with nested track format (as in playlist items)
        spotify_data = {
            "track": {
                "id": "1234567890",
                "name": "Test Track",
                "artists": [{"name": "Test Artist"}],
                "album": {"name": "Test Album"},
                "uri": "spotify:track:1234567890"
            }
        }
        
        track = Track.from_spotify_track(spotify_data)
        
        self.assertEqual(track.id, "1234567890")
        self.assertEqual(track.name, "Test Track")
        self.assertEqual(track.artist, "Test Artist")
        self.assertEqual(track.album, "Test Album")
        self.assertEqual(track.uri, "spotify:track:1234567890")
        
    def test_track_from_spotify_track_missing_data(self):
        """Test Track creation with missing data."""
        # Missing various fields
        spotify_data = {
            "id": "1234567890",
            "name": "Test Track",
            # Missing artists
            # Missing album
            "uri": "spotify:track:1234567890"
        }
        
        track = Track.from_spotify_track(spotify_data)
        
        self.assertEqual(track.id, "1234567890")
        self.assertEqual(track.name, "Test Track")
        self.assertEqual(track.artist, "Unknown Artist")
        self.assertEqual(track.album, "Unknown Album")
        self.assertEqual(track.uri, "spotify:track:1234567890")
        
        # Completely empty data
        empty_track = Track.from_spotify_track({})
        
        self.assertEqual(empty_track.id, "")
        self.assertEqual(empty_track.name, "")
        self.assertEqual(empty_track.artist, "Unknown Artist")
        self.assertEqual(empty_track.album, "Unknown Album")
        self.assertEqual(empty_track.uri, "")


class TestPlaylist(unittest.TestCase):
    """Test cases for the Playlist class."""

    def test_playlist_init(self):
        """Test Playlist initialization with direct parameters."""
        track1 = Track(
            id="track1",
            name="Track 1",
            artist="Artist 1",
            album="Album 1",
            uri="spotify:track:track1"
        )
        
        track2 = Track(
            id="track2",
            name="Track 2",
            artist="Artist 2",
            album="Album 2",
            uri="spotify:track:track2"
        )
        
        playlist = Playlist(
            id="playlist123",
            name="My Playlist",
            description="A test playlist",
            owner="Test User",
            tracks=[track1, track2],
            image_url="https://example.com/image.jpg",
            uri="spotify:playlist:playlist123"
        )
        
        self.assertEqual(playlist.id, "playlist123")
        self.assertEqual(playlist.name, "My Playlist")
        self.assertEqual(playlist.description, "A test playlist")
        self.assertEqual(playlist.owner, "Test User")
        self.assertEqual(len(playlist.tracks), 2)
        self.assertEqual(playlist.tracks[0].id, "track1")
        self.assertEqual(playlist.tracks[1].id, "track2")
        self.assertEqual(playlist.image_url, "https://example.com/image.jpg")
        self.assertEqual(playlist.uri, "spotify:playlist:playlist123")
        
    def test_playlist_from_spotify_playlist(self):
        """Test Playlist creation from Spotify API data."""
        # Spotify playlist data
        playlist_data = {
            "id": "playlist123",
            "name": "My Playlist",
            "description": "A test playlist",
            "owner": {"display_name": "Test User"},
            "images": [{"url": "https://example.com/image.jpg"}],
            "uri": "spotify:playlist:playlist123"
        }
        
        # Spotify track data
        track_data = [
            {
                "track": {
                    "id": "track1",
                    "name": "Track 1",
                    "artists": [{"name": "Artist 1"}],
                    "album": {"name": "Album 1"},
                    "uri": "spotify:track:track1"
                }
            },
            {
                "track": {
                    "id": "track2",
                    "name": "Track 2",
                    "artists": [{"name": "Artist 2"}],
                    "album": {"name": "Album 2"},
                    "uri": "spotify:track:track2"
                }
            }
        ]
        
        playlist = Playlist.from_spotify_playlist(playlist_data, track_data)
        
        self.assertEqual(playlist.id, "playlist123")
        self.assertEqual(playlist.name, "My Playlist")
        self.assertEqual(playlist.description, "A test playlist")
        self.assertEqual(playlist.owner, "Test User")
        self.assertEqual(len(playlist.tracks), 2)
        self.assertEqual(playlist.tracks[0].id, "track1")
        self.assertEqual(playlist.tracks[0].name, "Track 1")
        self.assertEqual(playlist.tracks[1].id, "track2")
        self.assertEqual(playlist.tracks[1].name, "Track 2")
        self.assertEqual(playlist.image_url, "https://example.com/image.jpg")
        self.assertEqual(playlist.uri, "spotify:playlist:playlist123")
        
    def test_playlist_from_spotify_playlist_no_tracks(self):
        """Test Playlist creation without tracks."""
        playlist_data = {
            "id": "playlist123",
            "name": "My Playlist",
            "description": "A test playlist",
            "owner": {"display_name": "Test User"},
            "images": [{"url": "https://example.com/image.jpg"}],
            "uri": "spotify:playlist:playlist123"
        }
        
        playlist = Playlist.from_spotify_playlist(playlist_data)
        
        self.assertEqual(playlist.id, "playlist123")
        self.assertEqual(playlist.name, "My Playlist")
        self.assertEqual(playlist.description, "A test playlist")
        self.assertEqual(playlist.owner, "Test User")
        self.assertEqual(len(playlist.tracks), 0)
        self.assertEqual(playlist.image_url, "https://example.com/image.jpg")
        self.assertEqual(playlist.uri, "spotify:playlist:playlist123")
        
    def test_playlist_from_spotify_playlist_missing_data(self):
        """Test Playlist creation with missing data."""
        # Missing or empty fields
        playlist_data = {
            "id": "playlist123",
            "name": "My Playlist",
            # Missing description
            # Missing owner
            "images": [],  # Empty images array
            # Missing URI
        }
        
        playlist = Playlist.from_spotify_playlist(playlist_data)
        
        self.assertEqual(playlist.id, "playlist123")
        self.assertEqual(playlist.name, "My Playlist")
        self.assertEqual(playlist.description, "")
        self.assertEqual(playlist.owner, "Unknown")
        self.assertEqual(len(playlist.tracks), 0)
        self.assertIsNone(playlist.image_url)
        self.assertIsNone(playlist.uri)
        
        # Completely empty data
        empty_playlist = Playlist.from_spotify_playlist({})
        
        self.assertEqual(empty_playlist.id, "")
        self.assertEqual(empty_playlist.name, "")
        self.assertEqual(empty_playlist.description, "")
        self.assertEqual(empty_playlist.owner, "Unknown")
        self.assertEqual(len(empty_playlist.tracks), 0)
        self.assertIsNone(empty_playlist.image_url)
        self.assertIsNone(empty_playlist.uri)


if __name__ == '__main__':
    unittest.main() 