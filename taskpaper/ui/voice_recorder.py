"""
Voice recording functionality for TaskPaper.
"""
import os
import time
import uuid
import wave
import threading
import datetime as dt
from typing import Optional, Callable, Any

from taskpaper.core.config import VOICE_DIR, VOICE_SAMPLE_RATE, VOICE_CHANNELS, VOICE_FORMAT
from taskpaper.core.models import VoiceRecording

# Audio recording library
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    sd = None
    np = None
    AUDIO_AVAILABLE = False


class VoiceRecorder:
    """Voice recording manager."""
    
    def __init__(self):
        self.is_recording = False
        self.recording_data = []
        self.recording_thread = None
        self.current_recording = None
        self.start_time = None
        
    def check_audio_available(self) -> bool:
        """Check if audio recording is available."""
        return AUDIO_AVAILABLE
    
    def get_audio_devices(self) -> list:
        """Get available audio input devices."""
        if not AUDIO_AVAILABLE:
            return []
        
        try:
            devices = sd.query_devices()
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels']
                    })
            return input_devices
        except Exception:
            return []
    
    def start_recording(self, device_id: Optional[int] = None) -> bool:
        """
        Start voice recording.
        
        Args:
            device_id: Audio device ID, None for default
            
        Returns:
            True if recording started successfully
        """
        if not AUDIO_AVAILABLE:
            return False
            
        if self.is_recording:
            return False
            
        try:
            # Create recording metadata
            recording_id = str(uuid.uuid4())
            timestamp = dt.datetime.now()
            filename = f"voice_{timestamp:%Y%m%d_%H%M%S}_{recording_id[:8]}.{VOICE_FORMAT}"
            filepath = os.path.join(VOICE_DIR, filename)
            
            self.current_recording = VoiceRecording(
                id=recording_id,
                filename=filename,
                path=filepath,
                created_at=timestamp
            )
            
            # Initialize recording
            self.recording_data = []
            self.is_recording = True
            self.start_time = time.time()
            
            # Start recording in separate thread
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                args=(device_id,),
                daemon=True
            )
            self.recording_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> Optional[VoiceRecording]:
        """
        Stop voice recording and save file.
        
        Returns:
            VoiceRecording object if successful, None otherwise
        """
        if not self.is_recording or not self.current_recording:
            return None
            
        try:
            # Stop recording
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)
            
            # Calculate duration
            if self.start_time:
                duration = time.time() - self.start_time
                self.current_recording.duration = duration
            
            # Save audio file
            if self.recording_data and len(self.recording_data) > 0:
                self._save_audio_file(
                    self.current_recording.path,
                    np.concatenate(self.recording_data, axis=0)
                )
                
                recording = self.current_recording
                self.current_recording = None
                self.recording_data = []
                
                return recording
            else:
                # No data recorded
                self.current_recording = None
                self.recording_data = []
                return None
                
        except Exception as e:
            print(f"Failed to stop recording: {e}")
            self.is_recording = False
            self.current_recording = None
            self.recording_data = []
            return None
    
    def cancel_recording(self) -> bool:
        """
        Cancel current recording without saving.
        
        Returns:
            True if cancelled successfully
        """
        if not self.is_recording:
            return False
            
        try:
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)
            
            # Clean up
            self.current_recording = None
            self.recording_data = []
            
            return True
            
        except Exception:
            return False
    
    def get_recording_duration(self) -> float:
        """Get current recording duration in seconds."""
        if not self.is_recording or not self.start_time:
            return 0.0
        return time.time() - self.start_time
    
    def _record_audio(self, device_id: Optional[int]):
        """Internal method to record audio in separate thread."""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"Recording status: {status}")
                if self.is_recording:
                    self.recording_data.append(indata.copy())
            
            # Start recording stream
            with sd.InputStream(
                callback=audio_callback,
                device=device_id,
                channels=VOICE_CHANNELS,
                samplerate=VOICE_SAMPLE_RATE,
                dtype=np.float32
            ):
                while self.is_recording:
                    sd.sleep(100)  # Sleep 100ms
                    
        except Exception as e:
            print(f"Recording error: {e}")
            self.is_recording = False
    
    def _save_audio_file(self, filepath: str, audio_data: Any):
        """Save recorded audio data to WAV file."""
        try:
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Save as WAV file
            with wave.open(filepath, 'wb') as wav_file:
                wav_file.setnchannels(VOICE_CHANNELS)
                wav_file.setsampwidth(2)  # 2 bytes for int16
                wav_file.setframerate(VOICE_SAMPLE_RATE)
                wav_file.writeframes(audio_int16.tobytes())
                
        except Exception as e:
            print(f"Failed to save audio file: {e}")
            raise


def cleanup_old_recordings(keep_count: int = None):
    """
    Clean up old voice recordings, keeping only the most recent ones.
    
    Args:
        keep_count: Number of recordings to keep, uses config default if None
    """
    if keep_count is None:
        from taskpaper.core.config import VOICE_KEEP_COUNT
        keep_count = VOICE_KEEP_COUNT
    
    try:
        # Get all recording files
        files = []
        for filename in os.listdir(VOICE_DIR):
            if filename.startswith('voice_') and filename.endswith(f'.{VOICE_FORMAT}'):
                filepath = os.path.join(VOICE_DIR, filename)
                if os.path.isfile(filepath):
                    files.append(filepath)
        
        # Sort by modification time (newest first)
        files.sort(key=os.path.getmtime, reverse=True)
        
        # Delete files beyond keep_count
        files_to_delete = files[keep_count:]
        for filepath in files_to_delete:
            try:
                os.remove(filepath)
            except OSError:
                pass  # Ignore errors if file is in use
                
    except Exception:
        pass  # Silently ignore cleanup errors


