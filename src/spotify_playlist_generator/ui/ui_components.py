"""
UI components for the Spotify Playlist Generator.
"""
from nicegui import ui

class PlaylistComponents:
    """Helper class for rendering playlist UI components."""
    
    @staticmethod
    def render_playlist_card(playlist, on_click=None):
        """
        Render a single playlist card for tiled view.
        
        Args:
            playlist (dict): The playlist data to render.
            on_click (function): Function to call when card is clicked.
        """
        # Get playlist data
        name = playlist.get('name', 'Unnamed Playlist')
        description = playlist.get('description', '')
        total_tracks = playlist.get('tracks', {}).get('total', 0)
        owner = playlist.get('owner', {}).get('display_name', 'Unknown')
        
        # Get the image URL (use the first image if available)
        image_url = None
        if playlist.get('images') and len(playlist['images']) > 0:
            image_url = playlist['images'][0].get('url')
        
        # Create a card for the playlist
        with ui.card().classes('w-full h-full cursor-pointer hover:shadow-lg transition-shadow relative'):
            # Add checkbox at top left
            with ui.element('div').classes('absolute top-2 left-2 z-10'):
                checkbox = ui.checkbox().props('dense').classes('bg-white bg-opacity-70 rounded')
                checkbox.on('click', lambda e: e.stop_propagation(), [])
            
            if image_url:
                ui.image(image_url).classes('w-full aspect-square object-cover')
            else:
                # Placeholder for missing image
                with ui.element('div').classes('w-full aspect-square bg-gray-200 flex items-center justify-center'):
                    ui.icon('music_note', size='xl').classes('text-gray-400')
            
            with ui.card_section():
                ui.label(name).classes('font-bold text-lg truncate w-full')
                if description:
                    ui.label(description).classes('text-xs text-gray-500 h-8 overflow-hidden')
                
                with ui.row().classes('items-center justify-between w-full'):
                    ui.label(f"{total_tracks} tracks").classes('text-xs')
                    ui.label(f"By {owner}").classes('text-xs')
            
            # Add click event if provided
            if on_click:
                ui.element('div').on('click', lambda e, p=playlist: on_click(p)).classes('absolute inset-0 z-0')
    
    @staticmethod
    def render_playlist_list_item(playlist, on_click=None):
        """
        Render a single playlist as a list item for list view.
        
        Args:
            playlist (dict): The playlist data to render.
            on_click (function): Function to call when item is clicked.
        """
        # Get playlist data
        name = playlist.get('name', 'Unnamed Playlist')
        description = playlist.get('description', '')
        total_tracks = playlist.get('tracks', {}).get('total', 0)
        owner = playlist.get('owner', {}).get('display_name', 'Unknown')
        playlist_id = playlist.get('id', '')
        
        # Get the image URL (use the first image if available)
        image_url = None
        if playlist.get('images') and len(playlist['images']) > 0:
            image_url = playlist['images'][0].get('url')
        
        # Create a list item with hover effect
        with ui.card().classes('w-full mb-2 cursor-pointer transition-colors hover:bg-gray-100'):
            with ui.row().classes('items-center p-2 w-full'):
                # Add checkbox at center left with event stopPropagation
                checkbox = ui.checkbox().props('dense').classes('mr-2')
                checkbox.on('click', lambda e: e.stop_propagation(), [])
                
                # Image thumbnail (small square)
                if image_url:
                    ui.image(image_url).classes('w-12 h-12 mr-4 rounded object-cover')
                else:
                    with ui.element('div').classes('w-12 h-12 mr-4 bg-gray-200 flex items-center justify-center rounded'):
                        ui.icon('music_note', size='md').classes('text-gray-400')
                
                # Playlist details
                with ui.column().classes('flex-grow'):
                    with ui.row().classes('w-full items-center'):
                        ui.label(name).classes('font-bold')
                        if playlist.get('public') is False:
                            ui.icon('lock', size='xs').classes('text-gray-400 ml-1')
                    
                    if description:
                        ui.label(description).classes('text-xs text-gray-500 line-clamp-1')
                    
                    with ui.row().classes('text-xs text-gray-500 mt-1 space-x-2'):
                        ui.label(f"{total_tracks} tracks")
                        ui.label('•').classes('text-gray-300 mx-1')
                        ui.label(f"By {owner}")
            
            # Add click event if provided, but don't cover the checkbox
            if on_click:
                content_area = ui.element('div').classes('absolute inset-0 ml-10')
                content_area.on('click', lambda e, p=playlist: on_click(p))

    @staticmethod
    def render_track_item(track_data, on_click=None):
        """
        Render a single track item with Spotify link.
        
        Args:
            track_data (dict): The track data from Spotify API.
            on_click (function): Function to call when track is clicked.
        """
        print(f"[DEBUG UI] Rendering track item: {type(track_data)}")
        
        if not track_data:
            print("[DEBUG UI] Track data is None or empty, skipping render")
            return
        
        try:
            # Extract track information
            track = track_data.get('track', {})
            if not track:
                print("[DEBUG UI] No 'track' field in track_data, skipping render")
                print(f"[DEBUG UI] Track data keys: {track_data.keys()}")
                return
            
            print(f"[DEBUG UI] Track object type: {type(track)}")
            print(f"[DEBUG UI] Track object keys: {track.keys() if isinstance(track, dict) else 'Not a dict'}")
            
            track_id = track.get('id', '')
            track_name = track.get('name', 'Unknown Track')
            print(f"[DEBUG UI] Rendering track: {track_name} (ID: {track_id})")
            
            # Get artist(s)
            artists = track.get('artists', [])
            artist_names = []
            artist_ids = []
            
            print(f"[DEBUG UI] Artists data: {type(artists)}, count: {len(artists) if isinstance(artists, list) else 'Not a list'}")
            
            # Debug the artists array to understand structure
            print(f"[DEBUG UI] Raw artists array: {artists if len(str(artists)) < 500 else 'Too large to print'}")
            
            for artist in artists:
                if isinstance(artist, dict):
                    artist_name = artist.get('name')
                    artist_id = artist.get('id')
                    
                    if artist_id:
                        print(f"[DEBUG UI] Found artist ID: {artist_id!r} for artist: {artist_name}")
                    else:
                        print(f"[DEBUG UI] No ID found for artist: {artist_name}, full artist data: {artist}")
                        
                    if artist_name:
                        artist_names.append(artist_name)
                        if artist_id:
                            artist_ids.append(artist_id)
                else:
                    print(f"[DEBUG UI] Artist is not a dict: {type(artist)}")
            
            artist_display = ', '.join(artist_names) if artist_names else 'Unknown Artist'
            print(f"[DEBUG UI] Artist display: {artist_display}")
            
            # Get album data
            album = track.get('album', {})
            album_name = album.get('name', 'Unknown Album')
            print(f"[DEBUG UI] Album: {album_name}")
            
            # Get album image if available
            album_image = None
            if album.get('images') and len(album['images']) > 0:
                album_images = album.get('images', [])
                print(f"[DEBUG UI] Album images count: {len(album_images)}")
                # Try to get smallest image for thumbnail
                if len(album_images) >= 3:
                    album_image = album_images[2].get('url')
                elif album_images:
                    album_image = album_images[-1].get('url')
            
            # Get track external URL or build from ID
            track_url = None
            if track.get('external_urls', {}).get('spotify'):
                track_url = track['external_urls']['spotify']
            elif track_id:
                track_url = f"https://open.spotify.com/track/{track_id}"
            
            print(f"[DEBUG UI] Track URL: {track_url}")
            
            # Create a more compact track item row
            with ui.card().classes('w-full p-2 hover:bg-gray-50 cursor-pointer relative'):
                with ui.row().classes('items-center w-full gap-3'):
                    # Album thumbnail (smaller)
                    if album_image:
                        ui.image(album_image).classes('w-8 h-8 rounded object-cover')
                    else:
                        with ui.element('div').classes('w-8 h-8 bg-gray-200 flex items-center justify-center rounded'):
                            ui.icon('music_note', size='xs').classes('text-gray-400')
                    
                    # Track details (simplified layout)
                    with ui.column().classes('flex-grow min-w-0'): # min-w-0 helps with text truncation
                        with ui.row().classes('w-full items-center gap-2'):
                            # Track name
                            ui.label(track_name).classes('font-bold truncate')
                            
                            # Play button (smaller and inline)
                            if track_url:
                                with ui.link(target=track_url, new_tab=True).classes('no-underline ml-auto flex-shrink-0 z-10'):
                                    play_button = ui.button(icon='play_arrow').props('flat round dense').classes('text-green-600 text-sm')
                                    play_button.on('click', lambda e: e.stop_propagation(), [])
                        
                        # Artist and album on one line with truncation
                        with ui.label(f"{artist_display} • {album_name}").classes('text-xs text-gray-500 truncate w-full'):
                            pass
                
                # Add click handler for the entire card if provided
                if on_click:
                    ui.element('div').on('click', lambda e, t=track_data: on_click(t)).classes('absolute inset-0 z-0')
            
            print(f"[DEBUG UI] Successfully rendered track: {track_name}")
        except Exception as e:
            print(f"[DEBUG UI] Error rendering track: {str(e)}")
            import traceback
            print(f"[DEBUG UI] Track rendering error traceback: {traceback.format_exc()}")

    @staticmethod
    def render_track_detail(track_data, on_back=None, on_play=None, current_playlist=None, similar_artists=None):
        """
        Render a detailed view of a track.
        
        Args:
            track_data (dict): The track data from Spotify API.
            on_back (function): Function to call when back button is clicked.
            on_play (function): Function to call when play button is clicked.
            current_playlist (dict): The current playlist context, if applicable.
            similar_artists (list): List of similar artists from Spotify API.
        """
        print(f"[DEBUG UI] Starting track detail rendering: {type(track_data)}")
        
        # Basic fallback rendering when no data is available
        if not track_data:
            print("[DEBUG UI] No track data available")
            ui.label("No track data available").classes('text-h5 text-gray-500 text-center py-8')
            if on_back:
                ui.button("Back", icon="arrow_back").on('click', on_back).classes('bg-blue-500 text-white')
            return
        
        try:
            # Extract track data - handle both wrapped and unwrapped formats
            track = track_data.get('track', {}) if isinstance(track_data, dict) and 'track' in track_data else track_data
            
            if not isinstance(track, dict):
                print(f"[DEBUG UI] Track data is not a dictionary: {type(track)}")
                ui.label("Invalid track data format").classes('text-h5 text-gray-500 text-center py-8')
                if on_back:
                    ui.button("Back", icon="arrow_back").on('click', on_back).classes('bg-blue-500 text-white')
                return
                
            # Extract basic track info
            track_id = track.get('id', 'Unknown ID')
            track_name = track.get('name', 'Unknown Track')
            
            # Get artist info
            artists = track.get('artists', [])
            artist_names = [artist.get('name', 'Unknown Artist') for artist in artists if isinstance(artist, dict)]
            artist_display = ', '.join(artist_names) if artist_names else 'Unknown Artist'
            
            # Get album info
            album = track.get('album', {})
            album_name = album.get('name', 'Unknown Album') if isinstance(album, dict) else 'Unknown Album'
            
            # Get album image
            album_image = None
            if isinstance(album, dict) and 'images' in album and album['images']:
                images = album['images']
                if images and isinstance(images, list) and len(images) > 0:
                    first_image = images[0]
                    if isinstance(first_image, dict) and 'url' in first_image:
                        album_image = first_image.get('url')
                        
            # Get track URL
            track_url = None
            if isinstance(track, dict) and 'external_urls' in track:
                ext_urls = track['external_urls']
                if isinstance(ext_urls, dict) and 'spotify' in ext_urls:
                    track_url = ext_urls.get('spotify')
            if not track_url and track_id and track_id != 'Unknown ID':
                track_url = f"https://open.spotify.com/track/{track_id}"
                
            # Render track details - simplified version that prioritizes reliability
            # Back button
            ui.label("Track Details").classes('text-h5 mb-4')
            if on_back:
                ui.button("Back", icon="arrow_back").on('click', on_back).classes('bg-blue-500 text-white mb-4')
                
            # Basic track info in a clear layout
            with ui.row().classes('w-full gap-4'):
                # Album image
                if album_image:
                    ui.image(album_image).classes('w-32 h-32 object-cover')
                else:
                    with ui.element('div').classes('w-32 h-32 bg-gray-200 flex items-center justify-center'):
                        ui.icon('music_note', size='xl').classes('text-gray-400')
                
                # Track info
                with ui.column().classes('flex-grow gap-2'):
                    ui.label(track_name).classes('text-h4 font-bold')
                    ui.label(f"Artist: {artist_display}").classes('text-h6')
                    ui.label(f"Album: {album_name}").classes('text-body1')
                    
                    # Action buttons
                    with ui.row().classes('gap-2 mt-2'):
                        if track_url:
                            with ui.link(target=track_url, new_tab=True).classes('no-underline'):
                                ui.button('Open in Spotify', icon='open_in_new').classes('bg-green-600 text-white')
                        
                        if on_play and track_url:
                            ui.button('Play', icon='play_arrow').on('click', lambda: on_play(track_url)).classes('bg-green-600 text-white')
            
            # Display additional details if available
            ui.separator().classes('my-4')
            
            # Try to show some additional track data if available
            with ui.column().classes('w-full gap-2'):
                ui.label("Additional Information").classes('text-h6')
                
                # Duration
                if 'duration_ms' in track:
                    duration_ms = int(track.get('duration_ms', 0))
                    minutes = duration_ms // 60000
                    seconds = (duration_ms % 60000) // 1000
                    duration_formatted = f"{minutes}:{seconds:02d}"
                    ui.label(f"Duration: {duration_formatted}").classes('text-body2')
                
                # Popularity
                if 'popularity' in track:
                    popularity = int(track.get('popularity', 0))
                    ui.label(f"Popularity: {popularity}/100").classes('text-body2')
                
                # Release date 
                if isinstance(album, dict) and 'release_date' in album:
                    release_date = album.get('release_date', '')
                    if release_date:
                        ui.label(f"Released: {release_date}").classes('text-body2')
            
            # Similar Artists section
            if similar_artists and len(similar_artists) > 0:
                ui.separator().classes('my-4')
                ui.label("Similar Artists").classes('text-h6 mb-2')
                
                with ui.grid(columns=5).classes('w-full gap-2'):
                    for artist in similar_artists:
                        if not isinstance(artist, dict):
                            continue
                            
                        artist_name = artist.get('name', 'Unknown Artist')
                        artist_id = artist.get('id', '')
                        
                        with ui.card().classes('p-2 hover:bg-gray-50'):
                            # Artist image
                            artist_image = None
                            if 'images' in artist and artist['images'] and len(artist['images']) > 0:
                                img = artist['images'][0] if len(artist['images']) > 0 else None
                                if img and isinstance(img, dict) and 'url' in img:
                                    artist_image = img.get('url')
                                    
                            if artist_image:
                                ui.image(artist_image).classes('w-full aspect-square object-cover rounded-full')
                            else:
                                with ui.element('div').classes('w-full aspect-square bg-gray-200 flex items-center justify-center rounded-full'):
                                    ui.icon('person').classes('text-gray-400')
                            
                            # Artist name
                            ui.label(artist_name).classes('text-center text-sm mt-1')
                            
                            # Make the entire card clickable if artist ID exists
                            if artist_id:
                                artist_url = f"https://open.spotify.com/artist/{artist_id}"
                                ui.element('a').props(f'href="{artist_url}" target="_blank"').classes('absolute inset-0')
                
            print(f"[DEBUG UI] Successfully rendered track detail view for '{track_name}'")
            
        except Exception as e:
            print(f"[DEBUG UI] Error in render_track_detail: {str(e)}")
            import traceback
            print(f"[DEBUG UI] Error traceback: {traceback.format_exc()}")
            
            # Fallback rendering
            ui.label("Error displaying track details").classes('text-h5 text-red-500 text-center py-4')
            ui.label(f"Error: {str(e)}").classes('text-body2 text-center')
            if on_back:
                ui.button("Back", icon="arrow_back").on('click', on_back).classes('bg-blue-500 text-white mt-4')

    @staticmethod
    def render_playlist_detail(playlist, tracks=None, on_back=None, on_load_tracks=None, on_track_click=None):
        """
        Render a detailed view of a playlist.
        
        Args:
            playlist (dict): The playlist data to render.
            tracks (list): Optional list of track data to display.
            on_back (function): Function to call when back button is clicked.
            on_load_tracks (function): Function to call to load tracks if not provided.
            on_track_click (function): Function to call when a track is clicked.
        """
        print(f"[DEBUG UI] Rendering playlist detail for: {playlist.get('name', 'Unknown')}")
        print(f"[DEBUG UI] Tracks provided: {tracks is not None}")
        if tracks:
            print(f"[DEBUG UI] Number of tracks provided: {len(tracks)}")
        
        # Get playlist data
        name = playlist.get('name', 'Unnamed Playlist')
        description = playlist.get('description', '')
        owner = playlist.get('owner', {}).get('display_name', 'Unknown')
        total_tracks = playlist.get('tracks', {}).get('total', 0)
        playlist_id = playlist.get('id', '')
        
        print(f"[DEBUG UI] Playlist info - Name: {name}, Owner: {owner}, Total tracks: {total_tracks}")
        
        # Get the image URL (use the first image if available)
        image_url = None
        if playlist.get('images') and len(playlist['images']) > 0:
            image_url = playlist['images'][0].get('url')
        
        # Playlist URL for opening in Spotify
        playlist_url = f"https://open.spotify.com/playlist/{playlist_id}" if playlist_id else None
        
        with ui.card().classes('w-full'):
            # Back button
            with ui.row().classes('w-full mb-4 items-center justify-between'):
                ui.button('Back', icon='arrow_back').on('click', on_back).classes('bg-blue-500 text-white')
                
                # Open in Spotify button
                if playlist_url:
                    with ui.link(target=playlist_url, new_tab=True).classes('no-underline'):
                        ui.button('Open in Spotify', icon='open_in_new').classes('bg-green-600 text-white')
            
            # Playlist header with image and basic info
            with ui.row().classes('w-full items-start gap-6 mb-8'):
                # Playlist image
                if image_url:
                    ui.image(image_url).classes('w-64 h-64 object-cover rounded-lg shadow-md')
                else:
                    with ui.element('div').classes('w-64 h-64 bg-gray-200 flex items-center justify-center rounded-lg shadow-md'):
                        ui.icon('music_note', size='xxl').classes('text-gray-400')
                
                # Playlist information
                with ui.column().classes('flex-grow py-4'):
                    ui.label(name).classes('text-h4 font-bold')
                    if description:
                        ui.label(description).classes('text-subtitle1 text-gray-600 mt-2')
                    
                    with ui.row().classes('mt-4 text-gray-600'):
                        ui.label(f"Created by: {owner}").classes('text-subtitle2')
                    
                    with ui.row().classes('mt-2 text-gray-600'):
                        ui.label(f"{total_tracks} tracks").classes('text-subtitle2')
            
            # Tracks section
            ui.separator()
            with ui.column().classes('w-full mt-4'):
                with ui.row().classes('w-full items-center justify-between mb-4'):
                    ui.label('Tracks').classes('text-h6')
                    
                    # Only show load button if tracks not loaded and callback provided
                    if not tracks and on_load_tracks:
                        print("[DEBUG UI] Rendering Load Tracks button")
                        ui.button('Load Tracks', icon='refresh').on('click', 
                                 lambda: on_load_tracks(playlist_id)).classes('text-blue-500')
                
                # Display loading indicator if no tracks yet
                if not tracks:
                    print("[DEBUG UI] No tracks to display")
                    with ui.row().classes('w-full justify-center my-8'):
                        ui.label('Tracks will be displayed when loaded').classes('text-gray-500')
                else:
                    print(f"[DEBUG UI] Attempting to render {len(tracks)} tracks")
                    
                    # Display tracks in a standard column, without scroll area
                    with ui.column().classes('w-full space-y-2'):
                        if not tracks:
                            ui.label('No tracks available').classes('text-gray-500')
                        else:
                            for i, track_data in enumerate(tracks):
                                print(f"[DEBUG UI] Rendering track #{i+1}")
                                # Pass the on_track_click callback to each track
                                PlaylistComponents.render_track_item(track_data, on_click=on_track_click)
                    
                    print("[DEBUG UI] Finished rendering tracks")


class CustomStyles:
    """Helper class for custom UI styles."""
    
    @staticmethod
    def add_left_aligned_tabs_style():
        """Add CSS style for left-aligned tabs."""
        ui.add_head_html('''
        <style>
        .q-tabs--horizontal .q-tabs__content {
            justify-content: flex-start;
        }
        </style>
        ''')
    
    @staticmethod
    def add_hidden_tabs_style():
        """Add CSS style to hide tab headers but keep tab panels functional."""
        ui.add_head_html('''
        <style>
        .hidden-tabs .q-tabs__content {
            display: none !important;
        }
        .hidden-tabs {
            min-height: 0 !important;
        }
        </style>
        ''') 