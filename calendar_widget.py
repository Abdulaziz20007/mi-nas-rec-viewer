"""
Custom calendar widget for selecting recording dates.
"""
from PyQt6.QtWidgets import QCalendarWidget, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt6.QtGui import QTextCharFormat, QPalette, QFont, QColor
from typing import List, Optional, Set
from datetime import date, datetime

from models import Camera, RecordingDay


class RecordingCalendarWidget(QFrame):
    """Calendar widget that shows available recording dates."""
    
    date_selected = pyqtSignal(date)
    
    def __init__(self):
        super().__init__()
        self.camera: Optional[Camera] = None
        self.available_dates: Set[date] = set()
        self.theme_dict = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the calendar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Title
        self.title_label = QLabel("Select Date")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.calendar.clicked.connect(self.on_date_clicked)
        self.calendar.currentPageChanged.connect(self.update_calendar_display)
        
        layout.addWidget(self.calendar)
        
        # Legend
        legend_frame = QFrame()
        legend_layout = QVBoxLayout(legend_frame)
        legend_layout.setContentsMargins(5, 5, 5, 5)
        legend_layout.setSpacing(3)
        
        legend_title = QLabel("Legend:")
        legend_font = QFont()
        legend_font.setPointSize(9)
        legend_font.setBold(True)
        legend_title.setFont(legend_font)
        legend_layout.addWidget(legend_title)
        
        # Available recordings legend
        available_label = QLabel("● Complete recordings")
        available_label.setProperty("legend", "complete")
        legend_layout.addWidget(available_label)
        
        # Partial recordings legend
        partial_label = QLabel("● Partial recordings")
        partial_label.setProperty("legend", "partial")
        legend_layout.addWidget(partial_label)
        
        # No recordings legend
        none_label = QLabel("● No recordings")
        none_label.setProperty("legend", "none")
        legend_layout.addWidget(none_label)
        
        layout.addWidget(legend_frame)
    
    def apply_theme(self, theme_dict: dict):
        """Apply theme colors to the widget."""
        self.theme_dict = theme_dict
        self.update_calendar_display()
    
    def set_camera(self, camera: Camera):
        """Set the camera and update available dates."""
        self.camera = camera
        self.available_dates = set(camera.get_available_dates())
        self.title_label.setText(f"Select Date - {camera.name}")
        self.calendar.setSelectedDate(QDate.currentDate())
        self.update_calendar_display()
    
    def update_calendar_display(self):
        """Update the calendar display with available dates."""
        if not self.camera or not self.theme_dict:
            return
        
        # Clear all formats
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Format for dates with complete recordings
        complete_format = QTextCharFormat()
        complete_format.setBackground(QColor(self.theme_dict['success']).lighter(160))
        complete_format.setForeground(QColor(self.theme_dict['text-primary']))
        complete_format.setFont(QFont("", -1, QFont.Weight.Bold))
        complete_format.setToolTip("Complete recordings available")
        
        # Format for dates with partial recordings
        partial_format = QTextCharFormat()
        partial_format.setBackground(QColor(self.theme_dict['warning']).lighter(160))
        partial_format.setForeground(QColor(self.theme_dict['text-primary']))
        partial_format.setFont(QFont("", -1, QFont.Weight.Normal))
        partial_format.setToolTip("Partial recordings available")
        
        # Format for dates with no recordings
        disabled_format = QTextCharFormat()
        disabled_format.setForeground(QColor(self.theme_dict['text-muted']))
        disabled_format.setFont(QFont("", -1, QFont.Weight.Normal))
        disabled_format.setToolTip("No recordings available")
        
        # Get the current month and year displayed
        current_date = self.calendar.monthShown(), self.calendar.yearShown()
        
        # Apply formats to all dates in the current month
        start_date = date(current_date[1], current_date[0], 1)
        
        # Check each day in the month
        for day in range(1, 32):  # Max 31 days
            try:
                check_date = date(current_date[1], current_date[0], day)
                qdate = QDate(check_date)
                
                if check_date in self.available_dates:
                    # Check if it's complete or partial recordings
                    recording_day = self.camera.get_recording_day(check_date)
                    if recording_day and self.is_complete_day(recording_day):
                        # Complete day
                        self.calendar.setDateTextFormat(qdate, complete_format)
                    else:
                        # Partial day
                        self.calendar.setDateTextFormat(qdate, partial_format)
                else:
                    # No recordings
                    self.calendar.setDateTextFormat(qdate, disabled_format)
                    
            except ValueError:
                # Invalid date (e.g., Feb 30)
                break
    
    def is_complete_day(self, recording_day: RecordingDay) -> bool:
        """Check if a recording day has complete coverage."""
        if not recording_day.video_segments:
            return False
        
        # Check if we have recordings spanning most of the day
        # This is a simplified check - you might want more sophisticated logic
        recording_hours = recording_day.recording_hours
        
        # Consider it complete if we have recordings for at least 12 hours
        # or if we have recordings spanning at least 16 hours of the day
        if len(recording_hours) >= 12:
            return True
        
        if recording_hours:
            span = max(recording_hours) - min(recording_hours)
            return span >= 16
        
        return False
    
    def on_date_clicked(self, qdate: QDate):
        """Handle date selection."""
        selected_date = qdate.toPyDate()
        
        # Only allow selection of dates with recordings
        if selected_date in self.available_dates:
            self.date_selected.emit(selected_date)
        else:
            # Show a tooltip or message that this date has no recordings
            pass
    
    def get_selected_date(self) -> date:
        """Get the currently selected date."""
        return self.calendar.selectedDate().toPyDate()
    
    def set_selected_date(self, target_date: date):
        """Set the selected date."""
        qdate = QDate(target_date)
        self.calendar.setSelectedDate(qdate)
    
    def clear_selection(self):
        """Clear the current selection."""
        self.camera = None
        self.available_dates.clear()
        self.title_label.setText("Select Date")
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
    
    def navigate_to_date(self, target_date: date):
        """Navigate calendar to show the specified date."""
        qdate = QDate(target_date)
        self.calendar.setCurrentPage(target_date.year, target_date.month)
        self.calendar.setSelectedDate(qdate)
    
    def get_camera_stats_for_month(self, year: int, month: int) -> dict:
        """Get recording statistics for a specific month."""
        if not self.camera:
            return {'total_days': 0, 'recording_days': 0, 'complete_days': 0}
        
        total_days = 0
        recording_days = 0
        complete_days = 0
        
        # Check each day in the month
        for day in range(1, 32):
            try:
                check_date = date(year, month, day)
                total_days += 1
                
                if check_date in self.available_dates:
                    recording_days += 1
                    recording_day = self.camera.get_recording_day(check_date)
                    if recording_day and self.is_complete_day(recording_day):
                        complete_days += 1
                        
            except ValueError:
                # Invalid date
                break
        
        return {
            'total_days': total_days,
            'recording_days': recording_days,
            'complete_days': complete_days
        }
    
    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        # Update calendar display after resize
        self.update_calendar_display()
