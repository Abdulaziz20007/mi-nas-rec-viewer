"""
Settings view for configuring application settings.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox,
                            QLabel, QLineEdit, QPushButton, QSpinBox, 
                            QCheckBox, QGroupBox, QFrame, QMessageBox,
                            QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from typing import Optional

from services import ConfigService, NASScannerService


class SettingsView(QWidget):
    """Settings view for application configuration."""
    
    # Signals
    settings_saved = pyqtSignal()
    back_to_dashboard = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Services
        self.config_service = ConfigService()
        self.nas_scanner = NASScannerService()
        
        # UI state
        self.testing_connection = False
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # NAS Configuration
        self.create_nas_config_section(layout)
        
        # Cache Configuration
        self.create_cache_config_section(layout)
        
        # Application Settings
        self.create_app_settings_section(layout)
        
        # Connection Test
        self.create_connection_test_section(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
        
        layout.addStretch()
    
    def create_header(self, layout: QVBoxLayout):
        """Create the header section."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        # Title
        title_label = QLabel("Application Settings")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Configure NAS connection and application preferences")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def create_nas_config_section(self, layout: QVBoxLayout):
        """Create NAS configuration section."""
        nas_group = QGroupBox("NAS Configuration")
        
        grid_layout = QGridLayout(nas_group)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(15, 20, 15, 15)
        
        # NAS Path
        grid_layout.addWidget(QLabel("NAS Path:"), 0, 0)
        self.nas_path_edit = QLineEdit()
        self.nas_path_edit.setPlaceholderText("\\\\SERVER or \\\\192.168.1.100")
        grid_layout.addWidget(self.nas_path_edit, 0, 1)
        
        # Shared Folder
        grid_layout.addWidget(QLabel("Shared Folder:"), 1, 0)
        self.shared_folder_edit = QLineEdit()
        self.shared_folder_edit.setPlaceholderText("test")

        grid_layout.addWidget(self.shared_folder_edit, 1, 1)
        
        # Camera Default Folder
        grid_layout.addWidget(QLabel("Camera Folder:"), 2, 0)
        self.camera_folder_edit = QLineEdit()
        self.camera_folder_edit.setPlaceholderText("xiaomi_camera_videos")

        grid_layout.addWidget(self.camera_folder_edit, 2, 1)
        
        # Username (optional)
        grid_layout.addWidget(QLabel("Username:"), 3, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Optional - leave blank if no authentication")

        grid_layout.addWidget(self.username_edit, 3, 1)
        
        # Password (optional)
        grid_layout.addWidget(QLabel("Password:"), 4, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Optional")
        grid_layout.addWidget(self.password_edit, 4, 1)
        
        layout.addWidget(nas_group)
    
    def create_cache_config_section(self, layout: QVBoxLayout):
        """Create cache configuration section."""
        cache_group = QGroupBox("Cache Configuration")
        
        grid_layout = QGridLayout(cache_group)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(15, 20, 15, 15)
        
        # Enable Cache
        self.cache_enabled_checkbox = QCheckBox("Enable caching")
        grid_layout.addWidget(self.cache_enabled_checkbox, 0, 0, 1, 2)
        
        # Cache Max Age
        grid_layout.addWidget(QLabel("Cache max age (hours):"), 1, 0)
        self.cache_max_age_spinbox = QSpinBox()
        self.cache_max_age_spinbox.setRange(1, 168)  # 1 hour to 1 week
        self.cache_max_age_spinbox.setValue(24)

        grid_layout.addWidget(self.cache_max_age_spinbox, 1, 1)
        
        layout.addWidget(cache_group)
    
    def create_app_settings_section(self, layout: QVBoxLayout):
        """Create application settings section."""
        app_group = QGroupBox("Application Configuration")
        
        grid_layout = QGridLayout(app_group)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(15, 20, 15, 15)
        
        # Auto-refresh interval
        grid_layout.addWidget(QLabel("Auto-refresh interval (minutes):"), 0, 0)
        self.auto_refresh_spinbox = QSpinBox()
        self.auto_refresh_spinbox.setRange(0, 1440)  # 0 (disabled) to 24 hours
        self.auto_refresh_spinbox.setValue(30)
        self.auto_refresh_spinbox.setSpecialValueText("Disabled")

        grid_layout.addWidget(self.auto_refresh_spinbox, 0, 1)

        # Theme
        grid_layout.addWidget(QLabel("Theme:"), 1, 0)
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItem("Light", "light")
        self.theme_combobox.addItem("Dark", "dark")
        grid_layout.addWidget(self.theme_combobox, 1, 1)
        
        layout.addWidget(app_group)
    
    def create_connection_test_section(self, layout: QVBoxLayout):
        """Create connection test section."""
        test_group = QGroupBox("Test Connection")
        
        test_layout = QVBoxLayout(test_group)
        test_layout.setContentsMargins(15, 20, 15, 15)
        test_layout.setSpacing(10)
        
        # Test button
        button_layout = QHBoxLayout()
        self.test_button = QPushButton("Test NAS Connection")
        self.test_button.setObjectName("testButton")
        self.test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        
        test_layout.addLayout(button_layout)
        
        # Progress bar
        self.test_progress = QProgressBar()
        self.test_progress.setRange(0, 0)  # Indeterminate
        self.test_progress.hide()
        test_layout.addWidget(self.test_progress)
        
        # Test results
        self.test_results = QTextEdit()
        self.test_results.setMaximumHeight(100)
        self.test_results.setReadOnly(True)
        self.test_results.hide()
        test_layout.addWidget(self.test_results)
        
        layout.addWidget(test_group)
    
    def create_action_buttons(self, layout: QVBoxLayout):
        """Create action buttons."""
        button_layout = QHBoxLayout()
        
        # Back button
        back_button = QPushButton("Back to Dashboard")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.back_to_dashboard.emit)
        button_layout.addWidget(back_button)
        
        button_layout.addStretch()
        
        # Reset button
        reset_button = QPushButton("Reset Defaults")
        reset_button.setObjectName("resetButton")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.setObjectName("saveButton")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """Load current settings into the form."""
        settings = self.config_service.settings
        
        self.nas_path_edit.setText(settings.nas_path)
        self.shared_folder_edit.setText(settings.shared_folder)
        self.camera_folder_edit.setText(settings.camera_default_folder)
        self.username_edit.setText(settings.username)
        self.password_edit.setText(settings.password)
        
        self.cache_enabled_checkbox.setChecked(settings.cache_enabled)
        self.cache_max_age_spinbox.setValue(settings.cache_max_age_hours)
        
        self.auto_refresh_spinbox.setValue(settings.auto_refresh_interval_minutes)

        # Set theme combobox
        index = self.theme_combobox.findData(settings.theme)
        if index != -1:
            self.theme_combobox.setCurrentIndex(index)
    
    def save_settings(self):
        """Save the current form values to settings."""
        try:
            # Validate inputs
            if not self.nas_path_edit.text().strip():
                QMessageBox.warning(self, "Invalid Input", "NAS Path is required.")
                return
            
            if not self.shared_folder_edit.text().strip():
                QMessageBox.warning(self, "Invalid Input", "Shared Folder is required.")
                return
            
            # Update settings
            success = self.config_service.update_settings(
                nas_path=self.nas_path_edit.text().strip(),
                shared_folder=self.shared_folder_edit.text().strip(),
                camera_default_folder=self.camera_folder_edit.text().strip(),
                username=self.username_edit.text().strip(),
                password=self.password_edit.text(),
                cache_enabled=self.cache_enabled_checkbox.isChecked(),
                cache_max_age_hours=self.cache_max_age_spinbox.value(),
                auto_refresh_interval_minutes=self.auto_refresh_spinbox.value(),
                theme=self.theme_combobox.currentData()
            )
            
            if success:
                QMessageBox.information(self, "Settings Saved", 
                                      "Settings have been saved successfully.")
                self.settings_saved.emit()
            else:
                QMessageBox.warning(self, "Save Error", 
                                  "Failed to save settings. Please try again.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving settings:\n{str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Create default settings
            from models import Settings
            default_settings = Settings()
            
            self.nas_path_edit.setText(default_settings.nas_path)
            self.shared_folder_edit.setText(default_settings.shared_folder)
            self.camera_folder_edit.setText(default_settings.camera_default_folder)
            self.username_edit.setText(default_settings.username)
            self.password_edit.setText(default_settings.password)
            
            self.cache_enabled_checkbox.setChecked(default_settings.cache_enabled)
            self.cache_max_age_spinbox.setValue(default_settings.cache_max_age_hours)
            
            self.auto_refresh_spinbox.setValue(default_settings.auto_refresh_interval_minutes)
            index = self.theme_combobox.findData(default_settings.theme)
            if index != -1:
                self.theme_combobox.setCurrentIndex(index)
    
    def test_connection(self):
        """Test the NAS connection with current settings."""
        if self.testing_connection:
            return
        
        self.testing_connection = True
        self.test_button.setEnabled(False)
        self.test_progress.show()
        self.test_results.show()
        self.test_results.clear()
        self.test_results.append("Testing NAS connection...")
        
        # Create a temporary settings object
        from models import Settings
        test_settings = Settings(
            nas_path=self.nas_path_edit.text().strip(),
            shared_folder=self.shared_folder_edit.text().strip(),
            camera_default_folder=self.camera_folder_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text()
        )
        
        # Test the connection (simplified version)
        QTimer.singleShot(100, lambda: self.perform_connection_test(test_settings))
    
    def perform_connection_test(self, test_settings):
        """Perform the actual connection test."""
        try:
            import os
            
            # Test basic path accessibility
            full_path = test_settings.full_nas_path
            self.test_results.append(f"Testing path: {full_path}")
            
            if os.path.exists(full_path):
                self.test_results.append("✓ Path is accessible")
                
                # Try to list contents
                try:
                    contents = os.listdir(full_path)
                    self.test_results.append(f"✓ Found {len(contents)} items in directory")
                    
                    # Look for camera folders
                    camera_folders = [f for f in contents if os.path.isdir(os.path.join(full_path, f))]
                    if camera_folders:
                        self.test_results.append(f"✓ Found {len(camera_folders)} potential camera folders:")
                        for folder in camera_folders[:5]:  # Show first 5
                            self.test_results.append(f"  - {folder}")
                        if len(camera_folders) > 5:
                            self.test_results.append(f"  ... and {len(camera_folders) - 5} more")
                    else:
                        self.test_results.append("⚠ No camera folders found")
                    
                    self.test_results.append("✓ Connection test successful!")
                    
                except PermissionError:
                    self.test_results.append("✗ Access denied - check credentials")
                except Exception as e:
                    self.test_results.append(f"✗ Error listing directory: {str(e)}")
            else:
                self.test_results.append("✗ Path is not accessible")
                self.test_results.append("  Check that:")
                self.test_results.append("  - NAS is powered on and connected")
                self.test_results.append("  - Network path is correct")
                self.test_results.append("  - Shared folder exists")
                self.test_results.append("  - Credentials are correct (if required)")
        
        except Exception as e:
            self.test_results.append(f"✗ Connection test failed: {str(e)}")
        
        finally:
            self.testing_connection = False
            self.test_button.setEnabled(True)
            self.test_progress.hide()
            
            # Scroll to bottom
            self.test_results.verticalScrollBar().setValue(
                self.test_results.verticalScrollBar().maximum()
            )
