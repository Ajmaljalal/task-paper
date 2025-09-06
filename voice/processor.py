"""
Voice processing for TaskPaper - OpenAI integration for transcription and task extraction.
"""
import json
import datetime as dt
from typing import Optional, List
from pathlib import Path

from .models import VoiceTaskExtended

# Will be initialized when needed
OPENAI_CLIENT = None


def initialize_openai():
    """Initialize OpenAI client if API key is available."""
    global OPENAI_CLIENT
    
    try:
        # Import OpenAI and get API key from config
        import openai
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from config import load_config
        
        config = load_config()
        api_key = config.get('openai_api_key')
        
        if api_key:
            OPENAI_CLIENT = openai.OpenAI(api_key=api_key)
        else:
            OPENAI_CLIENT = None
            
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        OPENAI_CLIENT = None


class VoiceProcessor:
    """Processes voice recordings to extract structured tasks."""
    
    def __init__(self):
        if OPENAI_CLIENT is None:
            initialize_openai()
    
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
        
        system_prompt = """You are a personal assistant that extracts tasks from voice recordings.

IMPORTANT: Only extract if the text is about adding/creating tasks, todos, or reminders. If the text is just conversation, notes, or not task-related, return null.

Extract tasks with these fields:
- title: Clear, actionable task title
- description: Additional details (optional)  
- priority: 1 (urgent) to 5 (low), default 3
- start_time: "HH:MM" format if mentioned (optional)
- end_time: "HH:MM" format if mentioned (optional)
- date: "YYYY-MM-DD" format, default to today if not specified
- emoji: Relevant emoji for the task (optional)

Return JSON format:
{"tasks": [{"title": "...", "description": "...", "priority": 3, "start_time": "09:00", "end_time": "10:00", "date": "2024-01-15", "emoji": "📅"}]}

Return null if not task-related."""

        user_prompt = f"TODAY: {today}\n\nVOICE TRANSCRIPTION:\n{text}"
        
        try:
            response = OPENAI_CLIENT.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
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
