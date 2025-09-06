"""
Google Calendar service operations for TaskPaper.
"""
import datetime as dt
from typing import List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from taskpaper.core.config import TZ
from taskpaper.core.models import CalItem


def get_today_events(creds: Credentials) -> List[CalItem]:
    """
    Fetch today's calendar events, filtering out past events.
    
    Args:
        creds: Google OAuth credentials
        
    Returns:
        List of CalItem objects for events that haven't ended yet
    """
    svc = build("calendar", "v3", credentials=creds, cache_discovery=False)
    now = dt.datetime.now(TZ)
    
    # Define today's time range
    start = dt.datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=TZ).isoformat()
    end = dt.datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=TZ).isoformat()
    
    # Fetch events
    resp = svc.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    items = resp.get("items", [])
    events: List[CalItem] = []
    current_time = dt.datetime.now(TZ)

    def parse_datetime(obj_key: str, event: dict) -> dt.datetime:
        """Parse datetime from calendar event."""
        val = event.get(obj_key, {})
        if "dateTime" in val:
            # Handle Z or offset
            return dt.datetime.fromisoformat(val["dateTime"].replace("Z", "+00:00")).astimezone(TZ)
        if "date" in val:
            return dt.datetime.fromisoformat(val["date"] + "T00:00:00").replace(tzinfo=TZ)
        return dt.datetime.now(TZ)

    for event in items:
        start_time, end_time = parse_datetime("start", event), parse_datetime("end", event)
        
        # Skip events that have already ended
        if end_time <= current_time:
            continue
            
        events.append(CalItem(
            id=event.get("id", ""),
            start=start_time,
            end=end_time,
            summary=event.get("summary", "(no title)"),
            location=event.get("location"),
            hangoutLink=event.get("hangoutLink")
        ))
    
    return events
