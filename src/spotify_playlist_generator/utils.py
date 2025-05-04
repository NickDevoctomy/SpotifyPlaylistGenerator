"""
Utility functions for the Spotify Playlist Generator.
"""
import re
import os
from typing import Dict, List, Optional, Any


def format_playlist_name(name: str) -> str:
    """
    Format a playlist name by removing special characters and limiting length.
    
    Args:
        name: The playlist name to format.
        
    Returns:
        The formatted playlist name.
    """
    # Remove special characters
    formatted = re.sub(r'[^\w\s]', '', name)
    
    # Limit length to 50 characters
    if len(formatted) > 50:
        formatted = formatted[:47] + "..."
    
    return formatted.strip()


def validate_spotify_uri(uri: str) -> bool:
    """
    Validate a Spotify URI format.
    
    Args:
        uri: The URI to validate.
        
    Returns:
        True if the URI is valid, False otherwise.
    """
    pattern = r'^spotify:(artist|album|track|playlist):([a-zA-Z0-9]{22})$'
    return bool(re.match(pattern, uri))


def truncate_description(description: str, max_length: int = 100) -> str:
    """
    Truncate a description to a specified length, adding ellipsis if needed.
    
    Args:
        description: The description to truncate.
        max_length: The maximum length of the truncated description.
        
    Returns:
        The truncated description.
    """
    if not description:
        return ""
    
    if len(description) <= max_length:
        return description
    
    return description[:max_length - 3] + '...'


def filter_playlists_by_owner(playlists: List[Dict[str, Any]], owner_id: str) -> List[Dict[str, Any]]:
    """
    Filter playlists by owner ID.
    
    Args:
        playlists: A list of playlist dictionaries.
        owner_id: The Spotify user ID of the owner to filter by.
        
    Returns:
        A list of playlists owned by the specified user.
    """
    return [playlist for playlist in playlists if playlist.get('owner', {}).get('id') == owner_id]


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get an environment variable, with an optional default value.
    
    Args:
        name: The name of the environment variable.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The value of the environment variable, or the default value if not set.
    """
    return os.environ.get(name, default) 