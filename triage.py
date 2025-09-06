"""
Task triage using LLM and heuristic fallbacks for TaskPaper.
"""
import json
import datetime as dt
from typing import List, Optional
import os

from config import LLM_SYSTEM_PROMPT, TZ, get_openai_api_key
from models import CalItem, UrgentTask

# Optional LLM (OpenAI)
OPENAI = None
try:
    from openai import OpenAI
    api_key = get_openai_api_key()
    if api_key:
        OPENAI = OpenAI(api_key=api_key)
except Exception:
    OPENAI = None


def reinitialize_openai():
    """Reinitialize OpenAI client with current API key from config."""
    global OPENAI
    try:
        from openai import OpenAI
        api_key = get_openai_api_key()
        if api_key:
            OPENAI = OpenAI(api_key=api_key)
        else:
            OPENAI = None
    except Exception:
        OPENAI = None


def triage_events(today_str: str, events: List[CalItem]) -> List[UrgentTask]:
    """
    Triage calendar events to identify urgent tasks using LLM or heuristics.
    
    Args:
        today_str: Today's date string (YYYY-MM-DD)
        events: List of calendar events
        
    Returns:
        List of urgent tasks, max 6 items
    """
    # Build prompt for LLM
    event_text = "\n".join(
        f"- [event] {event.start:%H:%M}-{event.end:%H:%M} {event.summary}"
        for event in events
    )
    user_prompt = f"TODAY: {today_str}\n\nCALENDAR (today):\n{event_text}\n"

    # Try LLM first
    tasks_json = _try_llm_triage(user_prompt)
    
    # Fall back to heuristics if LLM fails
    if tasks_json is None:
        tasks_json = _heuristic_triage(events)

    # Convert to UrgentTask objects
    return _parse_tasks(tasks_json)


def _try_llm_triage(user_prompt: str) -> Optional[List[dict]]:
    """Try to use LLM for triaging tasks."""
    if not OPENAI:
        return None
        
    try:
        res = OPENAI.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = res.choices[0].message.content
        parsed = json.loads(content)
        
        # Accept either an array or an object with "tasks"/"items"
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return parsed.get("tasks") or parsed.get("items") or []
    except Exception:
        return None
    
    return None


def _heuristic_triage(events: List[CalItem]) -> List[dict]:
    """Fallback heuristic triage for near-term meetings."""
    tasks_json = []
    now = dt.datetime.now(TZ)
    
    for event in events:
        # Skip events that have already ended
        if event.end <= now:
            continue
            
        # Meetings starting within next 3 hours, or ongoing
        seconds_until_start = (event.start - now).total_seconds()
        if seconds_until_start <= 3 * 3600:  # 3 hours
            tasks_json.append({
                "title": f"Meeting: {event.summary}",
                "source": "calendar",
                "time": event.start.strftime("%H:%M"),
                "priority": 5,
                "link": event.hangoutLink
            })
    
    return tasks_json[:6]


def _parse_tasks(tasks_json: List[dict]) -> List[UrgentTask]:
    """Parse task dictionaries into UrgentTask objects."""
    tasks: List[UrgentTask] = []
    
    for item in tasks_json:
        try:
            task = UrgentTask(
                title=(item.get("title") or "(no title)")[:140],
                source=(item.get("source") or "calendar")[:16],
                time=item.get("time"),
                priority=int(item.get("priority") or 3),
                link=item.get("link")
            )
            tasks.append(task)
        except Exception:
            continue  # Skip invalid tasks

    # Deduplicate by title, keep order
    seen = set()
    unique_tasks = []
    for task in tasks:
        if task.title not in seen:
            seen.add(task.title)
            unique_tasks.append(task)
    
    return unique_tasks[:6]
