"""
Core services for the NAS Camera Viewer application.
"""
import json
import os
import pickle
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import re
import threading
from models import Settings, Camera, RecordingDay, VideoSegment


class ConfigService:
    """Singleton service for managing application configuration."""
    
    _instance = None
    _settings_file = "settings.json"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._settings = None
        self._load_settings()
        self._initialized = True
    
    def _load_settings(self) -> None:
        """Load settings from JSON file or create defaults."""
        try:
            if os.path.exists(self._settings_file):
                with open(self._settings_file, 'r') as f:
                    data = json.load(f)
                self._settings = Settings.from_dict(data)
            else:
                self._settings = Settings()
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self._settings = Settings()
    
    def save_settings(self) -> bool:
        """Save current settings to JSON file."""
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    @property
    def settings(self) -> Settings:
        """Get current settings."""
        return self._settings
    
    def update_settings(self, **kwargs) -> bool:
        """Update settings with new values."""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
        return self.save_settings()


class CacheService:
    """Service for caching NAS scan results locally."""
    
    def __init__(self):
        self.cache_file = "nas_cache.pkl"
        self.metadata_file = "cache_metadata.json"
    
    def save_cache(self, cameras: List[Camera]) -> bool:
        """Save camera data to cache file."""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cameras, f)
            
            # Save metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'camera_count': len(cameras),
                'total_days': sum(len(camera.recording_days) for camera in cameras)
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving cache: {e}")
            return False
    
    def load_cache(self) -> Optional[List[Camera]]:
        """Load camera data from cache file."""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'rb') as f:
                cameras = pickle.load(f)
            
            return cameras
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None
    
    def is_cache_valid(self, max_age_hours: int = 24) -> bool:
        """Check if cache is valid based on age."""
        try:
            if not os.path.exists(self.metadata_file):
                return False
            
            with open(self.metadata_file, 'r') as f:
                metadata = json.load(f)
            
            cache_time = datetime.fromisoformat(metadata['timestamp'])
            age = datetime.now() - cache_time
            
            return age < timedelta(hours=max_age_hours)
        except Exception as e:
            print(f"Error checking cache validity: {e}")
            return False
    
    def clear_cache(self) -> bool:
        """Clear cache files."""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False


class NASScannerService:
    """Service for scanning NAS and discovering camera recordings."""
    
    def __init__(self):
        self.config_service = ConfigService()
        self.cache_service = CacheService()
        self._scanning = False
        self._scan_thread = None
        self._progress_callback = None
        self._complete_callback = None
    
    def scan_async(self, progress_callback=None, complete_callback=None) -> None:
        """Start asynchronous scan of NAS."""
        if self._scanning:
            return
        
        self._progress_callback = progress_callback
        self._complete_callback = complete_callback
        self._scanning = True
        
        self._scan_thread = threading.Thread(target=self._scan_worker)
        self._scan_thread.daemon = True
        self._scan_thread.start()
    
    def _scan_worker(self) -> None:
        """Worker thread for scanning NAS."""
        try:
            cameras = self._scan_nas()
            self.cache_service.save_cache(cameras)
            
            if self._complete_callback:
                self._complete_callback(cameras, None)
        except Exception as e:
            if self._complete_callback:
                self._complete_callback(None, str(e))
        finally:
            self._scanning = False
    
    def _scan_nas(self) -> List[Camera]:
        """Scan NAS for camera recordings."""
        settings = self.config_service.settings
        cameras = []
        
        if self._progress_callback:
            self._progress_callback("Connecting to NAS...")
        
        nas_path = settings.full_nas_path
        
        # Check if NAS path exists
        if not os.path.exists(nas_path):
            raise Exception(f"NAS path not accessible: {nas_path}")
        
        if self._progress_callback:
            self._progress_callback("Scanning camera folders...")
        
        # Scan for camera folders
        try:
            camera_folders = [f for f in os.listdir(nas_path) 
                            if os.path.isdir(os.path.join(nas_path, f))]
        except Exception as e:
            raise Exception(f"Unable to list camera folders: {e}")
        
        for i, camera_id in enumerate(camera_folders):
            if self._progress_callback:
                self._progress_callback(f"Scanning camera {camera_id} ({i+1}/{len(camera_folders)})...")
            
            camera_path = os.path.join(nas_path, camera_id)
            camera = self._scan_camera(camera_id, camera_path)
            if camera.has_recordings:
                cameras.append(camera)
        
        return cameras
    
    def _scan_camera(self, camera_id: str, camera_path: str) -> Camera:
        """Scan a single camera folder for recordings."""
        recording_days = []
        
        try:
            # Get all date folders in camera directory
            date_folders = [f for f in os.listdir(camera_path) 
                          if os.path.isdir(os.path.join(camera_path, f)) and self._is_date_folder(f)]
            
            # Group folders by date (handle multiple folders per day)
            date_groups = self._group_folders_by_date(date_folders)
            
            for date_str, folders in date_groups.items():
                try:
                    target_date = self._parse_date(date_str)
                    video_segments = []
                    
                    # Scan all folders for this date
                    for folder in folders:
                        folder_path = os.path.join(camera_path, folder)
                        hour = int(folder[8:10])
                        segments = self._scan_date_folder(folder_path, target_date, hour)
                        video_segments.extend(segments)

                    if video_segments:
                        recording_day = RecordingDay(date=target_date, video_segments=video_segments)
                        recording_days.append(recording_day)

                except Exception as e:
                    print(f"Error scanning date folder {date_str}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scanning camera {camera_id}: {e}")
        
        return Camera(
            camera_id=camera_id,
            name=camera_id,  # Use camera_id as display name for now
            nas_path=camera_path,
            recording_days=recording_days
        )
    
    def _scan_date_folder(self, folder_path: str, target_date: date, hour: int) -> List[VideoSegment]:
        """Scan a date folder for video files."""
        video_segments = []
        
        try:
            video_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith('.mp4')]
            
            for video_file in video_files:
                try:
                    video_path = os.path.join(folder_path, video_file)
                    start_time = self._parse_video_filename(video_file, target_date, hour)
                    
                    if start_time:
                        segment = VideoSegment(
                            path=video_path,
                            start_time=start_time,
                            duration=60  # Assume 1-minute videos
                        )
                        video_segments.append(segment)
                
                except Exception as e:
                    print(f"Error parsing video file {video_file}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scanning folder {folder_path}: {e}")
        
        return video_segments
    
    def _is_date_folder(self, folder_name: str) -> bool:
        """Check if folder name represents a date (YYYYMMDDHH format)."""
        return re.match(r'^\d{10}$', folder_name) is not None
    
    def _group_folders_by_date(self, folders: List[str]) -> Dict[str, List[str]]:
        """Group date folders by date (YYYYMMDD), handling multiple folders per day."""
        groups = {}
        for folder in folders:
            if len(folder) >= 8:
                date_part = folder[:8]  # YYYYMMDD
                if date_part not in groups:
                    groups[date_part] = []
                groups[date_part].append(folder)
        return groups
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in YYYYMMDD format."""
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        return date(year, month, day)
    
    def _parse_video_filename(self, filename: str, target_date: date, hour: int) -> Optional[datetime]:
        """Parse video filename to extract start time from filename components."""
        # Expected format: 00M03S_1756195203.mp4
        from datetime import time
        match = re.match(r'(\d{2})M(\d{2})S_.*', filename)
        if not match:
            return None
        
        try:
            minute = int(match.group(1))
            second = int(match.group(2))
            
            # Construct datetime from folder/file parts
            return datetime.combine(target_date, time(hour=hour, minute=minute, second=second))
                
        except ValueError as e:
            print(f"Error parsing time from filename {filename}: {e}")
            return None
    
    @property
    def is_scanning(self) -> bool:
        """Check if scan is currently in progress."""
        return self._scanning
    
    def get_cached_cameras(self) -> Optional[List[Camera]]:
        """Get cameras from cache if available and valid."""
        if self.cache_service.is_cache_valid(self.config_service.settings.cache_max_age_hours):
            return self.cache_service.load_cache()
        return None
