"""
Voice processing for TaskPaper - OpenAI integration for transcription and task extraction.
"""
import json
import datetime as dt
import os
import sys
from typing import Optional, List

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_openai_api_key, VOICE_SYSTEM_PROMPT

from .models import VoiceTaskExtended

# OpenAI client - will be initialized when needed
OPENAI_CLIENT = None

try:
    from openai import OpenAI
    api_key = get_openai_api_key()
    if api_key:
        OPENAI_CLIENT = OpenAI(api_key=api_key)
except Exception:
    OPENAI_CLIENT = None


def reinitialize_openai():
    """Reinitialize OpenAI client with current API key from config."""
    global OPENAI_CLIENT
    try:
        from openai import OpenAI
        api_key = get_openai_api_key()
        if api_key:
            OPENAI_CLIENT = OpenAI(api_key=api_key)
        else:
            OPENAI_CLIENT = None
    except Exception:
        OPENAI_CLIENT = None


class VoiceProcessor:
    """Processes voice recordings to extract structured tasks."""
    
    def __init__(self):
        if OPENAI_CLIENT is None:
            reinitialize_openai()
    
    def process_recording(self, audio_file_path: str, recording_id: str) -> Optional[List[VoiceTaskExtended]]:
        """
        Process a voice recording to extract tasks.
        
        Args:
            audio_file_path: Path to the audio file
            recording_id: ID of the recording
            
        Returns:
            List of extracted tasks or None if not task-related
        """
        if not OPENAI_CLIENT:
            print("OpenAI client not available")
            return None
        
        try:
            # Step 1: Transcribe audio
            transcription = self._transcribe_audio(audio_file_path)
            if not transcription:
                return None
            
            # Step 2: Extract tasks from transcription
            tasks = self._extract_tasks_from_text(transcription, recording_id)
            return tasks
            
        except Exception as e:
            print(f"Error processing voice recording: {e}")
            return None
    
    def _transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file using OpenAI Whisper."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = OPENAI_CLIENT.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return response.strip()
            
        except Exception as e:
            print(f"Transcription failed: {e}")
            return None
    
    def _extract_tasks_from_text(self, text: str, recording_id: str) -> Optional[List[VoiceTaskExtended]]:
        """Extract structured tasks from transcribed text using GPT."""
        today = dt.datetime.now().strftime("%Y-%m-%d")
        user_prompt = f"TODAY: {today}\n\nVOICE TRANSCRIPTION:\n{text}"
        
        try:
            response = OPENAI_CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": VOICE_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            
            # Handle null response
            if result.lower() == 'null' or not result:
                return None
            
            # Parse JSON response
            try:
                data = json.loads(result)
                if not data or 'tasks' not in data or not data['tasks']:
                    return None
                
                # Convert to VoiceTaskExtended objects
                tasks = []
                for task_data in data['tasks']:
                    task = VoiceTaskExtended(
                        title=task_data.get('title', 'Untitled Task'),
                        description=task_data.get('description'),
                        priority=int(task_data.get('priority', 3)),
                        start_time=task_data.get('start_time'),
                        end_time=task_data.get('end_time'),
                        date=task_data.get('date', today),
                        emoji=task_data.get('emoji'),
                        recording_id=recording_id,
                        source="voice"
                    )
                    tasks.append(task)
                
                return tasks if tasks else None
                
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Response was: {result}")
                return None
                
        except Exception as e:
            print(f"Task extraction failed: {e}")
            return None
