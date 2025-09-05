"""
Data models for TaskPaper app.
"""
import datetime as dt
from dataclasses import dataclass
from typing import Optional


@dataclass
class CalItem:
    """Calendar event item."""
    id: str
    start: dt.datetime
    end: dt.datetime
    summary: str
    location: Optional[str] = None
    hangoutLink: Optional[str] = None


@dataclass
class UrgentTask:
    """Urgent task extracted from calendar events."""
    title: str
    source: str  # 'calendar'
    time: Optional[str]  # 'HH:MM' 24h or None
    priority: int        # 1..5
    link: Optional[str] = None


@dataclass
class DisplayItem:
    """Item to display on wallpaper."""
    text: str
    source: str
    priority: int
    type: str  # 'task' or 'event'
