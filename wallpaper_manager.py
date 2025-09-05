"""
Wallpaper management operations for TaskPaper.
"""
import os
import glob
import time
from typing import Tuple

from AppKit import NSWorkspace, NSScreen, NSURL

from config import WALL_DIR, WALLPAPER_KEEP_COUNT


def set_wallpaper_all_displays(path: str):
    """Set wallpaper on all displays."""
    ws = NSWorkspace.sharedWorkspace()
    screens = NSScreen.screens()
    for screen in screens:
        url = NSURL.fileURLWithPath_(path)
        # options and error can be None in PyObjC call
        ws.setDesktopImageURL_forScreen_options_error_(url, screen, None, None)


def cleanup_old_wallpapers(current_file: str, keep_count: int = WALLPAPER_KEEP_COUNT):
    """
    Clean up old wallpaper files, keeping only the most recent ones.
    
    Args:
        current_file: Path to the current wallpaper file to always keep
        keep_count: Number of most recent wallpapers to keep
    """
    try:
        # Get all wallpaper files
        pattern = os.path.join(WALL_DIR, "wall-*.png")
        all_files = glob.glob(pattern)
        
        # Sort by modification time (newest first)
        all_files.sort(key=os.path.getmtime, reverse=True)
        
        # Always keep the current file at the top
        if current_file in all_files:
            all_files.remove(current_file)
            all_files.insert(0, current_file)
        
        # Delete files beyond keep_count
        files_to_delete = all_files[keep_count:]
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
            except OSError:
                pass  # Ignore errors if file is in use or doesn't exist
                
    except Exception:
        pass  # Silently ignore cleanup errors to not break main functionality


def get_primary_screen_size() -> Tuple[int, int]:
    """Get the size of the primary screen."""
    screens = NSScreen.screens()
    if not screens:
        return (1920, 1080)  # Default fallback
    
    frame = screens[0].frame()
    return int(frame.size.width), int(frame.size.height)


def generate_wallpaper_filename() -> str:
    """Generate a unique filename for wallpaper."""
    return os.path.join(WALL_DIR, f"wall-{int(time.time())}.png")
