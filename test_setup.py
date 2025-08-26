#!/usr/bin/env python3
"""
Test script to verify NAS Camera Viewer setup.
"""

import sys
import os

def test_python_version():
    """Test Python version."""
    print("Testing Python version...")
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("⚠ Warning: Python 3.10+ recommended")
    return True

def test_import(module_name, display_name=None):
    """Test if a module can be imported."""
    if display_name is None:
        display_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {display_name}")
        return True
    except ImportError as e:
        print(f"✗ {display_name} - {e}")
        return False
    except Exception as e:
        print(f"✗ {display_name} - Error: {e}")
        return False



def main():
    """Main test function."""
    print("=" * 50)
    print("NAS Camera Viewer Setup Test")
    print("=" * 50)
    
    results = []
    
    # Test Python version
    results.append(test_python_version())
    
    print("\nTesting Python packages...")
    
    # Test required packages
    results.append(test_import("PyQt6", "PyQt6"))
    results.append(test_import("PyQt6.QtMultimedia", "PyQt6.QtMultimedia"))
    results.append(test_import("PyInstaller", "PyInstaller"))
    
    # Test application modules
    print("\nTesting application modules...")
    app_modules = [
        ("models", "Data Models"),
        ("services", "Services"),
        ("main_window", "Main Window"),
        ("dashboard_view", "Dashboard View"),
        ("video_player", "Video Player"),
    ]
    
    for module, name in app_modules:
        results.append(test_import(module, name))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("Your setup is ready! You can run the application with: python app.py")
    else:
        print(f"✗ {total - passed} test(s) failed ({passed}/{total} passed)")
        print("\nNext steps:")
        print("1. Ensure all packages are installed: pip install -r requirements.txt")
        print("2. Run this test again: python test_setup.py")
    
    print("\nTo build the executable after all tests pass:")
    print("  Windows: .\\build.bat")
    print("  Linux/macOS: ./build.sh")

if __name__ == "__main__":
    main()
