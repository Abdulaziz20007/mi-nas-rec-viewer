"""
Dashboard view for displaying camera cards.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QScrollArea,
                             QProgressBar, QSizePolicy, QStyle)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette
from typing import List, Optional
from datetime import date

from models import Camera


class CameraCard(QFrame):
    """Widget representing a single camera as a card."""
    
    clicked = pyqtSignal(Camera)
    
    def __init__(self, camera: Camera):
        super().__init__()
        self.camera = camera
        self.setup_ui()
        self.setObjectName("CameraCard")
        self.setFixedSize(300, 220)
    
    def setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Camera name/ID
        name_label = QLabel(self.camera.name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Camera info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        # Total recording days
        days_label = QLabel(f"Recording days: {self.camera.total_recording_days}")
        days_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(days_label)
        
        # Latest recording date
        if self.camera.latest_recording_date:
            latest_label = QLabel(f"Latest: {self.camera.latest_recording_date.strftime('%Y-%m-%d')}")
            latest_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(latest_label)
        else:
            no_data_label = QLabel("No recordings found")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setObjectName("mutedText")
            info_layout.addWidget(no_data_label)
        
        layout.addLayout(info_layout)
        
        # Status indicator
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame); status_layout.setContentsMargins(0,0,0,0)
        
        status_dot = QLabel("●")
        status_dot.setProperty("status", "active" if self.camera.has_recordings else "inactive")
        status_text = QLabel("Active" if self.camera.has_recordings else "No Data")
        status_text.setProperty("status", "active" if self.camera.has_recordings else "inactive")
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        layout.addWidget(status_frame)
        layout.addStretch()
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.camera)
        super().mousePressEvent(event)


class DashboardView(QWidget):
    """Main dashboard view showing camera cards."""
    
    camera_selected = pyqtSignal(Camera)
    
    def __init__(self):
        super().__init__()
        self.cameras: List[Camera] = []
        self.camera_cards: List[CameraCard] = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Camera Dashboard")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Select a camera to view recordings")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setObjectName("mutedText")
        header_layout.addWidget(subtitle_label)
        
        layout.addLayout(header_layout)
        
        # Loading indicator
        self.loading_frame = QFrame()
        loading_layout = QVBoxLayout(self.loading_frame)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setFixedWidth(300)
        loading_layout.addWidget(self.progress_bar)
        
        loading_label = QLabel("Scanning NAS for cameras...")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_layout.addWidget(loading_label)
        
        layout.addWidget(self.loading_frame)
        self.loading_frame.hide()
        
        # Scroll area for camera cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container for camera cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.cards_container)
        layout.addWidget(scroll_area)
        
        # Empty state
        self.empty_state_frame = QFrame()
        empty_layout = QVBoxLayout(self.empty_state_frame)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        empty_icon = QLabel()
        empty_icon.setPixmap(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon).pixmap(48, 48))
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_icon)
        
        empty_title = QLabel("No Cameras Found")
        empty_title_font = QFont()
        empty_title_font.setPointSize(18)
        empty_title_font.setBold(True)
        empty_title.setFont(empty_title_font)
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_title)
        
        empty_message = QLabel("Check your NAS connection and settings")
        empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_message.setObjectName("mutedText")
        empty_layout.addWidget(empty_message)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedWidth(120)
        refresh_btn.clicked.connect(self.request_refresh)
        empty_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.empty_state_frame)
        self.empty_state_frame.hide()
    
    def set_cameras(self, cameras: List[Camera]):
        """Update the dashboard with a new list of cameras."""
        self.cameras = cameras
        self.update_cards()
    
    def update_cards(self):
        """Update the camera cards display."""
        # Clear existing cards
        for card in self.camera_cards:
            card.setParent(None)
        self.camera_cards.clear()
        
        # Show/hide empty state
        if not self.cameras:
            self.cards_container.hide()
            self.empty_state_frame.show()
            return
        
        self.empty_state_frame.hide()
        self.cards_container.show()
        
        # Create new cards
        columns = max(1, self.width() // 320)  # Calculate columns based on width
        
        for i, camera in enumerate(self.cameras):
            card = CameraCard(camera)
            card.clicked.connect(self.on_camera_clicked)
            
            row = i // columns
            col = i % columns
            self.cards_layout.addWidget(card, row, col)
            self.camera_cards.append(card)
    
    def on_camera_clicked(self, camera: Camera):
        """Handle camera card click."""
        self.camera_selected.emit(camera)
    
    def set_loading(self, loading: bool):
        """Show/hide loading indicator."""
        if loading:
            self.cards_container.hide()
            self.empty_state_frame.hide()
            self.loading_frame.show()
        else:
            self.loading_frame.hide()
            if self.cameras:
                self.cards_container.show()
            else:
                self.empty_state_frame.show()
    
    def request_refresh(self):
        """Request a refresh of camera data."""
        # This would typically emit a signal to the main window
        # For now, we'll just show loading state
        self.set_loading(True)
    
    def resizeEvent(self, event):
        """Handle window resize to adjust card layout."""
        super().resizeEvent(event)
        if self.cameras:
            # Delay the update to avoid too many rapid updates
            QTimer.singleShot(100, self.update_cards)
