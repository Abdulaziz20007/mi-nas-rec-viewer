"""
Custom 24-hour timeline widget for video navigation.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QFrame, QSizePolicy, QToolTip)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics, QMouseEvent, QPolygonF, QWheelEvent
from typing import List, Optional, Tuple
from datetime import datetime, date, time, timedelta

from models import RecordingDay, VideoSegment


class TimelineWidget(QWidget):
    """Custom widget for displaying and navigating a 24-hour timeline."""
    
    # Signals
    time_clicked = pyqtSignal(float)  # Time in seconds from start of day
    playhead_moved = pyqtSignal(float)  # Playhead position in seconds
    
    def __init__(self):
        super().__init__()
        
        # Timeline data
        self.recording_day: Optional[RecordingDay] = None
        self.video_segments: List[VideoSegment] = []
        
        # Timeline state
        self.playhead_position = 0.0  # Seconds from start of day
        self.total_seconds = 24 * 60 * 60  # 24 hours in seconds
        self.dragging_playhead = False
        self.hover_time = -1.0
        
        self.view_start_seconds = 0.0
        self.visible_duration_seconds = self.total_seconds
        self.min_zoom_duration = 60 * 10  # 10 minutes
        self.max_zoom_duration = self.total_seconds
        
        self.theme_dict = {}
        
        # Layout
        self.timeline_height = 40
        self.hour_label_height = 30
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Fonts
        self.hour_font = QFont("Arial", 9)
        self.time_font = QFont("Arial", 8)

    def apply_theme(self, theme_dict: dict):
        """Apply theme colors to the widget."""
        self.theme_dict = theme_dict
        self.update()

    def _get_color(self, name: str, fallback: str = "#000000") -> QColor:
        """Helper to get a color from the theme dict."""
        if not self.theme_dict:
            # Return a default QColor if theme is not set yet
            return QColor(fallback)
        return QColor(self.theme_dict.get(name, fallback))
    
    def set_recording_day(self, recording_day: RecordingDay):
        """Set the recording day data for the timeline."""
        self.recording_day = recording_day
        self.video_segments = recording_day.video_segments if recording_day else []
        self.view_start_seconds = 0.0
        self.visible_duration_seconds = self.total_seconds
        self.update()
    
    def set_playhead_position(self, seconds: float):
        """Set the playhead position in seconds from start of day."""
        self.playhead_position = max(0, min(seconds, self.total_seconds))
        self.update()
    
    def has_segment_at_time(self, seconds: float) -> bool:
        """Check if a video segment exists at the given time."""
        if not self.video_segments:
            return False
        for segment in self.video_segments:
            start_seconds = (segment.start_time.hour * 3600 +
                           segment.start_time.minute * 60 +
                           segment.start_time.second)
            end_seconds = start_seconds + segment.duration
            if start_seconds <= seconds < end_seconds:
                return True
        return False
    
    def paintEvent(self, event):
        """Paint the timeline widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Calculate timeline area
        timeline_y = self.hour_label_height
        timeline_width = width - 20  # Margin on sides
        timeline_x = 10
        
        # Draw background
        painter.fillRect(0, 0, width, height, self._get_color("surface-alt"))
        
        # Draw timeline background
        timeline_rect = QRect(timeline_x, timeline_y, timeline_width, self.timeline_height)
        painter.fillRect(timeline_rect, self._get_color("surface"))
        painter.setPen(QPen(self._get_color("border"), 1))
        painter.drawRect(timeline_rect)
        
        # Draw hour markers and labels
        self.draw_hour_markers(painter, timeline_x, timeline_y, timeline_width)
        
        # Draw video segments
        self.draw_video_segments(painter, timeline_x, timeline_y, timeline_width)
        
        # Draw hover indicator
        if self.hover_time >= 0:
            self.draw_hover_indicator(painter, timeline_x, timeline_y, timeline_width)
        
        # Draw playhead
        self.draw_playhead(painter, timeline_x, timeline_y, timeline_width)
        
        # Draw time tooltip
        if self.hover_time >= 0:
            self.draw_time_tooltip(painter, timeline_x, timeline_y, timeline_width)
    
    def draw_hour_markers(self, painter: QPainter, x: int, y: int, width: int):
        """Draw hour markers and labels."""
        painter.setFont(self.hour_font)

        # Determine marker interval based on zoom level
        if self.visible_duration_seconds <= 3600:  # <= 1 hour view
            major_interval_seconds = 10 * 60  # 10 minutes
            medium_interval_seconds = 5 * 60 # 5 minutes
            minor_interval_seconds = 1 * 60   # 1 minute
            label_format = "{minutes:02d}:{seconds:02d}"
            label_interval_seconds = 15 * 60 # 15 minutes
        elif self.visible_duration_seconds <= 6 * 3600: # <= 6 hours view
            major_interval_seconds = 3600     # 1 hour
            medium_interval_seconds = 30 * 60 # 30 minutes
            minor_interval_seconds = 10 * 60  # 10 minutes
            label_format = "{hour:02d}:{minutes:02d}"
            label_interval_seconds = 3600 # 1 hour
        else: # > 6 hours view
            major_interval_seconds = 6 * 3600 # 6 hours
            medium_interval_seconds = 3 * 3600 # 3 hours
            minor_interval_seconds = 3600     # 1 hour
            label_format = "{hour:02d}:00"
            label_interval_seconds = 2 * 3600 # 2 hours

        view_end_seconds = self.view_start_seconds + self.visible_duration_seconds
        
        # Start from the first minor interval visible
        start_marker = int(self.view_start_seconds / minor_interval_seconds) * minor_interval_seconds
        
        for s in range(start_marker, int(view_end_seconds) + 1, minor_interval_seconds):
            pos_x = x + ((s - self.view_start_seconds) / self.visible_duration_seconds) * width
            
            if pos_x < x or pos_x > x + width:
                continue

            if s % major_interval_seconds == 0:
                painter.setPen(QPen(self._get_color("text-primary"), 2))
                line_height = self.timeline_height
            elif s % medium_interval_seconds == 0:
                painter.setPen(QPen(self._get_color("text-secondary"), 1))
                line_height = self.timeline_height * 0.7
            else:
                painter.setPen(QPen(self._get_color("border"), 1))
                line_height = self.timeline_height * 0.4
            
            painter.drawLine(int(pos_x), y, int(pos_x), int(y + line_height))
            
            if s % label_interval_seconds == 0:
                painter.setPen(QPen(self._get_color("text-primary"), 1))
                hour = int(s // 3600) % 24
                minutes = int((s % 3600) // 60)
                seconds = int(s % 60)
                
                if "seconds" in label_format:
                    label = label_format.format(minutes=minutes, seconds=seconds)
                else:
                    label = label_format.format(hour=hour, minutes=minutes)

                fm = QFontMetrics(self.hour_font)
                label_width = fm.horizontalAdvance(label)
                label_x = pos_x - label_width // 2
                label_y = y - 5
                
                painter.drawText(int(label_x), int(label_y), label)
    
    def draw_video_segments(self, painter: QPainter, x: int, y: int, width: int):
        """Draw video segments on the timeline."""
        if not self.video_segments:
            return
        
        view_end_seconds = self.view_start_seconds + self.visible_duration_seconds

        for segment in self.video_segments:
            start_time = segment.start_time.time()
            start_seconds = (start_time.hour * 3600 + 
                           start_time.minute * 60 + 
                           start_time.second)
            end_seconds = start_seconds + segment.duration
            
            if end_seconds < self.view_start_seconds or start_seconds > view_end_seconds:
                continue

            segment_start_x = x + ((start_seconds - self.view_start_seconds) / self.visible_duration_seconds) * width
            segment_end_x = x + ((end_seconds - self.view_start_seconds) / self.visible_duration_seconds) * width
            segment_width = segment_end_x - segment_start_x
            
            segment_width = max(segment_width, 1)
            
            segment_rect = QRect(int(segment_start_x), y + 2, 
                               int(segment_width), self.timeline_height - 4)
            
            painter.fillRect(segment_rect, self._get_color("success"))
            
            painter.setPen(QPen(self._get_color("success").darker(120), 1))
            painter.drawRect(segment_rect)
    
    def draw_playhead(self, painter: QPainter, x: int, y: int, width: int):
        """Draw the playhead indicator."""
        playhead_x = self.get_position_for_time(self.playhead_position)
        
        if not (x <= playhead_x <= x + width):
            return
        
        # Draw playhead line
        painter.setPen(QPen(self._get_color("error"), 3))
        painter.drawLine(int(playhead_x), y, int(playhead_x), y + self.timeline_height)
        
        # Draw playhead triangle at top
        triangle_size = 6
        triangle_points = [
            QPointF(playhead_x, y - 2),
            QPointF(playhead_x - triangle_size, y - triangle_size - 2),
            QPointF(playhead_x + triangle_size, y - triangle_size - 2)
        ]
        
        painter.setBrush(QBrush(self._get_color("error")))
        painter.setPen(QPen(self._get_color("error"), 1))
        painter.drawPolygon(QPolygonF(triangle_points))
    
    def draw_hover_indicator(self, painter: QPainter, x: int, y: int, width: int):
        """Draw hover indicator."""
        hover_x = self.get_position_for_time(self.hover_time)
        
        painter.setPen(QPen(self._get_color("primary"), 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(hover_x), y, int(hover_x), y + self.timeline_height)
    
    def draw_time_tooltip(self, painter: QPainter, x: int, y: int, width: int):
        """Draw time tooltip at hover position."""
        if self.hover_time < 0:
            return
        
        # Format time
        hours = int(self.hover_time // 3600)
        minutes = int((self.hover_time % 3600) // 60)
        seconds = int(self.hover_time % 60)
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Calculate tooltip position
        hover_x = self.get_position_for_time(self.hover_time)
        
        # Draw tooltip background
        painter.setFont(self.time_font)
        fm = QFontMetrics(self.time_font)
        text_width = fm.horizontalAdvance(time_text)
        text_height = fm.height()
        
        tooltip_width = text_width + 8
        tooltip_height = text_height + 4
        tooltip_x = hover_x - tooltip_width // 2
        tooltip_y = y + self.timeline_height + 5
        
        # Ensure tooltip stays within widget bounds
        tooltip_x = max(5, min(tooltip_x, self.width() - tooltip_width - 5))
        
        tooltip_rect = QRect(int(tooltip_x), int(tooltip_y), 
                           tooltip_width, tooltip_height)
        
        painter.fillRect(tooltip_rect, self._get_color("surface-alt"))
        painter.setPen(QPen(self._get_color("text-primary"), 1))
        painter.drawText(tooltip_rect, Qt.AlignmentFlag.AlignCenter, time_text)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            timeline_x = 10
            timeline_width = self.width() - 20
            timeline_y = self.hour_label_height
            
            # Check if click is within timeline area
            if (timeline_x <= event.position().x() <= timeline_x + timeline_width and
                timeline_y <= event.position().y() <= timeline_y + self.timeline_height):
                
                clicked_time = self.get_time_at_position(event.position().x())
                
                # Check if clicking near playhead (for dragging)
                playhead_x = self.get_position_for_time(self.playhead_position)
                if abs(event.position().x() - playhead_x) <= 10:
                    self.dragging_playhead = True
                else:
                    # Seek to clicked time only if a segment exists there
                    if self.has_segment_at_time(clicked_time):
                        self.time_clicked.emit(clicked_time)
                        self.set_playhead_position(clicked_time)
                    else:
                        # Handle clicks on empty (gray) areas
                        if not self.video_segments:
                            return  # No recordings for the day, do nothing

                        target_seconds = -1.0

                        # Find the first segment that starts after the clicked time
                        for segment in self.video_segments:
                            start_seconds = (segment.start_time.hour * 3600 +
                                           segment.start_time.minute * 60 +
                                           segment.start_time.second)
                            if start_seconds > clicked_time:
                                target_seconds = float(start_seconds)
                                break
                        
                        if target_seconds == -1.0:
                            # Click was after the last segment, jump to the start of the last segment
                            last_segment = self.video_segments[-1]
                            target_seconds = float(last_segment.start_time.hour * 3600 + last_segment.start_time.minute * 60 + last_segment.start_time.second)
                        
                        if target_seconds >= 0:
                            self.time_clicked.emit(target_seconds)
                            self.set_playhead_position(target_seconds)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        timeline_x = 10
        timeline_width = self.width() - 20
        timeline_y = self.hour_label_height
        
        # Update hover time
        if (timeline_x <= event.position().x() <= timeline_x + timeline_width and
            timeline_y <= event.position().y() <= timeline_y + self.timeline_height):
            
            self.hover_time = self.get_time_at_position(event.position().x())
        else:
            self.hover_time = -1
        
        # Handle playhead dragging
        if self.dragging_playhead:
            new_time = self.get_time_at_position(event.position().x())
            self.set_playhead_position(new_time)
            self.playhead_moved.emit(new_time)
        
        self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_playhead = False
    
    def leaveEvent(self, event):
        """Handle mouse leave events."""
        self.hover_time = -1
        self.update()
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        if delta == 0:
            return

        zoom_factor = 1.2 if delta > 0 else 1 / 1.2
        
        time_at_cursor = self.get_time_at_position(event.position().x())
        
        new_duration = self.visible_duration_seconds / zoom_factor
        new_duration = max(self.min_zoom_duration, min(new_duration, self.max_zoom_duration))
        
        if new_duration == self.visible_duration_seconds:
            return
            
        if self.visible_duration_seconds > 0:
            ratio = (time_at_cursor - self.view_start_seconds) / self.visible_duration_seconds
        else:
            ratio = 0.5
        
        self.visible_duration_seconds = new_duration
        self.view_start_seconds = time_at_cursor - ratio * self.visible_duration_seconds
        
        # Clamp view_start_seconds to be within [0, total_seconds - visible_duration]
        self.view_start_seconds = max(0, min(self.view_start_seconds, self.total_seconds - self.visible_duration_seconds))
        
        self.update()
        event.accept()
    
    def get_time_at_position(self, x: int) -> float:
        """Get time in seconds for a given x position."""
        timeline_x = 10
        timeline_width = self.width() - 20
        
        relative_x = x - timeline_x
        time_seconds = self.view_start_seconds + (relative_x / timeline_width) * self.visible_duration_seconds
        return max(0, min(time_seconds, self.total_seconds))
    
    def get_position_for_time(self, seconds: float) -> int:
        """Get x position for a given time in seconds."""
        timeline_x = 10
        timeline_width = self.width() - 20
        
        if self.visible_duration_seconds == 0:
            return timeline_x
        
        relative_pos = ((seconds - self.view_start_seconds) / self.visible_duration_seconds) * timeline_width
        return int(timeline_x + relative_pos)
    
    def format_time(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def get_segments_at_time(self, seconds: float) -> List[VideoSegment]:
        """Get video segments that are playing at a specific time."""
        target_time = datetime.combine(date.today(), time()) + timedelta(seconds=seconds)
        segments = []
        
        for segment in self.video_segments:
            segment_start = segment.start_time
            segment_end = segment_start + timedelta(seconds=segment.duration)
            
            # Convert to same date for comparison
            segment_start_time = datetime.combine(target_time.date(), segment_start.time())
            segment_end_time = segment_start_time + timedelta(seconds=segment.duration)
            
            if segment_start_time <= target_time < segment_end_time:
                segments.append(segment)
        
        return segments
    
    def clear_timeline(self):
        """Clear the timeline data."""
        self.recording_day = None
        self.video_segments = []
        self.playhead_position = 0.0
        self.hover_time = -1
        self.view_start_seconds = 0.0
        self.visible_duration_seconds = self.total_seconds
        self.update()
