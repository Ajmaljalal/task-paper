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


@dataclass
class VoiceRecording:
    """Voice recording metadata."""
    id: str
    filename: str
    path: str
    created_at: dt.datetime
    duration: Optional[float] = None  # seconds
    transcription: Optional[str] = None
    processed: bool = False


@dataclass
class VoiceTask:
    """Task generated from voice recording."""
    title: str
    source: str  # 'voice'
    time: Optional[str]  # 'HH:MM' 24h or None
    priority: int        # 1..5
    recording_id: str
    link: Optional[str] = None
