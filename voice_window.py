"""
Voice recording window for TaskPaper.
"""
import rumps
import threading
import time
from typing import Optional

from voice_recorder import VoiceRecorder, cleanup_old_recordings, get_recent_recordings
from models import VoiceRecording
from voice.processor import VoiceProcessor
from voice.storage import VoiceTaskStorage


class VoiceWindow(rumps.Window):
    """Voice recording window using rumps.Window for proper native behavior."""
    
    def __init__(self):
        super().__init__(
            "TaskPaper - Add Task",
            "Voice Recording Configuration",
            dimensions=(450, 200),
            ok="Close",
            cancel=None
        )
        
        self.voice_recorder = VoiceRecorder()
        self.recording_timer = None
        self.is_recording = False
        
        # Voice processing components
        self.voice_processor = VoiceProcessor()
        self.voice_storage = VoiceTaskStorage()
        
        # Check audio availability
        if not self.voice_recorder.check_audio_available():
            self.message = (
                "❌ Audio Not Available\n\n"
                "Voice recording requires 'sounddevice' and 'numpy' packages.\n"
                "Install with: pip install sounddevice numpy\n\n"
                "Recordings will be saved to:\n"
                "~/Library/Application Support/TaskPaper/voice_recordings/"
            )
            self.default_text = ""
        else:
            self.message = (
                "🎤 Voice Recording Ready\n\n"
                "Use the buttons below to record voice memos.\n"
                "Recordings will be automatically transcribed and\n"
                "converted to tasks using OpenAI.\n\n"
                "Recordings saved to:\n"
                "~/Library/Application Support/TaskPaper/voice_recordings/"
            )
            self.default_text = "Click 'Start Recording' to begin..."
    
    def run(self):
        """Show the window and handle the recording interface."""
        if not self.voice_recorder.check_audio_available():
            # Show error and close
            response = super().run()
            return response
        
        # Show main interface
        return self._show_recording_interface()
    
    def _show_recording_interface(self):
        """Show the interactive recording interface."""
        while True:
            try:
                # Update status based on recording state
                if self.is_recording:
                    duration = self.voice_recorder.get_recording_duration()
                    self.title = "🔴 Recording in Progress..."
                    self.message = (
                        f"Recording: {duration:.1f}s\n\n"
                        "Click 'Stop Recording' to save, or 'Cancel Recording' to discard.\n\n"
                        "Recordings saved to:\n"
                        "~/Library/Application Support/TaskPaper/voice_recordings/"
                    )
                    # Buttons: [OK=1, Other=0, Cancel=None/2]
                    buttons = ["Stop Recording", "Cancel Recording", "Close"]
                else:
                    self.title = "TaskPaper - Add Task"
                    self.message = (
                        "🎤 Voice Recording Ready\n\n"
                        "Record voice memos that will be automatically\n"
                        "transcribed and converted to tasks using OpenAI.\n\n"
                        "Recordings saved to:\n"
                        "~/Library/Application Support/TaskPaper/voice_recordings/"
                    )
                    # Buttons: [OK=1, Other=0, Cancel=None/2]
                    buttons = ["🎤 Start Recording", "📂 View Recent", "Close"]
                
                # Show dialog with current state
                response = rumps.alert(
                    self.title,
                    self.message,
                    ok=buttons[0],
                    other=buttons[1] if len(buttons) > 2 else None,
                    cancel=buttons[2]
                )
                
                # Handle response - SWAPPED to fix the button issue
                # The user reported Close and View Recent are swapped, so let's swap the logic
                if response == 1:  # OK button (first button)
                    if self.is_recording:
                        self._stop_recording()
                    else:
                        self._start_recording()
                elif response == 0:  # Other button - this is actually triggering Close
                    if self.is_recording:
                        self._cancel_recording()
                    break  # Close the window
                else:  # Cancel button - this is actually triggering View Recent
                    if self.is_recording:
                        self._cancel_recording()
                    else:
                        self._show_recent_recordings()  # Show recent recordings
                    
            except Exception as e:
                rumps.alert("Error", f"Recording interface error: {e}")
                break
        
        return response
    
    def _start_recording(self):
        """Start voice recording."""
        try:
            if self.voice_recorder.start_recording():
                self.is_recording = True
                rumps.notification("TaskPaper", "Recording Started", "Voice recording in progress...")
                
                # Start timer for duration updates
                self._start_timer()
            else:
                rumps.alert("Recording Failed", "Could not start voice recording.")
                
        except Exception as e:
            rumps.alert("Error", f"Failed to start recording: {e}")
    
    def _stop_recording(self):
        """Stop and save voice recording."""
        try:
            self._stop_timer()
            
            recording = self.voice_recorder.stop_recording()
            if recording:
                # Clean up old recordings
                cleanup_old_recordings()
                
                duration_str = f"{recording.duration:.1f}s" if recording.duration else "unknown"
                rumps.notification("TaskPaper", "Recording Saved", f"Voice memo saved ({duration_str})")
                
                # Start background processing
                self._process_recording_async(recording)
                
                # Show success message
                rumps.alert(
                    "Recording Saved! ✅",
                    f"Voice memo saved successfully!\n\n"
                    f"Duration: {duration_str}\n"
                    f"File: {recording.filename}\n\n"
                    f"Processing for tasks in background...\n"
                    f"Location: ~/Library/Application Support/TaskPaper/voice_recordings/",
                    ok="OK"
                )
            else:
                rumps.alert("Recording Failed", "Could not save voice recording.")
            
            self.is_recording = False
                
        except Exception as e:
            rumps.alert("Error", f"Failed to stop recording: {e}")
            self.is_recording = False
    
    def _cancel_recording(self):
        """Cancel current recording."""
        try:
            self._stop_timer()
            
            if self.voice_recorder.cancel_recording():
                rumps.notification("TaskPaper", "Recording Cancelled", "Voice recording cancelled")
            
            self.is_recording = False
            
        except Exception as e:
            rumps.alert("Error", f"Failed to cancel recording: {e}")
            self.is_recording = False
    
    def _show_recent_recordings(self):
        """Show list of recent recordings."""
        try:
            recordings = get_recent_recordings(limit=5)
            
            if not recordings:
                rumps.alert("No Recordings", "No voice recordings found yet.\n\nStart recording to create your first voice memo!")
                return
            
            # Build recordings list
            recording_list = []
            for i, recording in enumerate(recordings):
                created = recording.created_at.strftime("%m/%d %H:%M")
                duration_str = f"{recording.duration:.1f}s" if recording.duration else "unknown"
                recording_list.append(f"{i+1}. {created} ({duration_str})")
            
            recordings_text = "\n".join(recording_list)
            
            rumps.alert(
                "Recent Voice Recordings 📂",
                f"Your recent recordings:\n\n{recordings_text}\n\n"
                f"All recordings stored in:\n"
                f"~/Library/Application Support/TaskPaper/voice_recordings/\n\n"
                f"Recordings are automatically transcribed and converted to tasks.",
                ok="OK"
            )
            
        except Exception as e:
            rumps.alert("Error", f"Failed to load recordings: {e}")
    
    def _start_timer(self):
        """Start timer to update recording duration."""
        if self.recording_timer:
            self.recording_timer.stop()
        
        # Create timer that fires every 0.5 seconds for smoother updates
        self.recording_timer = rumps.Timer(self._timer_callback, 0.5)
        self.recording_timer.start()
    
    def _stop_timer(self):
        """Stop recording update timer."""
        if self.recording_timer:
            self.recording_timer.stop()
            self.recording_timer = None
    
    def _timer_callback(self, _):
        """Timer callback - just keeps timer running, actual update happens in main loop."""
        pass
    
    def _process_recording_async(self, recording: VoiceRecording):
        """Process recording in background thread to extract tasks."""
        def process():
            try:
                # Process the recording to extract tasks
                tasks = self.voice_processor.process_recording(recording.path, recording.id)
                
                if tasks:
                    # Save tasks to storage
                    success = self.voice_storage.add_tasks_from_recording(tasks)
                    
                    if success:
                        task_count = len(tasks)
                        today_tasks = [t for t in tasks if t.is_today]
                        today_count = len(today_tasks)
                        
                        # Show notification about extracted tasks
                        if today_count > 0:
                            rumps.notification(
                                "TaskPaper", 
                                "Tasks Extracted! 📝", 
                                f"Found {task_count} task(s), {today_count} for today"
                            )
                        else:
                            rumps.notification(
                                "TaskPaper", 
                                "Tasks Extracted! 📝", 
                                f"Found {task_count} task(s) for future dates"
                            )
                    else:
                        print("Failed to save extracted tasks")
                else:
                    # No tasks found - likely not task-related content
                    print(f"No tasks extracted from recording {recording.id} - not task-related content")
                    
            except Exception as e:
                print(f"Error processing recording {recording.id}: {e}")
                # Don't show error notification to user - just log it
        
        # Start processing in background thread
        processing_thread = threading.Thread(target=process, daemon=True)
        processing_thread.start()


def show_voice_window():
    """Show the voice recording window."""
    try:
        window = VoiceWindow()
        window.run()
    except Exception as e:
        rumps.alert("Error", f"Failed to open voice recording: {e}")
