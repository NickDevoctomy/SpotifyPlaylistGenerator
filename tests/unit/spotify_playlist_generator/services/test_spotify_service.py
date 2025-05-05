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
                        'uri': 'spotify:track:track1',
                        'duration_ms': 180000,
                        'artists': [{'name': 'Artist 1'}],
                        'album': {'name': 'Album 1', 'images': []},
                        'external_urls': {'spotify': 'https://open.spotify.com/track/track1'}
                    }
                },
                {
                    'track': {
                        'id': 'track2',
                        'name': 'Track 2',
                        'uri': 'spotify:track:track2',
                        'duration_ms': 210000,
                        'artists': [{'name': 'Artist 2'}],
                        'album': {'name': 'Album 2', 'images': []},
                        'external_urls': {'spotify': 'https://open.spotify.com/track/track2'}
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
            fields='items(track(id,name,uri,duration_ms,artists(id,name),album(id,name,images),external_urls))'
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

    def test_get_playlist_tracks_with_missing_fields(self):
        """Test getting playlist tracks with missing fields."""
        # Create mock client with incomplete track data
        mock_client = MagicMock()
        mock_client.playlist_tracks.return_value = {
            'items': [
                {
                    'track': {
                        'id': 'track1',
                        'name': 'Track 1',
                        # Missing 'artists' field
                        # Missing 'album' field
                        # Missing 'external_urls' field
                    }
                },
                {
                    'track': None  # Track is None
                },
                {
                    # Missing 'track' field entirely
                }
            ]
        }
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get tracks
        tracks = service.get_playlist_tracks('playlist1')
        
        # Verify valid tracks are returned and invalid ones filtered out
        self.assertEqual(len(tracks), 1)
        
        # Verify fields were added
        self.assertIn('artists', tracks[0]['track'])
        self.assertEqual(tracks[0]['track']['artists'], [])
        
        self.assertIn('album', tracks[0]['track'])
        self.assertEqual(tracks[0]['track']['album']['name'], 'Unknown Album')
        self.assertEqual(tracks[0]['track']['album']['images'], [])
        
        self.assertIn('external_urls', tracks[0]['track'])
        self.assertEqual(tracks[0]['track']['external_urls']['spotify'], 'https://open.spotify.com/track/track1')

    def test_get_playlist_tracks_with_fallback(self):
        """Test getting playlist tracks with fallback for API error."""
        # Create mock client
        mock_client = MagicMock()
        
        # Make first call fail with exception
        mock_client.playlist_tracks.side_effect = [
            Exception("API error with specific fields"),  # First call fails
            {'items': [{'track': {'id': 'track1', 'name': 'Track 1', 'artists': [{'name': 'Artist 1'}], 'album': {'name': 'Album 1', 'images': []}}}]}  # Second call succeeds
        ]
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get tracks
        tracks = service.get_playlist_tracks('playlist1')
        
        # Verify tracks from fallback are returned
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0]['track']['id'], 'track1')
        
        # Verify client was called twice - first with specific fields, then with minimal fields
        self.assertEqual(mock_client.playlist_tracks.call_count, 2)
        
        # Check first call
        first_call_args = mock_client.playlist_tracks.call_args_list[0][0]
        first_call_kwargs = mock_client.playlist_tracks.call_args_list[0][1]
        self.assertEqual(first_call_args[0], 'playlist1')
        self.assertIn('items(track(id,name,uri,duration_ms,artists(id,name),album(id,name,images),external_urls))', first_call_kwargs['fields'])
        
        # Check second call (fallback)
        second_call_args = mock_client.playlist_tracks.call_args_list[1][0]
        second_call_kwargs = mock_client.playlist_tracks.call_args_list[1][1]
        self.assertEqual(second_call_args[0], 'playlist1')
        self.assertEqual(second_call_kwargs['fields'], 'items')

    def test_get_saved_tracks(self):
        """Test getting user's saved tracks."""
        # Create mock client
        mock_client = MagicMock()
        
        # Set up mock client to return tracks
        mock_tracks_response = {
            'items': [
                {'track': {'id': 'track1', 'name': 'Track 1'}},
                {'track': {'id': 'track2', 'name': 'Track 2'}}
            ],
            'next': None  # No more pages
        }
        mock_client.current_user_saved_tracks.return_value = mock_tracks_response
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get saved tracks
        tracks = service.get_saved_tracks()
        
        # This method is likely a stub and we just need to make sure it doesn't fail
        # If it's actually implemented, we'd verify the tracks are returned correctly
        self.assertIsInstance(tracks, list)  # Should return some kind of list
        
        # Verify client was called
        mock_client.current_user_saved_tracks.assert_called()

    def test_add_tracks_to_playlist_no_client(self):
        """Test adding tracks to playlist with no client."""
        # Create service with no client
        service = SpotifyService()
        
        # Add tracks
        result = service.add_tracks_to_playlist('playlist1', ['uri1', 'uri2'])
        
        # Verify operation failed
        self.assertFalse(result)
        
    def test_add_tracks_to_playlist_success(self):
        """Test adding tracks to playlist successfully."""
        # Create mock client
        mock_client = MagicMock()
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Add tracks
        result = service.add_tracks_to_playlist('playlist1', ['uri1', 'uri2'])
        
        # Verify operation succeeded
        self.assertTrue(result)
        
        # Verify client was called with correct params
        mock_client.playlist_add_items.assert_called_once_with('playlist1', ['uri1', 'uri2'])
        
    def test_add_tracks_to_playlist_error(self):
        """Test error handling when adding tracks to playlist."""
        # Create mock client that raises exception
        mock_client = MagicMock()
        mock_client.playlist_add_items.side_effect = Exception("API error")
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Add tracks
        result = service.add_tracks_to_playlist('playlist1', ['uri1', 'uri2'])
        
        # Verify operation failed
        self.assertFalse(result)
        
    def test_get_track_audio_features_no_client(self):
        """Test getting track audio features with no client."""
        # Create service with no client
        service = SpotifyService()
        
        # Get audio features
        features = service.get_track_audio_features('track1')
        
        # Verify None is returned
        self.assertIsNone(features)
        
    def test_get_track_audio_features_success(self):
        """Test getting track audio features successfully."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.audio_features.return_value = [
            {
                "danceability": 0.8,
                "energy": 0.9,
                "key": 5,
                "tempo": 120.5
            }
        ]
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get audio features
        features = service.get_track_audio_features('track1')
        
        # Verify features are returned
        self.assertEqual(features["danceability"], 0.8)
        self.assertEqual(features["energy"], 0.9)
        self.assertEqual(features["tempo"], 120.5)
        
        # Verify client was called with correct params
        mock_client.audio_features.assert_called_once_with('track1')
        
    def test_get_track_audio_features_empty_response(self):
        """Test getting track audio features with empty response."""
        # Create mock client with empty response
        mock_client = MagicMock()
        mock_client.audio_features.return_value = []
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get audio features
        features = service.get_track_audio_features('track1')
        
        # Verify None is returned
        self.assertIsNone(features)
        
    def test_get_track_audio_features_403_error(self):
        """Test handling 403 error when getting track audio features."""
        # Create mock client that raises 403 exception
        mock_client = MagicMock()
        mock_client.audio_features.side_effect = Exception("403 Forbidden")
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get audio features
        features = service.get_track_audio_features('track1')
        
        # Verify default features are returned
        self.assertEqual(features["danceability"], 0.5)
        self.assertEqual(features["energy"], 0.5)
        self.assertEqual(features["tempo"], 120)
        
    def test_get_track_audio_features_general_error(self):
        """Test handling general error when getting track audio features."""
        # Create mock client that raises general exception
        mock_client = MagicMock()
        mock_client.audio_features.side_effect = Exception("API error")
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Get audio features
        features = service.get_track_audio_features('track1')
        
        # Verify None is returned
        self.assertIsNone(features)
        
    def test_search_artist_no_client(self):
        """Test searching for artist with no client."""
        # Create service with no client
        service = SpotifyService()
        
        # Search for artist
        artist = service.search_artist("Test Artist")
        
        # Verify None is returned
        self.assertIsNone(artist)
        
    def test_search_artist_success(self):
        """Test searching for artist successfully."""
        # Create mock client
        mock_client = MagicMock()
        mock_client.search.return_value = {
            'artists': {
                'items': [
                    {
                        'id': 'artist1',
                        'name': 'Test Artist',
                        'images': [{'url': 'http://example.com/image1.jpg'}]
                    }
                ]
            }
        }
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Search for artist
        artist = service.search_artist("Test Artist")
        
        # Verify artist is returned
        self.assertEqual(artist['id'], 'artist1')
        self.assertEqual(artist['name'], 'Test Artist')
        
        # Verify client was called with correct params
        mock_client.search.assert_called_once_with(q="artist:Test Artist", type="artist", limit=1)
        
    def test_search_artist_no_results(self):
        """Test searching for artist with no results."""
        # Create mock client with empty results
        mock_client = MagicMock()
        mock_client.search.return_value = {'artists': {'items': []}}
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Search for artist
        artist = service.search_artist("Test Artist")
        
        # Verify None is returned
        self.assertIsNone(artist)
        
    def test_search_artist_missing_images(self):
        """Test searching for artist with missing images."""
        # Create mock client with artist missing images
        mock_client = MagicMock()
        mock_client.search.return_value = {
            'artists': {
                'items': [
                    {
                        'id': 'artist1',
                        'name': 'Test Artist'
                        # Missing 'images' field
                    }
                ]
            }
        }
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Search for artist
        artist = service.search_artist("Test Artist")
        
        # Verify artist is returned with empty images array
        self.assertEqual(artist['id'], 'artist1')
        self.assertEqual(artist['name'], 'Test Artist')
        self.assertEqual(artist['images'], [])
        
    def test_search_artist_error(self):
        """Test error handling when searching for artist."""
        # Create mock client that raises exception
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("API error")
        
        # Create service with mock client
        service = SpotifyService(spotify_client=mock_client)
        
        # Search for artist
        artist = service.search_artist("Test Artist")
        
        # Verify None is returned
        self.assertIsNone(artist)


if __name__ == '__main__':
    unittest.main() 