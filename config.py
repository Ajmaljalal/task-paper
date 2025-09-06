"""
Configuration constants for TaskPaper app.
"""
import os
import json
import datetime as dt
from typing import Optional, Dict, Any

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

# Voice recording directories
VOICE_DIR = os.path.join(APP_DIR, "voice_recordings")
os.makedirs(VOICE_DIR, exist_ok=True)

# Timezone
TZ = dt.datetime.now().astimezone().tzinfo

# Wallpaper settings
MAX_CARD_WIDTH = 600
MAX_CARD_HEIGHT = 700
WALLPAPER_KEEP_COUNT = 3

# Voice recording settings
VOICE_SAMPLE_RATE = 44100  # CD quality
VOICE_CHANNELS = 1  # Mono
VOICE_FORMAT = "wav"  # WAV format for quality
VOICE_KEEP_COUNT = 10  # Number of recordings to keep

# Configuration file path
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

# LLM settings
LLM_SYSTEM_PROMPT = (
    "You are my personal assistant. I will give you a list of calendar events. "
    "You will extract up to 6 urgent, actionable tasks that must be handled TODAY. "
    "Make sure the tasks are actionable and have a deadline, and is related to me not someone else.\n"
    "Prefer: meetings starting soon, high priority events, explicit deadlines/times.\n"
    "Return strict JSON array: [{\"title\": str, \"source\": \"calendar\", \"time\": \"HH:MM\"|null, \"priority\": 1..5, \"link\": str|null}]\n"
)


# Configuration management functions
def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from config file or environment variable."""
    # First check config file
    config = load_config()
    api_key = config.get('openai_api_key')
    
    if api_key:
        return api_key
    
    # Fall back to environment variable
    return os.getenv("OPENAI_API_KEY")


def set_openai_api_key(api_key: str) -> bool:
    """Save OpenAI API key to config file."""
    config = load_config()
    config['openai_api_key'] = api_key
    return save_config(config)


def has_openai_api_key() -> bool:
    """Check if OpenAI API key is configured."""
    return get_openai_api_key() is not None
