"""
Configuration window for TaskPaper.
"""
import rumps
import threading
import time
from typing import Optional

from voice_recorder import VoiceRecorder, cleanup_old_recordings, get_recent_recordings
from models import VoiceRecording


class ConfigWindow:
    """Configuration window for TaskPaper settings."""
    
    def __init__(self):
        self.window = None
        self.voice_recorder = VoiceRecorder()
        self.recording_timer = None
        self.recording_duration = 0.0
        self.current_recording = None
        self._is_open = False
        
        # UI state
        self.recording_status = "Ready to record"
        self.record_button_title = "🎤 Start Recording"
        
    def is_open(self) -> bool:
        """Check if configuration window is open."""
        return self._is_open
    
    def show(self):
        """Show the configuration window."""
        if self._is_open:
            return
            
        self._is_open = True
        self._show_voice_recording_dialog()
    
    def close(self):
        """Close the configuration window."""
        if self.recording_timer:
            self.recording_timer.stop()
            self.recording_timer = None
            
        # Cancel any ongoing recording
        if self.voice_recorder.is_recording:
            self.voice_recorder.cancel_recording()
            
        self._is_open = False
    
    def _show_voice_recording_dialog(self):
        """Show voice recording interface using rumps dialogs."""
        try:
            # Check audio availability
            if not self.voice_recorder.check_audio_available():
                rumps.alert(
                    "Audio Not Available",
                    "Voice recording requires the 'sounddevice' and 'numpy' packages.\n\n"
                    "Install with: pip install sounddevice numpy",
                    ok="OK"
                )
                self._is_open = False
                return
            
            # Show main voice recording interface
            self._show_recording_interface()
            
        except Exception as e:
            rumps.alert("Error", f"Failed to open voice recording: {e}")
            self._is_open = False
    
    def _show_recording_interface(self):
        """Show the main recording interface."""
        while self._is_open:
            try:
                # Build status message
                if self.voice_recorder.is_recording:
                    duration = self.voice_recorder.get_recording_duration()
                    status_msg = f"🔴 Recording... ({duration:.1f}s)"
                    buttons = ["Stop Recording", "Cancel", "Close"]
                else:
                    status_msg = "Ready to record voice memo"
                    buttons = ["🎤 Start Recording", "View Recent", "Close"]
                
                # Show dialog
                response = rumps.alert(
                    "TaskPaper Voice Recording",
                    status_msg,
                    ok=buttons[0],
                    cancel=buttons[2] if len(buttons) > 2 else None,
                    other=buttons[1] if len(buttons) > 2 else None
                )
                
                # Handle response
                if response == 1:  # First button (OK)
                    if self.voice_recorder.is_recording:
                        self._stop_recording()
                    else:
                        self._start_recording()
                elif response == 0:  # Other button
                    if self.voice_recorder.is_recording:
                        self._cancel_recording()
                    else:
                        self._show_recent_recordings()
                else:  # Cancel or Close
                    if self.voice_recorder.is_recording:
                        self._cancel_recording()
                    break
                    
            except Exception as e:
                rumps.alert("Error", f"Recording interface error: {e}")
                break
        
        self.close()
    
    def _start_recording(self):
        """Start voice recording."""
        try:
            # Get available devices
            devices = self.voice_recorder.get_audio_devices()
            if not devices:
                rumps.alert("No Audio Device", "No audio input devices found.")
                return
            
            # Use default device (first available)
            device_id = None  # Use system default
            
            # Start recording
            if self.voice_recorder.start_recording(device_id):
                rumps.notification("TaskPaper", "Recording Started", "Voice recording in progress...")
                
                # Start update timer to refresh the dialog
                self._start_recording_timer()
            else:
                rumps.alert("Recording Failed", "Could not start voice recording.")
                
        except Exception as e:
            rumps.alert("Error", f"Failed to start recording: {e}")
    
    def _stop_recording(self):
        """Stop and save voice recording."""
        try:
            self._stop_recording_timer()
            
            recording = self.voice_recorder.stop_recording()
            if recording:
                # Clean up old recordings
                cleanup_old_recordings()
                
                duration_str = f"{recording.duration:.1f}s" if recording.duration else "unknown"
                rumps.notification(
                    "TaskPaper", 
                    "Recording Saved", 
                    f"Voice memo saved ({duration_str})"
                )
                
                # Show save confirmation
                rumps.alert(
                    "Recording Saved",
                    f"Voice memo saved successfully!\n\n"
                    f"Duration: {duration_str}\n"
                    f"File: {recording.filename}",
                    ok="OK"
                )
            else:
                rumps.alert("Recording Failed", "Could not save voice recording.")
                
        except Exception as e:
            rumps.alert("Error", f"Failed to stop recording: {e}")
    
    def _cancel_recording(self):
        """Cancel current recording."""
        try:
            self._stop_recording_timer()
            
            if self.voice_recorder.cancel_recording():
                rumps.notification("TaskPaper", "Recording Cancelled", "Voice recording cancelled")
            
        except Exception as e:
            rumps.alert("Error", f"Failed to cancel recording: {e}")
    
    def _show_recent_recordings(self):
        """Show list of recent recordings."""
        try:
            recordings = get_recent_recordings(limit=5)
            
            if not recordings:
                rumps.alert("No Recordings", "No voice recordings found.")
                return
            
            # Build recordings list
            recording_list = []
            for i, recording in enumerate(recordings):
                created = recording.created_at.strftime("%m/%d %H:%M")
                duration_str = f"{recording.duration:.1f}s" if recording.duration else "unknown"
                recording_list.append(f"{i+1}. {created} ({duration_str})")
            
            recordings_text = "\n".join(recording_list)
            
            rumps.alert(
                "Recent Voice Recordings",
                f"Recent recordings:\n\n{recordings_text}\n\n"
                f"Recordings are stored in:\n~/Library/Application Support/TaskPaper/voice_recordings/",
                ok="OK"
            )
            
        except Exception as e:
            rumps.alert("Error", f"Failed to load recordings: {e}")
    
    def _start_recording_timer(self):
        """Start timer to update recording duration."""
        if self.recording_timer:
            self.recording_timer.stop()
        
        # Create timer that fires every second while recording
        self.recording_timer = rumps.Timer(self._update_recording_status, 1)
        self.recording_timer.start()
    
    def _stop_recording_timer(self):
        """Stop recording update timer."""
        if self.recording_timer:
            self.recording_timer.stop()
            self.recording_timer = None
    
    def _update_recording_status(self, _):
        """Update recording status (called by timer)."""
        # This timer runs in background to keep duration updated
        # The actual UI update happens when the dialog is refreshed
        pass
