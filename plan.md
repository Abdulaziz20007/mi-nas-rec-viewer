# Design Plan: NAS Camera Recording Viewer

## 1. Executive Summary & Goals

This document outlines the architectural design and implementation plan for a Python-based Windows desktop application for viewing security camera recordings stored on a Network Attached Storage (NAS) device. The application will provide a user-friendly interface to browse cameras, select dates, and watch recordings seamlessly.

**Key Goals:**

- **Centralized Viewing:** Provide a single interface to access and view recordings from multiple Xiaomi cameras stored on a NAS, eliminating the need to manually browse network folders.
- **Seamless Playback Experience:** Create a continuous, 24-hour timeline for each day's recordings by virtually stitching together individual one-minute video files, with clear visual indicators for available and missing footage.
- **User-Friendly Navigation:** Implement an intuitive UI with a camera dashboard, a calendar for date selection, and familiar video player controls for an efficient user experience.
- **Standalone Deployment:** Package the final application into a single executable (`.exe`) file for easy distribution and installation on Windows machines.

## 2. Current Situation Analysis

The project is a "greenfield" development effort. The current system consists of a manual process where the user navigates a specific network folder structure (`\\NAS\Share\Camera_Default_Folder\Camera_ID\Date\video_files.mp4`) using Windows File Explorer.

**Key Pain Points to Address:**

- **Fragmented Viewing:** Watching a sequence of events requires manually opening multiple one-minute video files.
- **Lack of Timeline Visualization:** It is difficult to see at a glance what times of the day have recordings and which are missing.
- **Inefficient Navigation:** Switching between cameras or different days is a cumbersome, multi-step process.
- **Technical Barrier:** Requires users to be comfortable navigating network paths and understanding the folder structure.

## 3. Proposed Solution / Refactoring Strategy

### 3.1. High-Level Design / Architectural Overview

The application will be built on a Model-View-ViewModel (MVVM) architecture to ensure a clear separation of concerns between the user interface (View), the application logic (ViewModel), and the data handling (Model). This promotes testability and maintainability.

**Core Technology Stack:**

- **Programming Language:** Python 3.10+
- **GUI Framework:** **PyQt6** or **PySide6**. Chosen for its powerful widget library, support for custom UI elements (essential for the 24-hour timeline), and robust multimedia integration capabilities.
- **Video Playback:** **PyQt6.QtMultimedia**. Chosen as it's part of the Qt framework, providing good integration and removing the need for external dependencies like VLC Media Player to be installed on the user's system.
- **Packaging:** **PyInstaller**. As specified by the user, for creating the standalone Windows executable.

**Architectural Diagram (Conceptual):**

```
+-----------------------------------------------------------------+
|                           VIEW (PyQt6)                          |
|-----------------------------------------------------------------|
| [DashboardWindow] [CameraPlayerWindow]      [SettingsWindow]    |
|   - CameraCard    - VideoPlayer (QtMultimedia) - ConfigForm     |
|                   - CalendarWidget                              |
|                   - TimelineWidget                              |
|                   - CameraSwitcher                              |
+-----------------------------------------------------------------+
       ^                                      | (Reads/Writes)
       | (Data Binding & Commands)            v
+-----------------------------------------------------------------+
|                        VIEWMODEL (Python Logic)                 |
|-----------------------------------------------------------------|
| - DashboardViewModel (Manages list of cameras)                  |
| - CameraPlayerViewModel (Manages selected camera/date/playback) |
| - SettingsViewModel (Manages application configuration)         |
+-----------------------------------------------------------------+
       ^                                      | (Reads/Writes)
       | (Requests Data)                      v
+-----------------------------------------------------------------+
|                           MODEL (Data & Services)               |
|-----------------------------------------------------------------|
| - ConfigService (Handles loading/saving settings.json)          |
| - NASScannerService (Scans NAS for cameras/recordings)          |
| - CacheService (Caches NAS scan results to avoid re-scans)      |
| - Data Models (Camera, RecordingDay, VideoSegment)              |
+-----------------------------------------------------------------+
```

### 3.2. Key Components / Modules

- **ConfigService:** A singleton module responsible for loading, saving, and providing access to application settings (NAS path, credentials, etc.) from a local JSON or INI file.
- **NASScannerService:** Handles all interactions with the network file system. It will contain logic to discover camera folders, parse date-based subfolders, and index the one-minute video files. This service will run in a separate thread to prevent UI freezes.
- **CacheService:** Stores the results of the NAS scan (the file index) locally. On startup, it will load the cache and trigger a background refresh if the data is stale, ensuring a fast application launch.
- **CameraPlayerViewModel:** The core of the application's logic. It will take a selected camera and date, retrieve the list of video files from the `NASScannerService`, construct a playlist for the media player, and calculate the data for the 24-hour timeline widget.
- **TimelineWidget (Custom PyQt Widget):** A custom-drawn widget. It will display a 24-hour bar, render green segments based on the list of available video files for the selected day, and allow the user to click/drag to seek to a specific time.
- **VideoPlayer (QtMultimedia Integration):** A `QVideoWidget` that hosts the `QMediaPlayer` video output. It will receive commands (play, pause, seek) from the `CameraPlayerViewModel`.

### 3.3. Detailed Action Plan / Phases

#### Phase 1: Core Backend and Foundation

- **Objective(s):** Establish the project structure and implement the core non-UI logic for configuration and NAS interaction.
- **Priority:** High

- **Task 1.1: Project Setup**

  - **Rationale/Goal:** Create a clean project structure and initialize dependencies.
  - **Estimated Effort:** S
  - **Deliverable/Criteria for Completion:** A Git repository is initialized. A virtual environment is created with `PyQt6` and `PyInstaller` installed. A basic `main.py` entry point exists.

- **Task 1.2: Configuration Management (`ConfigService`)**

  - **Rationale/Goal:** Create a robust way to manage application settings without hardcoding values.
  - **Estimated Effort:** S
  - **Deliverable/Criteria for Completion:** A class that can read from and write to a `settings.json` file. It should handle default values if the file doesn't exist. Settings include `nas_path`, `shared_folder`, `username`, `password`.

- **Task 1.3: Data Models Definition**

  - **Rationale/Goal:** Define the core data structures for the application.
  - **Estimated Effort:** S
  - **Deliverable/Criteria for Completion:** Python classes/dataclasses for `Camera` (ID, path), `RecordingDay` (date, list of video segments), and `VideoSegment` (path, start_time, duration) are defined.

- **Task 1.4: NAS File Scanner (`NASScannerService`)**

  - **Rationale/Goal:** Implement the logic to discover and index all relevant video files from the NAS. This is a critical and potentially slow operation.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** A service that, given a root path, can recursively scan and return a structured list of `Camera` objects, each populated with its `RecordingDay`s. The service must correctly merge multiple folders for the same day. This should be testable via a command-line script.

- **Task 1.5: Caching Mechanism (`CacheService`)**
  - **Rationale/Goal:** Improve application startup time and reduce network load by caching the NAS file index.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** The `NASScannerService`'s output can be saved to a local file (e.g., `cache.pkl` or `cache.json`). On subsequent runs, the app reads from the cache first and triggers a background rescan.

#### Phase 2: UI Scaffolding and Dashboard

- **Objective(s):** Build the main application window and the initial camera selection screen.
- **Priority:** High

- **Task 2.1: Main Application Window**

  - **Rationale/Goal:** Create the main container for all other UI views.
  - **Estimated Effort:** S
  - **Deliverable/Criteria for Completion:** A basic, empty PyQt window that launches and closes cleanly.

- **Task 2.2: Dashboard View**

  - **Rationale/Goal:** Display the discovered cameras to the user.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** A view that displays a grid or list of "Camera Cards". Each card shows the camera ID. The view is populated with data from the `NASScannerService`.

- **Task 2.3: Navigation Logic**
  - **Rationale/Goal:** Allow users to move from the dashboard to the (currently non-existent) player view.
  - **Estimated Effort:** S
  - **Deliverable/Criteria for Completion:** Clicking a Camera Card on the dashboard navigates to a placeholder "Player View" widget, passing the selected Camera ID.

#### Phase 3: Camera Player View Implementation

- **Objective(s):** Develop the core feature of the application: the video player and its associated controls.
- **Priority:** High

- **Task 3.1: Video Player Integration**

  - **Rationale/Goal:** Embed a functional video player into the UI.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** A `QMediaPlayer` is connected to a `QVideoWidget`. A simple playlist of 2-3 video files from the NAS can be loaded and played back-to-back seamlessly. Basic play/pause/volume controls are functional.

- **Task 3.2: Calendar Widget**

  - **Rationale/Goal:** Create the date selection component.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** A `QCalendarWidget` is displayed in the sidebar. It is populated with data for the selected camera. Dates with recordings are visually distinct (e.g., bolded). Dates without recordings are disabled. Selecting a date fires a signal.

- **Task 3.3: Custom 24-Hour Timeline Widget**

  - **Rationale/Goal:** Build the most complex UI component for visualizing data availability and seeking.
  - **Estimated Effort:** L
  - **Deliverable/Criteria for Completion:** A custom `QWidget` is created. It draws a long horizontal bar. It can receive a list of `VideoSegment`s for a day and draw corresponding green blocks on the bar. A playhead line is drawn that can be updated programmatically. Clicking on the bar seeks the video player to the corresponding time.

- **Task 3.4: Player View ViewModel and Integration**

  - **Rationale/Goal:** Connect all the components of the player view to work together.
  - **Estimated Effort:** L
  - **Deliverable/Criteria for Completion:** Selecting a date in the calendar loads the corresponding videos into the player's playlist and updates the 24-hour timeline widget. The player's progress updates the playhead on the timeline. The hour markers and time input field are functional and can seek the player.

- **Task 3.5: Camera Switcher Sidebar**
  - **Rationale/Goal:** Implement the quick-switch functionality between cameras.
  - **Estimated Effort:** S
  - **Deliverable/Criteria for Completion:** A list of buttons, one for each camera, is displayed below the calendar. Clicking a button switches the entire player view to that camera's data.

#### Phase 4: Settings, Polishing, and Packaging

- **Objective(s):** Finalize the application with configuration options, error handling, and a distributable package.
- **Priority:** Medium

- **Task 4.1: Settings Page UI**

  - **Rationale/Goal:** Allow users to configure the application without editing files manually.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** A new window or view with input fields for NAS Path, Shared Folder, Username, and Password (masked). A "Save" button writes the settings using the `ConfigService`.

- **Task 4.2: Error Handling and UI Feedback**

  - **Rationale/Goal:** Make the application robust and user-friendly.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** The UI displays clear error messages if the NAS path is unreachable. A loading indicator is shown while the NAS is being scanned. The UI remains responsive during background tasks.

- **Task 4.3: PyInstaller Configuration and Build Script**

  - **Rationale/Goal:** Create the final `.exe` file.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** A `build.spec` file for PyInstaller is created. It correctly bundles the Python source and assets (icons). It ensures Qt Multimedia plugins are included. A build script (`build.bat` or similar) automates the creation of the single-file executable.

- **Task 4.4: Final Testing and Bug Fixing**
  - **Rationale/Goal:** Ensure a high-quality final product.
  - **Estimated Effort:** M
  - **Deliverable/Criteria for Completion:** The application is tested on a clean Windows machine. The executable runs correctly, connects to the NAS, and all features work as expected.

### 3.4. Data Model Changes

This is a new application, so no data models are being changed. The primary data models to be created are:

- `Settings`: A dataclass or dictionary to hold configuration.
- `Camera`: Represents a single camera, containing its ID and a list of `RecordingDay` objects.
- `RecordingDay`: Represents a single day of recordings, containing a `date` and a sorted list of `VideoSegment` objects.
- `VideoSegment`: Represents a single 1-minute video file, containing its absolute path and its start `datetime`.

## 4. Key Considerations & Risk Mitigation

### 4.1. Technical Risks & Challenges

- **Risk:** Slow NAS scanning performance over Wi-Fi or with a large number of files.
  - **Mitigation:** The background scanning thread and aggressive caching (`Phase 1`) are critical. The UI must always launch instantly using cached data.
- **Risk:** Choppy video playback or delays when transitioning between 1-minute files.
  - **Mitigation:** Manage the playlist manually by listening for the `mediaStatusChanged` signal from `QMediaPlayer` and loading the next segment when the current one ends.
- **Risk:** Missing codecs on the target system for `QtMultimedia`.
  - **Mitigation:** `QtMultimedia` on Windows typically uses DirectShow or Media Foundation, which should handle common formats like H.264/MP4. Advise users to install a codec pack (like K-Lite) if they encounter issues, although this is less ideal than a self-contained solution.
- **Risk:** Network connectivity issues (NAS offline, incorrect credentials).
  - **Mitigation:** Implement comprehensive error handling (`Task 4.2`). The application should not crash but instead inform the user of the problem and allow them to go to the settings page to fix it.

### 4.2. Dependencies

- **Internal:** The phases are largely sequential. The UI work (Phase 2 & 3) depends heavily on the backend services from Phase 1 being complete and reliable.
- **External:** The application is dependent on the continued availability and stability of the `PyQt6` and `PyInstaller` libraries. It also depends on the user's network infrastructure and the NAS itself.

### 4.3. Non-Functional Requirements (NFRs) Addressed

- **Performance:** Addressed by background processing for network operations and a local caching strategy to ensure fast startup and a responsive UI.
- **Usability:** Addressed by designing a familiar, intuitive UI (Dashboard, Calendar, YouTube-like player) and providing clear feedback during loading or error states.
- **Reliability:** Addressed by structured error handling for network and file system operations, preventing application crashes.
- **Maintainability:** Addressed by using the MVVM architecture, which separates concerns and makes individual components easier to modify and test.

## 5. Success Metrics / Validation Criteria

- **Goal Achievement:** The application successfully discovers all cameras and plays back recordings for a selected day without any noticeable stutter between the 1-minute video files.
- **Performance:** The application launches in under 3 seconds on subsequent runs (using cache). UI remains responsive (no freezes > 500ms) during all operations.
- **User Feedback:** A user can successfully navigate to a specific camera, pick a date and time (e.g., August 26th, 12:15 PM), and be watching the correct video segment within 15 seconds.
- **Deployment:** A single `.exe` file is produced that runs on a target Windows machine without requiring a separate Python installation.

## 6. Assumptions Made

- The NAS uses a standard SMB/CIFS file sharing protocol that is accessible from Windows via a `\\SERVER\SHARE` path.
- The file and folder naming conventions observed in the user request (`CameraID/YYYYMMDDHH/MM'M'SS'S'_timestamp.mp4`) are consistent for all cameras and recordings.
- The user running the application will have read permissions for the specified network share.
- The video files are in a standard codec (e.g., H.264) playable by the default Windows codecs (Media Foundation/DirectShow).

## 7. Open Questions / Areas for Further Investigation

- **Authentication:** How should NAS credentials be stored securely? For this plan, they will be stored in the plain-text `settings.json`, but for a more robust solution, using the Windows Credential Manager should be investigated.
- **Time Zones:** Does the file naming convention reflect local time or UTC? The plan assumes local time, but this needs to be confirmed to ensure the timeline is accurate.
- **Performance at Scale:** How does the application perform with 10+ cameras and years of footage? The caching model should scale well, but performance testing with a large, simulated file structure would be beneficial.
- **File Naming Details:** What exactly does the timestamp (`1756191962`) in the filename represent? Is it a Unix timestamp? If so, it can be used as a more reliable source for the video's start time than parsing the `MMSS` part of the name. This should be clarified.
