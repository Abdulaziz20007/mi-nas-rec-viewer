"""
Video player widget using Qt Multimedia for seamless playback.
"""
import sys
from datetime import timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QSlider, QLabel, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from typing import List, Optional
import os

from models import VideoSegment


class VideoPlayerWidget(QWidget):
    """Video player widget using Qt Multimedia integration."""
    
    # Signals
    position_changed = pyqtSignal(float)  # Position in seconds
    duration_changed = pyqtSignal(float)  # Duration in seconds
    time_changed = pyqtSignal(int)  # Current time in milliseconds
    media_changed = pyqtSignal(str)  # Current media path
    
    def __init__(self):
        super().__init__()
        
        # Qt Multimedia player setup
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        
        # Playback state
        self.current_playlist: List[VideoSegment] = []
        self.is_playing = False
        self.total_duration = 0.0
        self.pending_seek_ms = -1
        
        # UI setup
        self.setup_ui()
        self.setup_player()
        
    def setup_ui(self):
        """Setup the video player UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video display area
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(400)
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.video_widget)
        
        self.seeking = False # This is now unused but kept for minimal diff
    
    def setup_player(self):
        """Initialize media player."""
        self.player.setVideoOutput(self.video_widget)
        self.player.positionChanged.connect(self._emit_position_changed)
        self.player.playbackStateChanged.connect(self.on_playback_state_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.errorOccurred.connect(self.on_player_error)
        self.set_volume(80)
    
    def load_playlist(self, video_segments: List[VideoSegment]):
        """Load a playlist of video segments."""
        self.player.stop()
        self.current_playlist = video_segments
        self.current_segment_index = -1
        self.total_duration = sum(seg.duration for seg in video_segments if os.path.exists(seg.path))
        self.pending_seek_ms = -1

        if self.current_playlist:
            self.play_segment(0)
            self.pause()  # Start paused
        else:
            self.player.setSource(QUrl())  # Clear source

    def play_segment(self, index: int):
        """Play a specific segment from the playlist."""
        if 0 <= index < len(self.current_playlist):
            self.current_segment_index = index
            segment = self.current_playlist[index]
            if os.path.exists(segment.path):
                self.player.setSource(QUrl.fromLocalFile(segment.path))
                if self.is_playing:
                    self.player.play()
            else:
                # Skip to next segment if file doesn't exist
                self.on_media_status_changed(QMediaPlayer.MediaStatus.EndOfMedia)
    
    def play(self):
        """Start playback."""
        self.is_playing = True
        self.player.play()
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
        self.player.pause()
    
    def stop(self):
        """Stop playback."""
        self.player.stop()
        self.is_playing = False
    
    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()
    
    def seek_to_time(self, seconds: float):
        """Seek to a specific time in seconds from the start of the day."""
        if not self.current_playlist or not self.player:
            return
        
        target_segment_index = -1
        time_in_segment_ms = 0
        
        for i, segment in enumerate(self.current_playlist):
            st = segment.start_time
            start_seconds_of_segment = st.hour * 3600 + st.minute * 60 + st.second
            end_seconds_of_segment = start_seconds_of_segment + segment.duration

            if start_seconds_of_segment <= seconds < end_seconds_of_segment:
                target_segment_index = i
                time_in_segment_ms = int((seconds - start_seconds_of_segment) * 1000)
                break
        
        if target_segment_index != -1:
            if self.current_segment_index != target_segment_index:
                self.pending_seek_ms = time_in_segment_ms
                self.play_segment(target_segment_index)
            else:
                self.player.setPosition(time_in_segment_ms)
            if not self.is_playing:
                self.pause()
    
    def set_volume(self, volume: int):
        """Set volume (0-100)."""
        if self.audio_output:
            self.audio_output.setVolume(volume / 100.0)
    
    def set_playback_rate(self, rate: float):
        """Set playback rate."""
        if self.player:
            self.player.setPlaybackRate(rate)

    def get_current_time_seconds(self) -> float:
        """Get current playback time in seconds from start of day."""
        if self.current_segment_index < 0:
            return 0.0
        current_segment = self.current_playlist[self.current_segment_index]
        segment_start_dt = current_segment.start_time
        
        # Calculate the absolute datetime of the current frame
        current_frame_dt = segment_start_dt + timedelta(milliseconds=self.player.position())
        
        # Convert that datetime to total seconds from midnight of that day
        time_of_day = current_frame_dt.time()
        total_seconds = (time_of_day.hour * 3600) + (time_of_day.minute * 60) + time_of_day.second + (time_of_day.microsecond / 1_000_000)
        return total_seconds
    
    def _emit_position_changed(self, position_ms):
        current_total_seconds = self.get_current_time_seconds()
        self.position_changed.emit(current_total_seconds)

    def on_playback_state_changed(self, state: QMediaPlayer.PlaybackState):
        """Handle playback state changes."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.is_playing = True
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.is_playing = False
        # When media ends, state becomes StoppedState. We do not update is_playing here.
        # This prevents a race condition where is_playing is set to False before
        # on_media_status_changed can check it to advance to the next segment.

    def on_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        """Handle media status changes, e.g., for playlists."""
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            if self.pending_seek_ms >= 0:
                self.player.setPosition(self.pending_seek_ms)
                self.pending_seek_ms = -1
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.is_playing and self.current_segment_index < len(self.current_playlist) - 1:
                self.play_segment(self.current_segment_index + 1)
            else:
                self.stop()

    def on_player_error(self, error, error_string):
        """Handle player errors."""
        print(f"Player Error: {error_string}")
    
    def cleanup(self):
        """Clean up multimedia resources."""
        if self.player:
            self.player.stop()
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        # QVideoWidget handles resizing automatically
