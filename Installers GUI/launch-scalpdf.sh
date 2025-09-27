#!/bin/bash
# ScalPDF Standalone Launcher Script
# Double-click this file to launch ScalPDF without terminal

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to show GUI error dialog
show_error() {
    local message="$1"
    if command -v zenity &> /dev/null; then
        zenity --error --text="$message" --title="ScalPDF Launcher Error"
    elif command -v kdialog &> /dev/null; then
        kdialog --error "$message" --title "ScalPDF Launcher Error"
    elif command -v xmessage &> /dev/null; then
        xmessage -center "ScalPDF Launcher Error: $message"
    else
        echo "Error: $message"
        read -p "Press Enter to exit..."
    fi
}

# Function to show GUI info dialog
show_info() {
    local message="$1"
    if command -v zenity &> /dev/null; then
        zenity --info --text="$message" --title="ScalPDF Launcher"
    elif command -v kdialog &> /dev/null; then
        kdialog --msgbox "$message" --title "ScalPDF Launcher"
    elif command -v xmessage &> /dev/null; then
        xmessage -center "ScalPDF Launcher: $message"
    else
        echo "Info: $message"
    fi
}

# Check if we have a display (GUI environment)
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    show_error "No graphical display detected. Please run this in a desktop environment."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 is not installed. Please install Python 3 and try again.\n\nTo install: sudo apt install python3 python3-tk"
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    show_error "Python tkinter is not installed. Please install it and try again.\n\nTo install: sudo apt install python3-tk"
    exit 1
fi

# Launch the ScalPDF launcher
show_info "Starting ScalPDF Launcher..."
cd "$SCRIPT_DIR"

# Try the executable version first (no .py extension)
if [ -f "ScalPDF-Launcher" ] && [ -x "ScalPDF-Launcher" ]; then
    python3 ScalPDF-Launcher
elif [ -f "scalpdf_launcher.py" ]; then
    python3 scalpdf_launcher.py
else
    show_error "ScalPDF launcher files not found in $SCRIPT_DIR"
    exit 1
fi

# Check if launcher started successfully
if [ $? -ne 0 ]; then
    show_error "ScalPDF Launcher failed to start. Please check that all dependencies are installed."
fi
