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
        with ui.card().classes('w-full h-full cursor-pointer hover:shadow-lg transition-shadow'):
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
                ui.element('div').on('click', lambda e, p=playlist: on_click(p)).classes('absolute inset-0')
    
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
            
            # Add click event if provided
            if on_click:
                ui.element('div').on('click', lambda e, p=playlist: on_click(p)).classes('absolute inset-0')

    @staticmethod
    def render_playlist_detail(playlist, on_back=None):
        """
        Render a detailed view of a playlist.
        
        Args:
            playlist (dict): The playlist data to render.
            on_back (function): Function to call when back button is clicked.
        """
        # Get playlist data
        name = playlist.get('name', 'Unnamed Playlist')
        description = playlist.get('description', '')
        owner = playlist.get('owner', {}).get('display_name', 'Unknown')
        total_tracks = playlist.get('tracks', {}).get('total', 0)
        
        # Get the image URL (use the first image if available)
        image_url = None
        if playlist.get('images') and len(playlist['images']) > 0:
            image_url = playlist['images'][0].get('url')
        
        with ui.card().classes('w-full'):
            # Back button
            with ui.row().classes('w-full mb-4'):
                ui.button('Back', icon='arrow_back').on('click', on_back).classes('bg-blue-500 text-white')
            
            # Playlist header with image and basic info
            with ui.row().classes('w-full items-start gap-6'):
                # Playlist image
                if image_url:
                    ui.image(image_url).classes('w-64 h-64 object-cover rounded-lg shadow-md')
                else:
                    with ui.element('div').classes('w-64 h-64 bg-gray-200 flex items-center justify-center rounded-lg shadow-md'):
                        ui.icon('music_note', size='xxl').classes('text-gray-400')
                
                # Playlist information
                with ui.column().classes('flex-grow'):
                    ui.label(name).classes('text-h4 font-bold')
                    if description:
                        ui.label(description).classes('text-subtitle1 text-gray-600 mt-2')
                    
                    with ui.row().classes('mt-4 text-gray-600'):
                        ui.label(f"Created by: {owner}").classes('text-subtitle2')
                    
                    with ui.row().classes('mt-2 text-gray-600'):
                        ui.label(f"{total_tracks} tracks").classes('text-subtitle2')


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