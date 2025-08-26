"""
Data models for the NAS Camera Viewer application.
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional
import os


@dataclass
class VideoSegment:
    """Represents a single 1-minute video file."""
    path: str
    start_time: datetime
    duration: int = 60  # seconds
    
    @property
    def filename(self) -> str:
        return os.path.basename(self.path)
    
    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)


@dataclass
class RecordingDay:
    """Represents a single day of recordings."""
    date: date
    video_segments: List[VideoSegment]
    
    def __post_init__(self):
        # Sort video segments by start time
        self.video_segments.sort(key=lambda x: x.start_time)
    
    @property
    def has_recordings(self) -> bool:
        return len(self.video_segments) > 0
    
    @property
    def total_duration(self) -> int:
        """Total recording duration in seconds."""
        return sum(segment.duration for segment in self.video_segments)
    
    @property
    def recording_hours(self) -> List[int]:
        """Returns list of hours (0-23) that have recordings."""
        hours = set()
        for segment in self.video_segments:
            hours.add(segment.start_time.hour)
        return sorted(list(hours))
    
    def get_segments_for_hour(self, hour: int) -> List[VideoSegment]:
        """Get all video segments for a specific hour."""
        return [seg for seg in self.video_segments if seg.start_time.hour == hour]
    
    def get_segment_at_time(self, target_time: datetime) -> Optional[VideoSegment]:
        """Find the video segment that should be playing at the given time."""
        for segment in self.video_segments:
            segment_end = segment.start_time.replace(
                second=segment.start_time.second + segment.duration
            )
            if segment.start_time <= target_time < segment_end:
                return segment
        return None


@dataclass
class Camera:
    """Represents a single camera with its recordings."""
    camera_id: str
    name: str
    nas_path: str
    recording_days: List[RecordingDay]
    
    def __post_init__(self):
        # Sort recording days by date
        self.recording_days.sort(key=lambda x: x.date, reverse=True)
    
    @property
    def has_recordings(self) -> bool:
        return any(day.has_recordings for day in self.recording_days)
    
    @property
    def latest_recording_date(self) -> Optional[date]:
        """Returns the latest date with recordings."""
        for day in self.recording_days:
            if day.has_recordings:
                return day.date
        return None
    
    @property
    def total_recording_days(self) -> int:
        """Count of days with recordings."""
        return sum(1 for day in self.recording_days if day.has_recordings)
    
    def get_recording_day(self, target_date: date) -> Optional[RecordingDay]:
        """Get recordings for a specific date."""
        for day in self.recording_days:
            if day.date == target_date:
                return day
        return None
    
    def get_available_dates(self) -> List[date]:
        """Returns list of dates that have recordings."""
        return [day.date for day in self.recording_days if day.has_recordings]


@dataclass
class Settings:
    """Application configuration settings."""
    nas_path: str = "\\\\OPENMEDIAVAULT"
    shared_folder: str = "test"
    camera_default_folder: str = "xiaomi_camera_videos"
    username: str = ""
    password: str = ""
    cache_enabled: bool = True
    cache_max_age_hours: int = 24
    auto_refresh_interval_minutes: int = 30
    theme: str = "light"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'nas_path': self.nas_path,
            'shared_folder': self.shared_folder,
            'camera_default_folder': self.camera_default_folder,
            'username': self.username,
            'password': self.password,
            'cache_enabled': self.cache_enabled,
            'cache_max_age_hours': self.cache_max_age_hours,
            'auto_refresh_interval_minutes': self.auto_refresh_interval_minutes,
            'theme': self.theme
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Settings':
        """Create Settings instance from dictionary."""
        return cls(
            nas_path=data.get('nas_path', '\\\\OPENMEDIAVAULT'),
            shared_folder=data.get('shared_folder', 'test'),
            camera_default_folder=data.get('camera_default_folder', 'xiaomi_camera_videos'),
            username=data.get('username', ''),
            password=data.get('password', ''),
            cache_enabled=data.get('cache_enabled', True),
            cache_max_age_hours=data.get('cache_max_age_hours', 24),
            auto_refresh_interval_minutes=data.get('auto_refresh_interval_minutes', 30),
            theme=data.get('theme', 'light')
        )
    
    @property
    def full_nas_path(self) -> str:
        """Complete path to the camera folders."""
        return os.path.join(self.nas_path, self.shared_folder, self.camera_default_folder)
