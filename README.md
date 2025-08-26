# 📹 NAS Camera Viewer 🏠

```
 ███╗   ██╗ █████╗ ███████╗     ██████╗ █████╗ ███╗   ███╗
 ████╗  ██║██╔══██╗██╔════╝    ██╔════╝██╔══██╗████╗ ████║
 ██╔██╗ ██║███████║███████╗    ██║     ███████║██╔████╔██║
 ██║╚██╗██║██╔══██║╚════██║    ██║     ██╔══██║██║╚██╔╝██║
 ██║ ╚████║██║  ██║███████║    ╚██████╗██║  ██║██║ ╚═╝ ██║
 ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝     ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝
```

> 🔍 **Your Security, Simplified** - A sleek Python desktop application that transforms your NAS into a powerful security camera management hub!

---

## ✨ What Makes This Special?

🎯 **Smart Dashboard**: Beautiful camera cards that show you everything at a glance  
⏰ **Time Travel**: 24-hour interactive timeline - click anywhere to jump through time!  
🎬 **Seamless Cinema**: Watch hours of recordings as one continuous movie  
📅 **Visual Calendar**: Color-coded dates show recording availability instantly  
⚙️ **Easy Setup**: One-time configuration, lifetime convenience  
🚀 **Lightning Fast**: Smart caching keeps everything snappy  
🔄 **Multi-Camera Magic**: Switch between cameras with a single click

## 🛠️ What You'll Need

### 💻 System Requirements

```
✅ Windows 10/11 (64-bit) - Because we love stability!
🌐 Network connection to your NAS - The magic highway
📁 Some camera recordings - The star of the show!
```

### 🐍 For the Code Wizards (Development)

```python
# The essentials
🐍 Python 3.10+
🎨 PyQt6      # For that gorgeous UI
📦 PyInstaller # Turn Python into .exe magic
```

## 🚀 Get Started in Seconds!

### 🎁 Option 1: The Easy Way (Recommended)

```
1️⃣ Download NASCameraViewer.exe from releases
2️⃣ Double-click and enjoy!
   ↪️ No installation drama, no dependency hell!
```

### 🔧 Option 2: For the Adventurous (From Source)

**🌱 Clone & Conquer:**

```bash
git clone <repository-url>
cd nas-camera-viewer
# Welcome to the source side! 🌟
```

**📦 Gather the Magic Ingredients:**

```bash
pip install -r requirements.txt
# Installing the secret sauce... ✨
```

**🏃‍♂️ Take It for a Spin:**

```bash
python app.py
# And... ACTION! 🎬
```

**🏗️ Build Your Own Executable (Because Why Not?):**

```bash
# Windows Warriors:
build.bat

# Unix/Linux Legends:
chmod +x build.sh && ./build.sh
```

> 💡 **Pro Tip**: The build scripts create a standalone .exe that you can share with friends!

## 🎛️ Setup Your Command Center

### 🚀 First Launch Magic

```
🌟 Launch the app (exciting moment!)
⚙️ Hit File > Settings (or Ctrl+S for speed demons)
🔗 Connect to your NAS and watch the magic happen!
```

### 🗺️ The Connection Map

Fill in these treasure map coordinates:

| 🏷️ Setting           | 📝 What to Enter            | 💡 Example                                  |
| -------------------- | --------------------------- | ------------------------------------------- |
| 🌐 **NAS Path**      | Your network highway        | `\\\\OPENMEDIAVAULT` or `\\\\192.168.1.100` |
| 📁 **Shared Folder** | The main vault              | `test` or `security_videos`                 |
| 📹 **Camera Folder** | Where the action lives      | `xiaomi_camera_videos`                      |
| 🔐 **Credentials**   | Secret handshake (optional) | username & password                         |

### 📂 The Perfect Folder Recipe

Your NAS should be organized like this delicious layer cake:

```
🏠 NAS_ROOT/
├── 📁 SHARED_FOLDER/
│   └── 📹 CAMERA_FOLDER/
│       ├── 📷 CAMERA_ID_1/
│       │   ├── 📅 2024010100/    ← Hour folders (YYYYMMDDHH)
│       │   │   ├── 🎬 00M00S_timestamp.mp4
│       │   │   ├── 🎬 01M00S_timestamp.mp4
│       │   │   └── 🎬 ... more movie magic
│       │   └── 📅 2024010101/
│       └── 📷 CAMERA_ID_2/
```

**🎯 Real-World Example:**

```
🏠 \\OPENMEDIAVAULT/
├── 📁 test/
│   └── 📹 xiaomi_camera_videos/
│       ├── 📷 6005F4CA7D44/           ← Camera 1
│       │   ├── 📅 2024081207/         ← August 12, 7 AM
│       │   │   ├── 🎬 06M02S_1756191962.mp4
│       │   │   ├── 🎬 07M01S_1756192021.mp4
│       │   │   └── 🎬 ... security gold!
│       │   └── 📅 2024081212/         ← August 12, 12 PM
│       └── 📷 6005F4CA7D45/           ← Camera 2
```

## 🎮 Master the Interface

### 🏡 The Dashboard - Your Security HQ

```
🚀 Launch → Instant camera overview
📊 Beautiful cards showing:
   📷 Camera name/ID (your digital sentries)
   📅 Recording days count (how much history you've got)
   ⏰ Latest activity (what's fresh)
   🟢 Status lights (green = active, gray = sleeping)
👆 Click any card → Dive into the action!
```

### 🎬 The Player - Where Magic Happens

**🖥️ Video Theater:**

```
🎭 Large, beautiful video display
⏯️ All the controls you love (play, pause, seek)
🎪 Continuous playback across video segments
```

**📅 Time Machine Calendar:**

```
🟢 Green days = Full recordings (jackpot!)
🟡 Yellow days = Partial recordings (some action)
⚪ Gray days = Quiet days (nothing to see)
👆 Click any date to time travel!
```

**⏰ The 24-Hour Timeline:**

```
🟢 Green bars = Video available (the good stuff)
⚪ Gray gaps = No recording (quiet moments)
🔴 Red line = You are here (current position)
👆 Click anywhere = Instant time jump!
```

**🎯 Quick Navigation Superpowers:**

```
🕒 Hour buttons (0, 2, 4, 6...) → Jump to any hour
⌨️ Time input → Precision seeking (HH:MM:SS)
🔄 Camera buttons → Switch between your digital eyes
```

### ⚙️ Settings Command Center

```
🌐 NAS Setup → Connect to your digital vault
💾 Cache Control → Speed vs. storage balance
🔄 Auto-refresh → How often to check for new footage
🧪 Connection Test → Make sure everything's working
```

## 🚨 When Things Go Sideways

### 🔧 Common Fixes for Common Problems

#### 🚫 "NAS path not accessible"

```
🔍 Detective Work:
   ✅ Is your NAS actually on? (Power button = important!)
   🌐 Network connection solid? (Try pinging it)
   📝 Path format correct? (Windows loves \\\\SERVER)
   🔐 Need a password? (Some NASeS are shy)

🧪 Quick Test: Open Windows File Explorer → Navigate to your NAS
```

#### 👻 "No cameras found"

```
📂 Structure Check:
   ✅ Folder layout matches our recipe above?
   📝 Spelling matters! (case-sensitive sometimes)
   🔧 Try the connection test in settings

💡 Pro Tip: Start with one camera folder to test
```

#### 🎬 Video Playback Acting Up

```
🎭 Format Drama:
   ✅ MP4, AVI files work best
   💿 Corrupted files = no bueno
   🌐 Network too slow? (Try local files first)

🔧 Quick Fix: Try a different video file
```

#### 🐌 Performance Feeling Sluggish

```
⚡ Speed Boost Recipe:
   💾 Enable caching (it's like coffee for apps)
   🔄 Reduce auto-refresh frequency
   🌐 Check your network speed
   💻 More RAM = happier app
```

### 📋 Detective Mode (Logs)

When things get mysterious:

```bash
# Windows Command Prompt:
NASCameraViewer.exe

# Look for clues in the console output! 🕵️‍♂️
```

## 🛠️ For the Code Enthusiasts

### 🏗️ The Blueprint

```
🏠 nas-camera-viewer/
├── 🚀 app.py                    # The launchpad
├── 🏛️ main_window.py           # The command center
├── 📊 models.py                # Data blueprints
├── ⚙️ services.py              # The engine room
├── 🏡 dashboard_view.py        # Camera gallery
├── 🎬 camera_player_view.py    # The main theater
├── 📺 video_player.py          # VLC magic wrapper
├── 📅 calendar_widget.py       # Time travel device
├── ⏰ timeline_widget.py       # 24-hour ruler
├── ⚙️ settings_view.py         # Control panel
├── 📦 requirements.txt         # Shopping list
├── 🔧 build.spec              # Build recipe
├── 🪟 build.bat              # Windows builder
├── 🐧 build.sh               # Unix builder
└── 📖 README.md              # This masterpiece!
```

### 🏛️ Architecture Wisdom

```
📐 MVVM Pattern (Because we're classy):
   📊 Model → Data models & services (the brains)
   🎨 View → UI components (the beauty)
   🔗 ViewModel → The matchmaker (main_window.py)
```

### 🤝 Join the Fun!

```
1️⃣ Fork it (make it yours!)
2️⃣ Branch it (feature/awesome-thing)
3️⃣ Code it (make magic happen)
4️⃣ Test it (break things responsibly)
5️⃣ PR it (share the love!)
```

---

## 📜 The Fine Print

**📄 License:** MIT License - because sharing is caring!

## 🙏 Standing on Giants' Shoulders

- 🎨 **PyQt6** - Making desktop apps beautiful since forever
- 🎬 **Qt Multimedia** - Video playback wizardry
- 📦 **PyInstaller** - Python → .exe alchemy
- ❤️ **You** - For being awesome and using this app!

---

<div align="center">

**🎯 Made with ❤️ for security camera enthusiasts everywhere! 🎯**

_Got questions? Found a bug? Want to add a feature?_  
_Don't be shy - open an issue! 🐛_

</div>
