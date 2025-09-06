"""
Settings window for TaskPaper - handles general configuration like OpenAI API key.
"""
import rumps
from config import get_openai_api_key, set_openai_api_key, has_openai_api_key
from triage import reinitialize_openai


class SettingsWindow(rumps.Window):
    """Settings window for general configuration."""
    
    def __init__(self):
        super().__init__(
            "⚙️ TaskPaper - Settings",
            "Configure TaskPaper settings:",
            dimensions=(500, 200),
            ok="Close",
            cancel=None
        )
        
    def run(self):
        """Show the settings window."""
        while True:
            # Check current OpenAI status
            openai_status = "✅ Configured" if has_openai_api_key() else "❌ Not configured"
            
            response = rumps.alert(
                "⚙️ TaskPaper Settings",
                f"Current configuration:\n\n"
                f"🤖 OpenAI API Key: {openai_status}\n\n"
                f"OpenAI enables AI-powered task triaging from your calendar events.\n"
                f"Without it, the app will use basic heuristics for task detection.",
                ok="🤖 Configure OpenAI",
                other="Close",
                cancel=None
            )
            
            if response == 1:  # Configure OpenAI
                if self._show_openai_config():
                    continue  # Return to settings after successful config
                else:
                    break  # User cancelled
            else:  # Close
                break
    
    def _show_openai_config(self):
        """Show OpenAI API key configuration."""
        # Load current API key (masked for display)
        current_key = get_openai_api_key()
        if current_key:
            # Show only last 4 characters for security
            masked_key = "sk-..." + current_key[-4:] if len(current_key) > 4 else current_key
            default_text = masked_key
        else:
            default_text = "sk-..."
        
        window = rumps.Window(
            "🤖 OpenAI API Key",
            "Enter your OpenAI API key to enable AI-powered task triaging:",
            dimensions=(500, 150),
            ok="Save",
            cancel="Cancel"
        )
        window.default_text = default_text
        
        response = window.run()
        
        if response.clicked == 1:  # Save button
            api_key = response.text.strip()
            
            # Don't save if user didn't change the masked display
            if current_key and api_key == "sk-..." + current_key[-4:]:
                return True  # No change needed
            
            # Validate API key format
            if not api_key.startswith("sk-") or len(api_key) < 20:
                rumps.alert(
                    "Invalid API Key",
                    "Please enter a valid OpenAI API key.\n\n"
                    "API keys start with 'sk-' and are typically 51 characters long.\n"
                    "You can get your API key from: https://platform.openai.com/api-keys"
                )
                return False
            
            # Test the API key
            if self._test_api_key(api_key):
                # Save the API key
                if set_openai_api_key(api_key):
                    # Reinitialize OpenAI client
                    reinitialize_openai()
                    rumps.notification(
                        "TaskPaper", 
                        "OpenAI Configured", 
                        "API key saved successfully. AI-powered task triaging is now enabled."
                    )
                    return True
                else:
                    rumps.alert("Error", "Failed to save API key. Please try again.")
                    return False
            else:
                rumps.alert(
                    "Invalid API Key",
                    "The API key you entered is not valid or cannot be used.\n\n"
                    "Please check your key and try again.\n"
                    "You can get your API key from: https://platform.openai.com/api-keys"
                )
                return False
        
        return response.clicked == 1
    
    def _test_api_key(self, api_key: str) -> bool:
        """Test if the API key is valid by making a simple API call."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Make a minimal test call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False


def show_settings():
    """Show the settings window."""
    try:
        window = SettingsWindow()
        window.run()
    except Exception as e:
        rumps.alert("Error", f"Failed to open settings: {e}")


def show_initial_openai_setup():
    """Show OpenAI setup on first launch."""
    try:
        # Show notification first
        rumps.notification(
            "TaskPaper", 
            "Setup Required", 
            "OpenAI API key needed for AI-powered task triaging."
        )
        
        window = SettingsWindow()
        window._show_openai_config()
        
    except Exception as e:
        print(f"Error showing initial OpenAI setup: {e}")
