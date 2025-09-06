"""
Configuration window for TaskPaper - simplified launcher for settings.
"""
from taskpaper.ui.settings import show_settings


class ConfigWindow:
    """Configuration window wrapper for TaskPaper settings."""
    
    def __init__(self):
        self._is_open = False
        
    def is_open(self) -> bool:
        """Check if configuration window is open."""
        return self._is_open
    
    def show(self, force_openai_config: bool = False):
        """Show the configuration window."""
        if self._is_open:
            return
            
        try:
            self._is_open = True
            show_settings()
                
        except Exception as e:
            print(f"Error opening settings: {e}")
        finally:
            self._is_open = False
    
    def close(self):
        """Close the configuration window."""
        self._is_open = False
