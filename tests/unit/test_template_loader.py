"""
Unit tests for the TemplateLoader class.
"""
import os
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

from src.spotify_playlist_generator.ui.template_loader import TemplateLoader


class TestTemplateLoader(unittest.TestCase):
    """Test cases for the TemplateLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.template_loader = TemplateLoader()

    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="<html>Test Template</html>")
    def test_load_template_success(self, mock_file, mock_exists):
        """Test that templates are loaded correctly when file exists."""
        # Configure the mock
        mock_exists.return_value = True
        
        # Call the method under test
        result = self.template_loader.load_template('test.html')
        
        # Assert the result
        self.assertEqual(result, "<html>Test Template</html>")
        
        # Verify that the file was opened correctly
        mock_file.assert_called_once()
        
        # Get the path that was used to open the file
        args, _ = mock_file.call_args
        # The first arg is the file path
        file_path = args[0]
        
        # Verify the file path contains the template name
        self.assertIn('test.html', str(file_path))

    @patch('pathlib.Path.exists')
    def test_load_template_file_not_found(self, mock_exists):
        """Test that FileNotFoundError is raised when template doesn't exist."""
        # Configure the mock
        mock_exists.return_value = False
        
        # Verify that attempting to load a non-existent template raises an error
        with self.assertRaises(FileNotFoundError):
            self.template_loader.load_template('non_existent.html')

    @patch('os.path.dirname')
    @patch('os.path.abspath')
    def test_template_dir_initialization(self, mock_abspath, mock_dirname):
        """Test that the template directory is initialized correctly."""
        # Configure the mocks
        mock_abspath.return_value = "/fake/path/to/ui"
        mock_dirname.return_value = "/fake/path/to"
        
        # Create a new instance to trigger initialization
        loader = TemplateLoader()
        
        # Verify that the template directory is set correctly
        expected_path = Path("/fake/path/to") / 'templates'
        self.assertEqual(loader.template_dir, expected_path)


if __name__ == '__main__':
    unittest.main() 