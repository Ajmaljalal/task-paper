"""
Voice task storage management for TaskPaper.
"""
import json
import os
import datetime as dt
from typing import List, Optional
from pathlib import Path

from .models import VoiceTaskExtended


class VoiceTaskStorage:
    """Manages local storage of voice-extracted tasks."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # Use the same app directory as the main app
            from taskpaper.core.config import APP_DIR
            self.storage_dir = Path(APP_DIR)
        
        self.storage_dir.mkdir(exist_ok=True)
        self.tasks_file = self.storage_dir / "voice_tasks.json"
    
    def load_voice_tasks(self) -> List[VoiceTaskExtended]:
        """Load all voice tasks from storage."""
        try:
            if not self.tasks_file.exists():
                return []
            
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = []
            for task_data in data.get('tasks', []):
                task = VoiceTaskExtended(
                    title=task_data.get('title', ''),
                    description=task_data.get('description'),
                    priority=task_data.get('priority', 3),
                    start_time=task_data.get('start_time'),
                    end_time=task_data.get('end_time'),
                    date=task_data.get('date'),
                    emoji=task_data.get('emoji'),
                    recording_id=task_data.get('recording_id', ''),
                    source=task_data.get('source', 'voice')
                )
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            print(f"Failed to load voice tasks: {e}")
            return []
    
    def save_voice_tasks(self, tasks: List[VoiceTaskExtended]) -> bool:
        """Save voice tasks to storage."""
        try:
            data = {
                'last_updated': dt.datetime.now().isoformat(),
                'tasks': []
            }
            
            for task in tasks:
                task_data = {
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'start_time': task.start_time,
                    'end_time': task.end_time,
                    'date': task.date,
                    'emoji': task.emoji,
                    'recording_id': task.recording_id,
                    'source': task.source
                }
                data['tasks'].append(task_data)
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Failed to save voice tasks: {e}")
            return False
    
    def add_tasks_from_recording(self, new_tasks: List[VoiceTaskExtended]) -> bool:
        """Add new tasks from a recording, merging with existing tasks."""
        try:
            # Load existing tasks
            existing_tasks = self.load_voice_tasks()
            
            # Filter out tasks from the same recording (in case of reprocessing)
            if new_tasks and new_tasks[0].recording_id:
                recording_id = new_tasks[0].recording_id
                existing_tasks = [t for t in existing_tasks if t.recording_id != recording_id]
            
            # Merge tasks
            all_tasks = existing_tasks + new_tasks
            
            # Save merged tasks
            return self.save_voice_tasks(all_tasks)
            
        except Exception as e:
            print(f"Failed to add tasks from recording: {e}")
            return False
    
    def get_today_tasks(self) -> List[VoiceTaskExtended]:
        """Get only today's voice tasks that are not past due."""
        all_tasks = self.load_voice_tasks()
        return [task for task in all_tasks if task.is_today and task.is_not_past_due]
    
    def get_active_tasks(self) -> List[VoiceTaskExtended]:
        """Get all active tasks (today's and future tasks that are not past due)."""
        all_tasks = self.load_voice_tasks()
        return [task for task in all_tasks if task.is_not_past_due]
    
    def cleanup_old_tasks(self, days_to_keep: int = 30) -> bool:
        """Remove tasks older than specified days."""
        try:
            all_tasks = self.load_voice_tasks()
            cutoff_date = dt.datetime.now().date() - dt.timedelta(days=days_to_keep)
            
            filtered_tasks = []
            for task in all_tasks:
                if task.date:
                    try:
                        task_date = dt.datetime.strptime(task.date, "%Y-%m-%d").date()
                        if task_date >= cutoff_date:
                            filtered_tasks.append(task)
                    except (ValueError, TypeError):
                        # Keep tasks with invalid dates
                        filtered_tasks.append(task)
                else:
                    # Keep tasks without dates
                    filtered_tasks.append(task)
            
            return self.save_voice_tasks(filtered_tasks)
            
        except Exception as e:
            print(f"Failed to cleanup old tasks: {e}")
            return False
