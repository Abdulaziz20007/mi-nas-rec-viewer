"""
Camera player view combining video player, calendar, and timeline.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMenu,
                             QPushButton, QLabel, QFrame, QScrollArea,
                             QLineEdit, QSpinBox, QTimeEdit, QGroupBox, QSlider, QStyle)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QTime
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtGui import QFont, QAction
from typing import List, Optional
from datetime import datetime, date, time, timedelta

from models import Camera, RecordingDay, VideoSegment
from video_player import VideoPlayerWidget
from calendar_widget import RecordingCalendarWidget
from timeline_widget import TimelineWidget


class CameraPlayerView(QWidget):
    """Main camera player view with video, calendar, and timeline."""
    
    # Signals
    back_to_dashboard = pyqtSignal()
    camera_switched = pyqtSignal(Camera)
    
    def __init__(self):
        super().__init__()
        
        # State
        self.cameras: List[Camera] = []
        self.current_camera: Optional[Camera] = None
        self.current_date: Optional[date] = None
        self.current_recording_day: Optional[RecordingDay] = None
        
        # UI Components
        self.video_player: Optional[VideoPlayerWidget] = None
        self.calendar_widget: Optional[RecordingCalendarWidget] = None
        self.timeline_widget: Optional[TimelineWidget] = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the camera player UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left sidebar
        sidebar = self.create_sidebar()
        splitter.addWidget(sidebar)
        
        # Main content area
        main_content = self.create_main_content()
        splitter.addWidget(main_content)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 0)  # Sidebar fixed width
        splitter.setStretchFactor(1, 1)  # Main content expandable
        splitter.setSizes([300, 800])
    
    def create_sidebar(self) -> QWidget:
        """Create the left sidebar with calendar and camera buttons."""
        sidebar = QFrame()
        sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Back button
        back_button = QPushButton(" Back to Dashboard")
        back_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.back_to_dashboard.emit)
        layout.addWidget(back_button)
        
        # Current camera info
        self.camera_info_label = QLabel("No camera selected")
        camera_font = QFont()
        camera_font.setPointSize(12)
        camera_font.setBold(True)
        self.camera_info_label.setFont(camera_font)
        self.camera_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.camera_info_label)
        
        # Calendar widget
        self.calendar_widget = RecordingCalendarWidget()
        self.calendar_widget.date_selected.connect(self.on_date_selected)
        layout.addWidget(self.calendar_widget)
        
        # Camera switcher
        self.create_camera_switcher(layout)
        
        layout.addStretch()
        return sidebar
    
    def create_camera_switcher(self, layout: QVBoxLayout):
        """Create camera switcher buttons."""
        # Camera switcher group
        camera_group = QGroupBox("Switch Camera")
        
        camera_layout = QVBoxLayout(camera_group)
        
        # Scroll area for camera buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMaximumHeight(200)
        
        self.camera_buttons_widget = QWidget()
        self.camera_buttons_layout = QVBoxLayout(self.camera_buttons_widget)
        self.camera_buttons_layout.setSpacing(5)
        
        scroll_area.setWidget(self.camera_buttons_widget)
        camera_layout.addWidget(scroll_area)
        
        layout.addWidget(camera_group)
    
    def create_main_content(self) -> QWidget:
        """Create the main content area with video player and timeline."""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video player
        self.video_player = VideoPlayerWidget()
        self.video_player.position_changed.connect(self.on_video_position_changed)
        self.video_player.player.playbackStateChanged.connect(self.update_play_button)
        layout.addWidget(self.video_player)
        
        # Timeline and controls section
        timeline_section = self.create_timeline_section()
        layout.addWidget(timeline_section)
        
        return main_widget
    
    def create_timeline_section(self) -> QWidget:
        """Create the timeline section with 24-hour view and controls."""
        section = QFrame()
        section.setFrameStyle(QFrame.Shape.StyledPanel)
        section.setObjectName("timelineSection")
        section.setFixedHeight(180)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Timeline widget
        self.timeline_widget = TimelineWidget()
        self.timeline_widget.time_clicked.connect(self.on_timeline_clicked)
        self.timeline_widget.playhead_moved.connect(self.on_timeline_seek)
        layout.addWidget(self.timeline_widget)
        
        # Player controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.setFixedSize(40, 40)
        self.play_button.clicked.connect(self.video_player.toggle_play_pause)
        controls_layout.addWidget(self.play_button)

        controls_layout.addStretch(1)

        # Speed control
        self.speed_button = QPushButton("1.0x")
        self.speed_button.setFixedWidth(70)
        self.speed_button.setToolTip("Playback Speed")
        speed_menu = QMenu(self)
        self.playback_rates = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
        for rate in self.playback_rates:
            action = QAction(f"{rate}x", self)
            action.setData(rate)
            action.triggered.connect(self.set_playback_speed)
            speed_menu.addAction(action)
        self.speed_button.setMenu(speed_menu)
        controls_layout.addWidget(self.speed_button)

        volume_icon_label = QLabel()
        volume_icon_label.setPixmap(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume).pixmap(20, 20))
        volume_icon_label.setObjectName("volumeIcon")
        controls_layout.addWidget(volume_icon_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.setFixedWidth(120)
        self.volume_slider.valueChanged.connect(self.video_player.set_volume)
        controls_layout.addWidget(self.volume_slider)
        
        layout.addLayout(controls_layout)
        
        return section
    
    def set_cameras(self, cameras: List[Camera]):
        """Set the list of available cameras."""
        self.cameras = cameras
        self.update_camera_buttons()
    
    def update_camera_buttons(self):
        """Update the camera switcher buttons."""
        # Clear existing buttons
        for i in reversed(range(self.camera_buttons_layout.count())):
            child = self.camera_buttons_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add buttons for each camera
        for camera in self.cameras:
            btn = QPushButton(camera.name)
            btn.setObjectName("cameraSwitchButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, cam=camera: self.switch_to_camera(cam))
            self.camera_buttons_layout.addWidget(btn)
        
        self.camera_buttons_layout.addStretch()
    
    def set_current_camera(self, camera: Camera):
        """Set the current camera and load its data."""
        self.current_camera = camera
        self.camera_info_label.setText(f"Camera: {camera.name}")
        
        # Update calendar
        self.calendar_widget.set_camera(camera)
        
        # Update camera button states
        for i in range(self.camera_buttons_layout.count()):
            item = self.camera_buttons_layout.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                if isinstance(btn, QPushButton):
                    btn.setChecked(btn.text() == camera.name)
        
        # Load latest recording day if available
        if camera.latest_recording_date:
            self.load_recording_day(camera.latest_recording_date)
    
    def switch_to_camera(self, camera: Camera):
        """Switch to a different camera."""
        if camera != self.current_camera:
            self.set_current_camera(camera)
            self.camera_switched.emit(camera)
    
    def on_date_selected(self, selected_date: date):
        """Handle date selection from calendar."""
        self.load_recording_day(selected_date)
    
    def load_recording_day(self, target_date: date):
        """Load recordings for a specific date."""
        if not self.current_camera:
            return
        
        self.current_date = target_date
        self.current_recording_day = self.current_camera.get_recording_day(target_date)
        
        if self.current_recording_day:
            # Update timeline
            self.timeline_widget.set_recording_day(self.current_recording_day)
            
            # Load videos into player
            self.video_player.load_playlist(self.current_recording_day.video_segments)
            
            # Set calendar selection
            self.calendar_widget.set_selected_date(target_date)
            
            # Reset speed to 1.0x
            self.video_player.set_playback_rate(1.0)
            self.speed_button.setText("1.0x")
        else:
            # No recordings for this date
            self.timeline_widget.clear_timeline()
            self.video_player.load_playlist([])
    
    def on_timeline_clicked(self, seconds: float):
        """Handle timeline click to seek video."""
        self.video_player.seek_to_time(seconds)
        self.timeline_widget.set_playhead_position(seconds)
    
    def on_timeline_seek(self, seconds: float):
        """Handle timeline scrubbing."""
        self.video_player.seek_to_time(seconds)
    
    def on_video_position_changed(self, seconds: float):
        """Handle video position changes to update timeline."""
        if self.timeline_widget and not self.timeline_widget.dragging_playhead:
            self.timeline_widget.set_playhead_position(seconds)
    
    def set_playback_speed(self):
        """Set the playback speed from the speed menu."""
        action = self.sender()
        if isinstance(action, QAction):
            rate = action.data()
            if self.video_player:
                self.video_player.set_playback_rate(rate)
                self.speed_button.setText(f"{rate}x")

    def apply_theme(self, theme_dict: dict):
        """Apply theme to child widgets that need it."""
        self.calendar_widget.apply_theme(theme_dict)
        self.timeline_widget.apply_theme(theme_dict)


    def jump_to_hour(self, hour: int):
        """Jump to a specific hour (placeholder, can be re-connected if needed)."""
        target_seconds = hour * 3600
        self.on_timeline_clicked(target_seconds)
    
    def jump_to_time_input(self):
        """Jump to the time specified in the time input (placeholder)."""
        time_value = self.time_edit.time()
        target_seconds = (time_value.hour() * 3600 + 
                         time_value.minute() * 60 + 
                         time_value.second())
        self.on_timeline_clicked(target_seconds)
    
    def update_play_button(self, state: QMediaPlayer.PlaybackState):
        """Update the play/pause button icon based on player state."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    
    def cleanup(self):
        """Clean up resources."""
        if self.video_player:
            self.video_player.cleanup()
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        # Components should handle their own resize
