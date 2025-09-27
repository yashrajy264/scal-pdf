#!/bin/bash
# ScalPDF Portable Launcher
# Double-click this file to run ScalPDF directly

# Get script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3 and try again."
    echo ""
    echo "Ubuntu/Debian: sudo apt install python3 python3-tk"
    echo "Fedora: sudo dnf install python3 python3-tkinter"
    echo "Arch: sudo pacman -S python python-tk"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check for tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ Python tkinter not found!"
    echo "Please install tkinter and try again."
    echo ""
    echo "Ubuntu/Debian: sudo apt install python3-tk"
    echo "Fedora: sudo dnf install python3-tkinter"
    read -p "Press Enter to exit..."
    exit 1
fi

# Launch ScalPDF
echo "🚀 Starting ScalPDF Portable..."
python3 ScalPDF-Portable.py

# Keep window open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ScalPDF encountered an error."
    echo "Make sure all dependencies are installed:"
    echo "pip install PyMuPDF Pillow pikepdf cryptography"
    read -p "Press Enter to exit..."
fi
