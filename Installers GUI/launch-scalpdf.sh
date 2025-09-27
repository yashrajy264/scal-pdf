#!/bin/bash
# ScalPDF Standalone Launcher Script
# Double-click this file to launch ScalPDF without terminal

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we have a display (GUI environment)
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "Error: No graphical display detected."
    echo "Please run this in a desktop environment."
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

# Launch the ScalPDF launcher
echo "Starting ScalPDF Launcher..."
cd "$SCRIPT_DIR"
python3 scalpdf_launcher.py

# Keep window open if there's an error
if [ $? -ne 0 ]; then
    echo "ScalPDF Launcher encountered an error."
    read -p "Press Enter to exit..."
fi
