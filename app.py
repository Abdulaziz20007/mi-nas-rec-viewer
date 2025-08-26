"""
Main entry point for the NAS Camera Viewer application.
"""
import sys
import os

# Suppress verbose FFmpeg logging from Qt Multimedia, which can show non-fatal warnings.
os.environ['QT_LOGGING_RULES'] = 'qt.multimedia.ffmpeg=false'

from PyQt6.QtWidgets import QApplication, QMessageBox, QStyleFactory
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from theme import generate_stylesheet, THEMES

from main_window import MainWindow


class NASCameraViewerApp(QApplication):
    """Main application class."""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = None
        
        # Use a style that better supports stylesheets
        self.setStyle(QStyleFactory.create("Fusion"))

        self.setApplicationName("NAS Camera Viewer")
        self.setApplicationVersion("1.0")
        self.setOrganizationName("NAS Camera Viewer")
        
        # Set application properties
        self.setQuitOnLastWindowClosed(True)
        
        # Set high DPI support (Qt6 enables scaling by default; guard for older flags)
        if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
            self.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
            self.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Create and show main window
        self.main_window = MainWindow()

        # Apply theme
        self.apply_theme()

        self.main_window.show()
    
    def apply_theme(self):
        """Apply the global theme and stylesheet."""
        theme_name = self.main_window.config_service.settings.theme
        stylesheet = generate_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)

        # Notify widgets that need programmatic color updates
        if self.main_window:
            self.main_window.apply_theme(THEMES[theme_name])


def main():
    """Main entry point."""
    try:
        app = NASCameraViewerApp(sys.argv)
        return app.exec()
    except Exception as e:
        print(f"Critical error during application startup: {e}")
        if not QApplication.instance():
            _ = QApplication([])
        QMessageBox.critical(None, "Application Error", 
                               f"Failed to start application:\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
