"""
Main application window for the NAS Camera Viewer.
"""
from PyQt6.QtWidgets import (QMainWindow, QStackedWidget, QVBoxLayout, QApplication,
                            QWidget, QStatusBar, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from typing import List, Optional

from models import Camera
from services import ConfigService, NASScannerService
from dashboard_view import DashboardView
from camera_player_view import CameraPlayerView
from settings_view import SettingsView


class MainWindow(QMainWindow):
    """Main application window with navigation between views."""
    
    def __init__(self):
        super().__init__()
        
        # Services
        self.config_service = ConfigService()
        self.nas_scanner = NASScannerService()
        
        # Data
        self.cameras: List[Camera] = []
        
        # UI Setup
        self.setWindowTitle("NAS Camera Viewer")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self.setup_status_bar()  # Create status bar first
        self.setup_ui()
        self.setup_menu_bar()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        
        # Load initial data
        self.load_cameras()
    
    def setup_ui(self):
        """Setup the main UI components."""
        # Central widget with stacked layout for different views
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for view switching
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create views
        self.dashboard_view = DashboardView()
        self.camera_player_view = CameraPlayerView()
        self.settings_view = SettingsView()
        
        # Add views to stack
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.camera_player_view)
        self.stacked_widget.addWidget(self.settings_view)
        
        # Connect signals
        self.dashboard_view.camera_selected.connect(self.open_camera_player)
        self.camera_player_view.back_to_dashboard.connect(self.show_dashboard)
        self.camera_player_view.camera_switched.connect(self.switch_camera)
        self.settings_view.settings_saved.connect(self.on_settings_saved)
        self.settings_view.back_to_dashboard.connect(self.show_dashboard)
        
        # Show dashboard initially
        self.show_dashboard()
    
    def setup_menu_bar(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        refresh_action = QAction('Refresh Cameras', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_cameras)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction('Settings', self)
        settings_action.setShortcut('Ctrl+S')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        dashboard_action = QAction('Dashboard', self)
        dashboard_action.setShortcut('Ctrl+D')
        dashboard_action.triggered.connect(self.show_dashboard)
        view_menu.addAction(dashboard_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def load_cameras(self):
        """Load cameras from cache or trigger scan."""
        # Try to load from cache first
        cached_cameras = self.nas_scanner.get_cached_cameras()
        
        if cached_cameras is not None:
            self.cameras = cached_cameras
            self.dashboard_view.set_cameras(self.cameras)
            self.camera_player_view.set_cameras(self.cameras)
            self.status_bar.showMessage(f"Loaded {len(self.cameras)} cameras from cache")
            
            # Start auto-refresh timer
            self.start_auto_refresh()
        else:
            # No cache, start scan immediately
            self.refresh_cameras()
    
    def refresh_cameras(self):
        """Refresh camera list from NAS."""
        if self.nas_scanner.is_scanning:
            return
        
        self.status_bar.showMessage("Scanning NAS for cameras...")
        self.dashboard_view.set_loading(True)
        
        self.nas_scanner.scan_async(
            progress_callback=self.on_scan_progress,
            complete_callback=self.on_scan_complete
        )
    
    def on_scan_progress(self, message: str):
        """Handle scan progress updates."""
        self.status_bar.showMessage(message)
    
    def on_scan_complete(self, cameras: Optional[List[Camera]], error: Optional[str]):
        """Handle scan completion."""
        self.dashboard_view.set_loading(False)
        
        if error:
            self.status_bar.showMessage(f"Scan failed: {error}")
            QMessageBox.warning(self, "Scan Error", f"Failed to scan NAS:\n{error}")
        else:
            self.cameras = cameras or []
            self.dashboard_view.set_cameras(self.cameras)
            self.camera_player_view.set_cameras(self.cameras)
            self.status_bar.showMessage(f"Found {len(self.cameras)} cameras")
            
            # Start auto-refresh timer
            self.start_auto_refresh()
    
    def start_auto_refresh(self):
        """Start the auto-refresh timer."""
        interval_minutes = self.config_service.settings.auto_refresh_interval_minutes
        if interval_minutes > 0:
            self.refresh_timer.start(interval_minutes * 60 * 1000)  # Convert to milliseconds
    
    def auto_refresh(self):
        """Perform automatic refresh."""
        if not self.nas_scanner.is_scanning:
            self.refresh_cameras()
    
    def show_dashboard(self):
        """Show the dashboard view."""
        self.stacked_widget.setCurrentWidget(self.dashboard_view)
        self.status_bar.showMessage(f"Dashboard - {len(self.cameras)} cameras")
    
    def show_settings(self):
        """Show the settings view."""
        self.settings_view.load_settings()
        self.stacked_widget.setCurrentWidget(self.settings_view)
        self.status_bar.showMessage("Settings")
    
    def open_camera_player(self, camera: Camera):
        """Open camera player for the selected camera."""
        self.camera_player_view.set_current_camera(camera)
        self.stacked_widget.setCurrentWidget(self.camera_player_view)
        self.status_bar.showMessage(f"Viewing camera: {camera.name}")
    
    def switch_camera(self, camera: Camera):
        """Switch to a different camera in the player view."""
        self.camera_player_view.set_current_camera(camera)
        self.status_bar.showMessage(f"Switched to camera: {camera.name}")
    
    def on_settings_saved(self):
        """Handle settings save event."""
        self.status_bar.showMessage("Settings saved")
        # Restart auto-refresh timer with new interval
        self.refresh_timer.stop()
        self.start_auto_refresh()
        # Re-apply theme in case it was changed
        if QApplication.instance():
            QApplication.instance().apply_theme()

    def apply_theme(self, theme_dict: dict):
        """Propagate theme changes to child widgets."""
        self.camera_player_view.apply_theme(theme_dict)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About NAS Camera Viewer",
            "NAS Camera Viewer v1.0\n\n"
            "A desktop application for viewing camera recordings\n"
            "stored on Network Attached Storage (NAS) devices.\n\n"
            "Built with PyQt6."
        )
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop timers
        self.refresh_timer.stop()
        
        # Clean up resources
        self.camera_player_view.cleanup()
        
        event.accept()
