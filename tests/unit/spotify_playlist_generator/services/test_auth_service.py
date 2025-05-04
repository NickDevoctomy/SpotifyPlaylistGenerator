"""
Unit tests for the auth_service module.
"""
import unittest
from unittest.mock import patch, MagicMock

from src.spotify_playlist_generator.services.auth_service import SpotifyAuthService


class TestSpotifyAuthService(unittest.TestCase):
    """Test cases for the SpotifyAuthService class."""

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_init(self, mock_spotify_oauth, mock_os):
        """Test service initialization with environment variables."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        service = SpotifyAuthService()
        
        # Verify credentials were set from environment
        self.assertEqual(service.client_id, 'test_client_id')
        self.assertEqual(service.client_secret, 'test_client_secret')
        self.assertEqual(service.redirect_uri, 'http://test.com/callback')
        
        # Verify OAuth was initialized
        mock_spotify_oauth.assert_called_once()
        self.assertIsNotNone(service.sp_oauth)

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_init_missing_credentials(self, mock_spotify_oauth, mock_os):
        """Test service initialization with missing credentials."""
        # Mock missing environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        service = SpotifyAuthService()
        
        # Verify credentials are None or default
        self.assertIsNone(service.client_id)
        self.assertIsNone(service.client_secret)
        self.assertEqual(service.redirect_uri, 'http://test.com/callback')
        
        # Verify OAuth was not initialized
        mock_spotify_oauth.assert_not_called()
        self.assertIsNone(service.sp_oauth)

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_get_auth_url(self, mock_spotify_oauth, mock_os):
        """Test getting authentication URL."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up the mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.get_authorize_url.return_value = 'https://accounts.spotify.com/authorize?test_params'
        
        service = SpotifyAuthService()
        auth_url = service.get_auth_url()
        
        # Verify the correct URL was returned
        self.assertEqual(auth_url, 'https://accounts.spotify.com/authorize?test_params')
        mock_oauth_instance.get_authorize_url.assert_called_once()

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_get_auth_url_no_oauth_initializes(self, mock_spotify_oauth, mock_os):
        """Test getting auth URL with uninitiated OAuth that successfully initializes."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up the mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.get_authorize_url.return_value = 'https://accounts.spotify.com/authorize?test_params'
        
        # Create service and manually unset the OAuth instance
        service = SpotifyAuthService()
        service.sp_oauth = None
        
        # Call get_auth_url, which should initialize OAuth
        auth_url = service.get_auth_url()
        
        # Verify OAuth was re-initialized and URL returned
        self.assertEqual(auth_url, 'https://accounts.spotify.com/authorize?test_params')
        # Should be called twice (once in init, once in get_auth_url)
        self.assertEqual(mock_spotify_oauth.call_count, 2)

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_get_auth_url_fails(self, mock_spotify_oauth, mock_os):
        """Test getting auth URL when OAuth initialization fails."""
        # Mock environment variables with missing credentials
        mock_os.getenv.side_effect = lambda key, default=None: {
            # Missing client_id and client_secret
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Create service with no OAuth
        service = SpotifyAuthService()
        service.sp_oauth = None
        
        # Mock _initialize_oauth to ensure sp_oauth remains None
        original_initialize = service._initialize_oauth
        service._initialize_oauth = lambda: None
        
        # Attempt to get auth URL
        with self.assertRaises(ValueError):
            service.get_auth_url()
        
        # Restore original method
        service._initialize_oauth = original_initialize

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    @patch('src.spotify_playlist_generator.services.auth_service.spotipy')
    def test_authenticate_success(self, mock_spotipy, mock_spotify_oauth, mock_os):
        """Test successful authentication with access code."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up mock OAuth and token
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.get_access_token.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_at': 1234567890
        }
        
        # Set up mock Spotify client
        mock_spotify_instance = mock_spotipy.Spotify.return_value
        mock_spotify_instance.current_user.return_value = {
            'display_name': 'Test User',
            'id': 'test_user_id'
        }
        
        # Create service and authenticate
        service = SpotifyAuthService()
        result = service.authenticate('test_auth_code')
        
        # Verify authentication was successful
        self.assertTrue(result)
        mock_oauth_instance.get_access_token.assert_called_once_with(
            'test_auth_code', as_dict=True, check_cache=False)
        mock_spotipy.Spotify.assert_called_once_with(auth='test_access_token')
        mock_spotify_instance.current_user.assert_called_once()
        
        # Verify token and client were stored
        self.assertEqual(service.token_info['access_token'], 'test_access_token')
        self.assertEqual(service.token_info['refresh_token'], 'test_refresh_token')
        self.assertIsNotNone(service.client)
        self.assertEqual(service.user_info['display_name'], 'Test User')

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    @patch('src.spotify_playlist_generator.services.auth_service.spotipy')
    def test_authenticate_no_oauth(self, mock_spotipy, mock_spotify_oauth, mock_os):
        """Test authentication when OAuth is not initialized."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up mock OAuth and token
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.get_access_token.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_at': 1234567890
        }
        
        # Set up mock Spotify client
        mock_spotify_instance = mock_spotipy.Spotify.return_value
        mock_spotify_instance.current_user.return_value = {
            'display_name': 'Test User',
            'id': 'test_user_id'
        }
        
        # Create service with no OAuth
        service = SpotifyAuthService()
        service.sp_oauth = None
        
        # Authenticate
        result = service.authenticate('test_auth_code')
        
        # Verify OAuth was initialized and authentication successful
        self.assertTrue(result)
        self.assertIsNotNone(service.sp_oauth)
        mock_spotify_oauth.assert_called_with(
            client_id='test_client_id',
            client_secret='test_client_secret',
            redirect_uri='http://test.com/callback',
            scope="user-library-read playlist-read-private playlist-modify-private playlist-modify-public",
            open_browser=False,
            cache_handler=None
        )

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    @patch('src.spotify_playlist_generator.services.auth_service.spotipy')
    def test_authenticate_failure(self, mock_spotipy, mock_spotify_oauth, mock_os):
        """Test authentication failure."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up mock OAuth to raise exception
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.get_access_token.side_effect = Exception("Invalid code")
        
        # Create service and attempt authentication
        service = SpotifyAuthService()
        result = service.authenticate('invalid_code')
        
        # Verify authentication failed
        self.assertFalse(result)
        self.assertIsNone(service.token_info)
        self.assertIsNone(service.client)
        self.assertIsNone(service.user_info)

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_check_token_no_token(self, mock_spotify_oauth, mock_os):
        """Test check_token with no token."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Create service
        service = SpotifyAuthService()
        service.token_info = None
        
        # Check token
        result = service.check_token()
        
        # Verify check fails with no token
        self.assertFalse(result)

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    @patch('src.spotify_playlist_generator.services.auth_service.spotipy')
    def test_check_token_expired(self, mock_spotipy, mock_spotify_oauth, mock_os):
        """Test check_token with expired token that needs refresh."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Old token data
        old_token = {
            'access_token': 'old_access_token',
            'refresh_token': 'old_refresh_token',
            'expires_at': 1234567890
        }
        
        # New token data after refresh
        new_token = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_at': 1234567890
        }
        
        # Set up mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.is_token_expired.return_value = True
        mock_oauth_instance.refresh_access_token.return_value = new_token
        
        # Set up mock Spotify client
        mock_spotify_instance = mock_spotipy.Spotify.return_value
        mock_spotify_instance.current_user.return_value = {
            'display_name': 'Test User',
            'id': 'test_user_id'
        }
        
        # Create service with expired token
        service = SpotifyAuthService()
        service.token_info = old_token.copy()
        
        # Check token
        result = service.check_token()
        
        # Verify token was refreshed
        self.assertTrue(result)
        mock_oauth_instance.is_token_expired.assert_called_once_with(old_token)
        mock_oauth_instance.refresh_access_token.assert_called_once_with('old_refresh_token')
        mock_spotipy.Spotify.assert_called_once_with(auth='new_access_token')
        
        # Verify token was updated
        self.assertEqual(service.token_info['access_token'], 'new_access_token')
        self.assertEqual(service.token_info['refresh_token'], 'new_refresh_token')

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_check_token_expired_no_refresh_token(self, mock_spotify_oauth, mock_os):
        """Test check_token with expired token but no refresh token."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up token with no refresh token
        token_without_refresh = {
            'access_token': 'old_access_token',
            'expires_at': 1234567890
            # No refresh_token key
        }
        
        # Set up mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.is_token_expired.return_value = True
        
        # Create service with token that has no refresh token
        service = SpotifyAuthService()
        service.token_info = token_without_refresh.copy()
        
        # Check token
        result = service.check_token()
        
        # Verify check fails without refresh token
        self.assertFalse(result)
        mock_oauth_instance.is_token_expired.assert_called_once_with(token_without_refresh)
        mock_oauth_instance.refresh_access_token.assert_not_called()

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_check_token_refresh_error(self, mock_spotify_oauth, mock_os):
        """Test check_token when refresh fails with exception."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up token with refresh token
        token_with_refresh = {
            'access_token': 'old_access_token',
            'refresh_token': 'old_refresh_token',
            'expires_at': 1234567890
        }
        
        # Set up mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.is_token_expired.return_value = True
        mock_oauth_instance.refresh_access_token.side_effect = Exception("Refresh failed")
        
        # Create service with token
        service = SpotifyAuthService()
        service.token_info = token_with_refresh.copy()
        
        # Check token
        result = service.check_token()
        
        # Verify check fails when refresh raises exception
        self.assertFalse(result)
        mock_oauth_instance.is_token_expired.assert_called_once_with(token_with_refresh)
        mock_oauth_instance.refresh_access_token.assert_called_once_with('old_refresh_token')

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_check_token_valid(self, mock_spotify_oauth, mock_os):
        """Test check_token with valid token."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.is_token_expired.return_value = False
        
        # Create service with valid token and mock client
        service = SpotifyAuthService()
        service.token_info = {
            'access_token': 'valid_access_token',
            'refresh_token': 'valid_refresh_token',
            'expires_at': 9999999999
        }
        service.client = MagicMock()
        service.client.current_user.return_value = {
            'display_name': 'Test User',
            'id': 'test_user_id'
        }
        
        # Check token
        result = service.check_token()
        
        # Verify token is valid
        self.assertTrue(result)
        mock_oauth_instance.is_token_expired.assert_called_once_with(service.token_info)
        service.client.current_user.assert_called_once()

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_check_token_client_error(self, mock_spotify_oauth, mock_os):
        """Test check_token when client verification fails."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up mock OAuth
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.is_token_expired.return_value = False
        
        # Create service with valid token but problematic client
        service = SpotifyAuthService()
        service.token_info = {
            'access_token': 'valid_access_token',
            'refresh_token': 'valid_refresh_token',
            'expires_at': 9999999999
        }
        
        # Create mock client that raises exception
        service.client = MagicMock()
        service.client.current_user.side_effect = Exception("API Error")
        
        # Check token
        result = service.check_token()
        
        # Verify check fails when client verification raises exception
        self.assertFalse(result)
        mock_oauth_instance.is_token_expired.assert_called_once_with(service.token_info)
        service.client.current_user.assert_called_once()

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_check_token_general_exception(self, mock_spotify_oauth, mock_os):
        """Test check_token handling a general exception."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Set up mock OAuth to raise exception
        mock_oauth_instance = mock_spotify_oauth.return_value
        mock_oauth_instance.is_token_expired.side_effect = Exception("Unexpected error")
        
        # Create service with token
        service = SpotifyAuthService()
        service.token_info = {
            'access_token': 'valid_access_token',
            'refresh_token': 'valid_refresh_token',
            'expires_at': 9999999999
        }
        
        # Check token
        result = service.check_token()
        
        # Verify check fails when an unexpected exception occurs
        self.assertFalse(result)

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_get_user_info(self, mock_spotify_oauth, mock_os):
        """Test getting user info."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Create service
        service = SpotifyAuthService()
        service.user_info = {'display_name': 'Test User', 'id': 'test_user_id'}
        
        # Get user info
        user_info = service.get_user_info()
        
        # Verify user info
        self.assertEqual(user_info['display_name'], 'Test User')
        self.assertEqual(user_info['id'], 'test_user_id')

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_get_spotify_client(self, mock_spotify_oauth, mock_os):
        """Test getting Spotify client."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Create service
        service = SpotifyAuthService()
        service.client = MagicMock()
        
        # Mock check_token to return True
        service.check_token = MagicMock(return_value=True)
        
        # Get client
        client = service.get_spotify_client()
        
        # Verify client is returned
        self.assertEqual(client, service.client)
        service.check_token.assert_called_once()
        
        # Mock check_token to return False
        service.check_token = MagicMock(return_value=False)
        
        # Get client with invalid token
        client = service.get_spotify_client()
        
        # Verify None is returned
        self.assertIsNone(client)
        service.check_token.assert_called_once()

    @patch('src.spotify_playlist_generator.services.auth_service.os')
    @patch('src.spotify_playlist_generator.services.auth_service.SpotifyOAuth')
    def test_logout(self, mock_spotify_oauth, mock_os):
        """Test logout functionality."""
        # Mock environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            'SPOTIFY_CLIENT_ID': 'test_client_id',
            'SPOTIFY_CLIENT_SECRET': 'test_client_secret',
            'SPOTIFY_REDIRECT_URI': 'http://test.com/callback'
        }.get(key, default)
        
        # Create service
        service = SpotifyAuthService()
        service.token_info = {'access_token': 'test_token'}
        service.client = MagicMock()
        service.user_info = {'display_name': 'Test User'}
        
        # Logout
        service.logout()
        
        # Verify state was cleared
        self.assertIsNone(service.token_info)
        self.assertIsNone(service.client)
        self.assertIsNone(service.user_info)


if __name__ == '__main__':
    unittest.main() 