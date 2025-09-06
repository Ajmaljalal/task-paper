"""
Extended models for voice task processing.
"""
import datetime as dt
from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceTaskExtended:
    """Extended voice task with additional fields extracted from voice."""
    title: str
    description: Optional[str] = None
    priority: int = 3  # 1-5, default medium
    start_time: Optional[str] = None  # "H:MM AM/PM" format
    end_time: Optional[str] = None    # "H:MM AM/PM" format
    date: Optional[str] = None        # "YYYY-MM-DD" format
    emoji: Optional[str] = None       # Emoji icon for the task
    recording_id: str = ""            # ID of the source recording
    source: str = "voice"             # Always "voice" for voice tasks
    
    @property
    def is_today(self) -> bool:
        """Check if this task is for today."""
        if not self.date:
            return True  # Assume today if no date specified
        
        try:
            task_date = dt.datetime.strptime(self.date, "%Y-%m-%d").date()
            today = dt.datetime.now().date()
            return task_date == today
        except (ValueError, TypeError):
            return True  # Assume today if date parsing fails
    
    @property
    def time_range(self) -> Optional[str]:
        """Get formatted time range for display."""
        if self.start_time and self.end_time:
            return f"{self.start_time}–{self.end_time}"
        elif self.start_time:
            return self.start_time
        return None
    
    def to_display_format(self) -> str:
        """Convert to display format for wallpaper."""
        time_part = f"{self.time_range} • " if self.time_range else ""
        return f"{time_part}{self.title}"
