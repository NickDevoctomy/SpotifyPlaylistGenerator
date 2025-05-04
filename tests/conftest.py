"""
Pytest configuration file.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create a mock for nicegui modules and components
# This needs to be done before any imports
class MockApp:
    def __init__(self):
        self.get = MagicMock()
        self.post = MagicMock()
        self.put = MagicMock()
        self.delete = MagicMock()

# Create a comprehensive nicegui mock
class MockUI:
    def __init__(self):
        self.page = MagicMock()
        self.card = MagicMock()
        self.card_section = MagicMock()
        self.label = MagicMock()
        self.button = MagicMock()
        self.image = MagicMock()
        self.row = MagicMock()
        self.column = MagicMock()
        self.icon = MagicMock()
        self.element = MagicMock()
        self.header = MagicMock()
        self.notify = MagicMock()
        self.grid = MagicMock()
        self.tabs = MagicMock()
        self.tab = MagicMock()
        self.tab_panels = MagicMock()
        self.tab_panel = MagicMock()
        self.select = MagicMock()
        self.add_head_html = MagicMock()
        self.navigate = MagicMock()
        self.navigate.reload = MagicMock()

# Setup mocks for necessary modules
mock_ui = MockUI()
mock_app = MockApp()

# Mock nicegui modules
sys.modules["nicegui"] = MagicMock()
sys.modules["nicegui.ui"] = mock_ui
sys.modules["nicegui.app"] = mock_app
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["fastapi.responses"].HTMLResponse = MagicMock()
sys.modules["fastapi.responses"].PlainTextResponse = MagicMock()

@pytest.fixture
def sample_playlist():
    """
    Provide a sample playlist dictionary for tests.
    """
    return {
        'name': 'Test Playlist',
        'description': 'Test Description',
        'tracks': {'total': 10},
        'owner': {'display_name': 'Test User'},
        'images': [{'url': 'http://example.com/image.jpg'}],
        'public': False,
        'id': 'test123'
    }

@pytest.fixture
def sample_playlist_no_image():
    """
    Provide a sample playlist without images for tests.
    """
    return {
        'name': 'Test Playlist No Image',
        'description': 'Test Description',
        'tracks': {'total': 5},
        'owner': {'display_name': 'Test User'},
        'images': [],
        'public': True,
        'id': 'test456'
    } 