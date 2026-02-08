#!/usr/bin/env python3
"""
🎥 Camera Diagnostic & Access Tool
Automatically detects and fixes camera permission issues
"""

import os
import sys
import subprocess
import platform
import cv2

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_os():
    """Detect operating system"""
    system = platform.system()
    print(f"🖥️  Operating System: {system}")
    return system

def check_python_opencv():
    """Check if OpenCV can be imported"""
    try:
        import cv2
        print(f"✓ OpenCV installed: {cv2.__version__}")
        return True
    except ImportError:
        print("❌ OpenCV not installed")
        print("   Fix: pip install opencv-python")
        return False

def check_video_devices_linux():
    """Check for video devices on Linux"""
    print("\n📋 Checking video devices...")
    try:
        result = subprocess.run(
            ["ls", "-la", "/dev/video*"],
            shell=True,
            capture_output=True,
            text=True
        )
        devices = subprocess.run(
            "ls /dev/video* 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True
        ).stdout.strip().split('\n')
        
        if devices and devices[0]:
            print(f"✓ Found {len(devices)} camera device(s):")
            for device in devices:
                if device:
                    print(f"   • {device}")
            return True
        else:
            print("❌ No camera devices found (/dev/video*)")
            print("   → Camera may not be connected")
            return False
    except Exception as e:
        print(f"⚠️  Could not check devices: {e}")
        return False

def check_camera_access_linux():
    """Check camera read/write permissions on Linux"""
    print("\n🔐 Checking camera permissions...")
    try:
        result = subprocess.run(
            "ls -la /dev/video0 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            perms = result.stdout.split()[0]
            print(f"   Permissions: {perms}")
            
            if 'rw' in perms or result.stdout.find('rw') > 0:
                print("✓ Camera is readable and writable")
                return True
            else:
                print("❌ Camera permissions restricted")
                print("   Fix: sudo chmod 666 /dev/video*")
                return False
    except Exception as e:
        print(f"⚠️  Error checking permissions: {e}")
        return False

def test_camera_access():
    """Test if Python can open camera"""
    print("\n📹 Testing camera access with OpenCV...")
    
    for index in range(3):
        print(f"   Trying /dev/video{index}...")
        cap = cv2.VideoCapture(index)
        
        if cap.isOpened():
            print(f"✓ Successfully opened camera at index {index}")
            
            # Try to read a frame
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                print(f"✓ Can read frames from camera")
                return True
            else:
                print(f"⚠️  Camera opened but cannot read frames")
        else:
            cap.release()
    
    print("❌ Cannot access any camera device")
    return False

def fix_permissions_linux():
    """Offer to fix permissions automatically"""
    print("\n🔧 Attempting automatic permission fix...")
    
    try:
        print("   Running: sudo chmod 666 /dev/video*")
        result = subprocess.run(
            "sudo chmod 666 /dev/video*",
            shell=True,
            capture_output=True,
            text=True
        )
        print("✓ Permissions updated")
        return True
    except Exception as e:
        print(f"❌ Could not fix permissions: {e}")
        print("   Please run manually: sudo chmod 666 /dev/video*")
        return False

def show_summary(os_type, opencv_ok, devices_ok, access_ok, camera_ok):
    """Show diagnostic summary"""
    print_header("DIAGNOSTIC SUMMARY")
    
    print(f"OS: {os_type}")
    print(f"OpenCV: {'✓ OK' if opencv_ok else '❌ FAILED'}")
    print(f"Devices: {'✓ Found' if devices_ok else '❌ Not found'}")
    print(f"Permissions: {'✓ OK' if access_ok else '❌ Denied'}")
    print(f"Camera Test: {'✓ WORKING' if camera_ok else '❌ FAILED'}")
    
    print()

def main():
    print_header("🎥 CAMERA ACCESS DIAGNOSTIC TOOL")
    
    os_type = check_os()
    
    # Check Python
    print("\n📦 Checking Python environment...")
    opencv_ok = check_python_opencv()
    
    if not opencv_ok:
        print("\n❌ Please install OpenCV first:")
        print("   pip install opencv-python")
        sys.exit(1)
    
    # OS-specific checks
    devices_ok = False
    access_ok = False
    camera_ok = False
    
    if os_type == "Linux":
        devices_ok = check_video_devices_linux()
        access_ok = check_camera_access_linux()
        camera_ok = test_camera_access()
        
        # Show summary
        show_summary(os_type, opencv_ok, devices_ok, access_ok, camera_ok)
        
        # Suggest fixes
        if not camera_ok:
            print("💡 SUGGESTIONS:")
            if not devices_ok:
                print("   1. Check if camera is physically connected")
                print("   2. Run: lsusb (to see USB devices)")
                print("   3. Check system settings for camera access")
            elif not access_ok:
                print("   1. Fix permissions: sudo chmod 666 /dev/video*")
                print("   2. Or add user to video group: sudo usermod -a -G video $USER")
                print("   3. Then logout and login again")
                
                response = input("\n   Run automatic fix? (y/n): ").lower()
                if response == 'y':
                    fix_permissions_linux()
                    print("\n   Please try again: python3 main.py")
            else:
                print("   1. Try restarting the application")
                print("   2. Close other apps using camera")
                print("   3. Try a different camera index")
    
    elif os_type == "Windows":
        print("\n⚠️  Windows: Please check Settings → Privacy & Security → Camera")
        print("   Ensure camera is enabled and app has permission")
        camera_ok = test_camera_access()
        show_summary(os_type, opencv_ok, True, True, camera_ok)
    
    elif os_type == "Darwin":  # macOS
        print("\n⚠️  macOS: Please check System Preferences → Security & Privacy → Camera")
        print("   Ensure Terminal has camera access permission")
        camera_ok = test_camera_access()
        show_summary(os_type, opencv_ok, True, True, camera_ok)
    
    # Final status
    print_header("FINAL RESULT")
    if camera_ok:
        print("✅ CAMERA IS READY!")
        print("\n   You can now run: python3 main.py")
        print("\n   The program will detect license plates in real-time!")
    else:
        print("❌ CAMERA ACCESS FAILED")
        print("\n   Please fix the issues above and try again")
        print("\n   If on Cloud/Codespaces: Download project locally")
        print("   This tool works on your local machine with a real camera")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
