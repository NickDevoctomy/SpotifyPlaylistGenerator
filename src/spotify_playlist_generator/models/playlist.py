"""
Playlist data model for representing Spotify playlists.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Track:
    """Model representing a Spotify track."""
    id: str
    name: str
    artist: str
    album: str
    uri: str
    
    @classmethod
    def from_spotify_track(cls, track_data: Dict[str, Any]) -> 'Track':
        """Create a Track instance from Spotify API track data."""
        track = track_data.get('track', track_data)
        return cls(
            id=track.get('id', ''),
            name=track.get('name', ''),
            artist=track.get('artists', [{}])[0].get('name', 'Unknown Artist'),
            album=track.get('album', {}).get('name', 'Unknown Album'),
            uri=track.get('uri', '')
        )


@dataclass
class Playlist:
    """Model representing a Spotify playlist."""
    id: str
    name: str
    description: str
    owner: str
    tracks: List[Track]
    image_url: Optional[str] = None
    uri: Optional[str] = None
    
    @classmethod
    def from_spotify_playlist(cls, playlist_data: Dict[str, Any], tracks: List[Dict[str, Any]] = None) -> 'Playlist':
        """Create a Playlist instance from Spotify API playlist data."""
        image_url = None
        if playlist_data.get('images') and len(playlist_data['images']) > 0:
            image_url = playlist_data['images'][0].get('url')
            
        track_objects = []
        if tracks:
            track_objects = [Track.from_spotify_track(track) for track in tracks]
            
        return cls(
            id=playlist_data.get('id', ''),
            name=playlist_data.get('name', ''),
            description=playlist_data.get('description', ''),
            owner=playlist_data.get('owner', {}).get('display_name', 'Unknown'),
            tracks=track_objects,
            image_url=image_url,
            uri=playlist_data.get('uri')
        ) 