"""
Google OAuth authentication handling for TaskPaper.
"""
import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from taskpaper.core.config import SCOPES, TOKEN_PATH, CREDS_PATH


def load_credentials() -> Optional[Credentials]:
    """Load existing credentials from token file."""
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            return creds
    return None


def connect_google() -> Optional[Credentials]:
    """Initiate Google OAuth flow and save credentials."""
    if not os.path.exists(CREDS_PATH):
        raise FileNotFoundError(f"credentials.json not found at: {CREDS_PATH}")
    
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    
    return creds
