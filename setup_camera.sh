#!/bin/bash

# 📸 Camera Permission Setup Script

echo "=========================================="
echo "🎥 Setting up camera permissions..."
echo "=========================================="

# Allow camera access on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📍 Detected Linux system"
    echo ""
    echo "Running: sudo chmod 666 /dev/video*"
    sudo chmod 666 /dev/video*
    echo "✓ Camera permissions updated"
    echo ""
    echo "Optional: Add user to video group"
    echo "  sudo usermod -a -G video $USER"
    echo "  (Requires logout/login to take effect)"
else
    echo "⚠️ Not a Linux system"
    echo "For other OS, ensure camera is enabled in system settings"
fi

echo ""
echo "=========================================="
echo "✓ Setup complete! Run: python3 main.py"
echo "=========================================="
