"""
Main entry point for TaskPaper app.
"""
import threading
import datetime as dt

import rumps

from config import APP_NAME, REFRESH_SECONDS, TZ, has_openai_api_key
from auth import load_credentials, connect_google
from calendar_service import get_today_events
from triage import triage_events
from renderer import render_wallpaper
from wallpaper_manager import (
    set_wallpaper_all_displays, 
    cleanup_old_wallpapers, 
    get_primary_screen_size, 
    generate_wallpaper_filename
)
from config_window import ConfigWindow
from voice_window import show_voice_window
from settings import show_initial_openai_setup
from voice.storage import VoiceTaskStorage


class TaskPaperApp(rumps.App):
    """Main TaskPaper menubar application."""
    
    def __init__(self):
        # Load credentials and set up state
        self.creds = load_credentials()
        self.paused = False
        self.lock = threading.Lock()
        self.config_window = None
        self.initial_config_shown = False
        
        # Initialize voice task storage
        self.voice_storage = VoiceTaskStorage()

        # Build menu
        self.status_item = rumps.MenuItem("● Running" if self.creds else "○ Disconnected")
        menu = [
            self.status_item,
            rumps.MenuItem("Pause", callback=self.toggle),
            None,
            rumps.MenuItem("Add Task", callback=self.add_task),
            rumps.MenuItem("Refresh Now", callback=self.refresh),
            None,
            rumps.MenuItem("Connect Google…", callback=self.connect),
            None,
            rumps.MenuItem("Settings…", callback=self.show_settings),
        ]

        super().__init__(APP_NAME, icon="transparent_icon.png", menu=menu)
        
        # Set the title with emoji icon
        self.title = "📝"

        # Start timer
        self.timer = rumps.Timer(self.tick, REFRESH_SECONDS)
        self.timer.start()

        # Initial setup prompts
        if not self.creds:
            rumps.notification(APP_NAME, "", "Please connect Google Calendar (menu → Connect Google…).")
        
        # Check for OpenAI API key on startup (only once)
        if not has_openai_api_key() and not self.initial_config_shown:
            # Schedule OpenAI config to show after a brief delay to let the app fully initialize
            timer = rumps.Timer(self._show_initial_openai_config, 2)
            timer.start()

    def connect(self, _):
        """Connect to Google services."""
        try:
            self.creds = connect_google()
            self.status_item.title = "● Running"
            rumps.notification(APP_NAME, "", "Google connected.")
            # Immediately run once
            self.tick(None, force_notification=True)
        except FileNotFoundError as e:
            rumps.alert(str(e))
        except Exception as e:
            rumps.alert(f"Failed to connect: {e}")

    def toggle(self, item):
        """Toggle pause/resume."""
        self.paused = not self.paused
        item.title = "Resume" if self.paused else "Pause"
        self.status_item.title = "◌ Paused" if self.paused else "● Running"

    def refresh(self, _):
        """Force immediate refresh."""
        self.tick(None, force_notification=True)

    def add_task(self, _):
        """Open voice recording window for adding tasks."""
        show_voice_window()

    def show_settings(self, _):
        """Open settings window."""
        if self.config_window is None or not self.config_window.is_open():
            self.config_window = ConfigWindow()
        self.config_window.show()
    
    def _show_initial_openai_config(self, _):
        """Show OpenAI configuration on first startup."""
        try:
            self.initial_config_shown = True
            show_initial_openai_setup()
            
        except Exception as e:
            print(f"Error showing initial OpenAI config: {e}")

    def tick(self, _, force_notification: bool = False):
        """Main refresh loop."""
        if self.paused:
            return
        if not self.lock.acquire(blocking=False):
            return  # Skip if previous run still working

        try:
            # Get calendar data (if connected)
            today = dt.datetime.now(TZ).strftime("%Y-%m-%d")
            events = []
            calendar_tasks = []
            
            if self.creds:
                events = get_today_events(self.creds)
                calendar_tasks = triage_events(today, events)

            # Get voice tasks
            voice_tasks = self._get_voice_tasks()
            
            # Combine tasks for wallpaper
            all_tasks = self._combine_tasks(calendar_tasks, voice_tasks)

            # Only regenerate wallpaper if we have tasks or are connected to calendar
            if all_tasks or self.creds:
                screen_size = get_primary_screen_size()
                wallpaper_path = generate_wallpaper_filename()
                
                render_wallpaper(all_tasks, events, screen_size, wallpaper_path)
                set_wallpaper_all_displays(wallpaper_path)
                cleanup_old_wallpapers(wallpaper_path)

            if force_notification:
                rumps.notification(APP_NAME, "", "Wallpaper updated.")
            
            # Update status
            if self.creds:
                self.status_item.title = "● Running"
            else:
                self.status_item.title = "○ Disconnected"
            
        except Exception as e:
            print("Error:", e)
            self.status_item.title = "⚠︎ Error"
        finally:
            self.lock.release()
    
    def _get_voice_tasks(self):
        """Get today's voice tasks and convert them to UrgentTask format."""
        try:
            from models import UrgentTask
            
            voice_tasks = self.voice_storage.get_today_tasks()
            urgent_tasks = []
            
            for voice_task in voice_tasks:
                # Convert VoiceTaskExtended to UrgentTask format
                urgent_task = UrgentTask(
                    title=voice_task.title,
                    source="voice",
                    time=voice_task.start_time,  # Use start_time for display
                    priority=voice_task.priority,
                    link=None  # Voice tasks don't have links
                )
                urgent_tasks.append(urgent_task)
            
            return urgent_tasks
            
        except Exception as e:
            print(f"Error loading voice tasks: {e}")
            return []
    
    def _combine_tasks(self, calendar_tasks, voice_tasks):
        """Combine calendar and voice tasks, prioritizing by urgency and time."""
        all_tasks = []
        
        # Add calendar tasks first (maintain existing priority)
        all_tasks.extend(calendar_tasks)
        
        # Add voice tasks
        all_tasks.extend(voice_tasks)
        
        # Sort by priority (1=highest priority) and then by time
        def task_sort_key(task):
            # Priority comes first (1 is highest priority, so lower numbers first)
            priority = task.priority
            
            # Time comes second - tasks with time come before tasks without time
            time_priority = 0 if task.time else 1
            
            # Convert time to minutes for sorting (if available)
            time_minutes = 0
            if task.time:
                try:
                    hours, minutes = map(int, task.time.split(':'))
                    time_minutes = hours * 60 + minutes
                except:
                    time_minutes = 0
            
            return (priority, time_priority, time_minutes)
        
        all_tasks.sort(key=task_sort_key)
        
        # Limit to 6 tasks total (same as original limit)
        return all_tasks[:6]


def main():
    """Entry point for the application."""
    # Quick dependency tips for user:
    # pip install --upgrade rumps google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib pillow pyobjc openai
    TaskPaperApp().run()


if __name__ == "__main__":
    main()
