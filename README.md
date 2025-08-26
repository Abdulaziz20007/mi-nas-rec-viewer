# NAS Camera Viewer

A Python desktop application for viewing security camera recordings stored on Network Attached Storage (NAS) devices.

## Features

- **Dashboard View**: Browse all available cameras with visual cards showing recording status
- **24-Hour Timeline**: Interactive timeline showing video availability throughout the day
- **Seamless Playback**: Continuous playback of 1-minute video segments as a single stream
- **Calendar Navigation**: Easy date selection with visual indicators for recording availability
- **Settings Management**: Configure NAS connection and application preferences
- **Caching System**: Fast startup with local caching of NAS scan results
- **Multi-Camera Support**: Quick switching between different cameras

## Requirements

### System Requirements

- Windows 10/11 (64-bit)
- Network access to NAS device

### Python Requirements (for development)

- Python 3.10 or newer
- PyQt6
- PyInstaller (for building executable)

## Installation

### Option 1: Download Pre-built Executable

1. Download `NASCameraViewer.exe` from releases
2. Run the executable directly - no installation required

### Option 2: Build from Source

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd nas-camera-viewer
   ```

2. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:

   ```bash
   python app.py
   ```

4. **Build executable (optional)**:

   ```bash
   # Windows
   build.bat

   # Linux/macOS
   chmod +x build.sh
   ./build.sh
   ```

## Configuration

### First Time Setup

1. Launch the application
2. Go to **File > Settings** (or press Ctrl+S)
3. Configure your NAS connection:
   - **NAS Path**: Your NAS server path (e.g., `\\\\OPENMEDIAVAULT` or `\\\\192.168.1.100`)
   - **Shared Folder**: The shared folder name (e.g., `test`)
   - **Camera Folder**: Default camera folder name (e.g., `xiaomi_camera_videos`)
   - **Username/Password**: Optional NAS credentials

### Expected Folder Structure

The application expects the following folder structure on your NAS:

```
NAS_PATH/
├── SHARED_FOLDER/
│   └── CAMERA_DEFAULT_FOLDER/
│       ├── CAMERA_ID_1/
│       │   ├── 2024010100/     # YYYYMMDDHH format
│       │   │   ├── 00M00S_timestamp.mp4
│       │   │   ├── 01M00S_timestamp.mp4
│       │   │   └── ...
│       │   ├── 2024010101/
│       │   └── ...
│       ├── CAMERA_ID_2/
│       └── ...
```

Example:

```
\\OPENMEDIAVAULT/
├── test/
│   └── xiaomi_camera_videos/
│       ├── 6005F4CA7D44/
│       │   ├── 2024081207/
│       │   │   ├── 06M02S_1756191962.mp4
│       │   │   ├── 07M01S_1756192021.mp4
│       │   │   └── ...
│       │   └── 2024081212/
│       └── 6005F4CA7D45/
```

## Usage

### Dashboard

- Launch the application to see the camera dashboard
- Each camera appears as a card showing:
  - Camera name/ID
  - Number of recording days
  - Latest recording date
  - Status indicator (Active/No Data)
- Click any camera card to open the player

### Camera Player

- **Video Player**: Large video display with standard controls
- **Calendar**: Left sidebar showing available recording dates
  - Green highlight: Complete recordings
  - Yellow highlight: Partial recordings
  - Gray: No recordings
- **Timeline**: 24-hour interactive timeline below the video
  - Green segments: Available video
  - Gray areas: No recording
  - Red line: Current playback position
  - Click anywhere to seek
- **Quick Navigation**:
  - Hour buttons (0, 2, 4, 6, ..., 22) for quick jumping
  - Time input field for precise seeking
- **Camera Switcher**: Buttons to switch between cameras

### Settings

- **NAS Configuration**: Set up connection to your NAS device
- **Cache Settings**: Configure local caching behavior
- **Auto-refresh**: Set automatic scanning interval
- **Connection Test**: Verify NAS accessibility

## Troubleshooting

### Common Issues

1. **"NAS path not accessible"**

   - Verify NAS is powered on and connected to network
   - Check network path format (use `\\\\` for Windows UNC paths)
   - Test connection using Windows File Explorer
   - Verify credentials if authentication is required

2. **"No cameras found"**

   - Check folder structure matches expected format
   - Verify shared folder and camera folder names in settings
   - Use the connection test in settings to diagnose

3. **Video playback issues**

   - Ensure video files are in a format supported by your system's codecs (MP4, AVI, etc.)
   - Check that video files are not corrupted
   - Verify sufficient network bandwidth for streaming

4. **Slow performance**
   - Enable caching in settings
   - Reduce auto-refresh interval
   - Check network connection speed to NAS

### Log Files

The application logs errors to the console. To see detailed error information:

1. Run the executable from Command Prompt/Terminal
2. Check the console output for error messages

## Development

### Project Structure

```
nas-camera-viewer/
├── app.py                    # Main application entry point
├── main_window.py           # Main application window
├── models.py                # Data models (Camera, RecordingDay, etc.)
├── services.py              # Core services (Config, NAS Scanner, Cache)
├── dashboard_view.py        # Camera dashboard view
├── camera_player_view.py    # Camera player view
├── video_player.py          # VLC video player widget
├── calendar_widget.py       # Custom calendar widget
├── timeline_widget.py       # Custom 24-hour timeline widget
├── settings_view.py         # Settings configuration view
├── requirements.txt         # Python dependencies
├── build.spec              # PyInstaller specification
├── build.bat              # Windows build script
├── build.sh               # Linux/macOS build script
└── README.md              # This file
```

### Architecture

The application follows an MVVM (Model-View-ViewModel) architecture:

- **Model**: Data models and services (`models.py`, `services.py`)
- **View**: UI components (`*_view.py`, `*_widget.py`)
- **ViewModel**: Application logic connecting models and views (`main_window.py`)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with PyQt6 for the user interface
- Uses the Qt Multimedia framework for video playback
- Packaged with PyInstaller for standalone distribution
