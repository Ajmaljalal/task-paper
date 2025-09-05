"""
Configuration constants for TaskPaper app.
"""
import os
import datetime as dt

# App configuration
APP_NAME = "TaskPaper"
REFRESH_SECONDS = 60

# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]

# Directories and paths
APP_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
os.makedirs(APP_DIR, exist_ok=True)

TOKEN_PATH = os.path.join(APP_DIR, "token.json")
CREDS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
WALL_DIR = os.path.join(APP_DIR, "wallpapers")
os.makedirs(WALL_DIR, exist_ok=True)

# Timezone
TZ = dt.datetime.now().astimezone().tzinfo

# Wallpaper settings
MAX_CARD_WIDTH = 600
MAX_CARD_HEIGHT = 700
WALLPAPER_KEEP_COUNT = 3

# LLM settings
LLM_SYSTEM_PROMPT = (
    "You are my personal assistant. I will give you a list of calendar events. "
    "You will extract up to 6 urgent, actionable tasks that must be handled TODAY. "
    "Make sure the tasks are actionable and have a deadline, and is related to me not someone else.\n"
    "Prefer: meetings starting soon, high priority events, explicit deadlines/times.\n"
    "Return strict JSON array: [{\"title\": str, \"source\": \"calendar\", \"time\": \"HH:MM\"|null, \"priority\": 1..5, \"link\": str|null}]\n"
)
