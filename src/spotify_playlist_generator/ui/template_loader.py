"""
Template loader for the Spotify Playlist Generator UI.
"""
import os
from pathlib import Path

class TemplateLoader:
    """Handles loading HTML templates for the application."""
    
    def __init__(self):
        """Initialize the template loader."""
        # Get the absolute path to the templates directory
        self.template_dir = Path(os.path.dirname(os.path.abspath(__file__))) / 'templates'
    
    def load_template(self, template_name):
        """
        Load a template from the templates directory.
        
        Args:
            template_name (str): The name of the template file to load.
            
        Returns:
            str: The contents of the template file.
            
        Raises:
            FileNotFoundError: If the template file cannot be found.
        """
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_name}")
        
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read() 