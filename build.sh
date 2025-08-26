#!/bin/bash
# Build script for NAS Camera Viewer (Linux/macOS)

echo "Building NAS Camera Viewer..."
echo

# Check if python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: PyQt6 is not installed"
    echo "Please run: pip3 install -r requirements.txt"
    exit 1
fi

python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller is not installed"
    echo "Please run: pip3 install -r requirements.txt"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Create build directory
mkdir -p build

# Run PyInstaller
echo "Building executable..."
if [ -f "build.spec" ]; then
    pyinstaller build.spec --noconfirm --clean
elif [ -f "NASCameraViewer.spec" ]; then
    pyinstaller NASCameraViewer.spec --noconfirm --clean
else
    pyinstaller --noconfirm --clean --onefile --windowed --name NASCameraViewer app.py
fi

# Check if build was successful
if [ -f "dist/NASCameraViewer" ]; then
    echo
    echo "=========================================="
    echo "Build completed successfully!"
    echo
    echo "Executable location: dist/NASCameraViewer"
    echo "File size: $(du -h dist/NASCameraViewer | cut -f1)"
    echo
    echo "You can now distribute the executable file."
    echo "=========================================="
    echo
else
    echo
    echo "=========================================="
    echo "Build FAILED!"
    echo
    echo "Check the output above for error messages."
    echo "Common issues:"
    echo "- Missing Python dependencies"
    echo "=========================================="
    echo
fi
