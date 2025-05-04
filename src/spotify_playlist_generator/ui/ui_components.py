"""
UI components for the Spotify Playlist Generator.
"""
from nicegui import ui

class PlaylistComponents:
    """Helper class for rendering playlist UI components."""
    
    @staticmethod
    def render_playlist_card(playlist):
        """
        Render a single playlist card for tiled view.
        
        Args:
            playlist (dict): The playlist data to render.
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
        with ui.card().classes('w-full h-full'):
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
    
    @staticmethod
    def render_playlist_list_item(playlist):
        """
        Render a single playlist as a list item for list view.
        
        Args:
            playlist (dict): The playlist data to render.
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