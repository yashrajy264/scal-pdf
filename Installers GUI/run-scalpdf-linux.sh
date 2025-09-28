#!/bin/bash
# ScalPDF Linux Launcher
# Automatically handles dependencies and runs ScalPDF

echo "🔒 ScalPDF - Secure PDF Viewer & Editor"
echo "=================================================="

# Get script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  Fedora: sudo dnf install python3 python3-pip python3-tkinter"
    echo "  Arch: sudo pacman -S python python-pip tk"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Python 3 found"

# Check tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ Python tkinter not found!"
    echo "Installing tkinter..."
    
    # Try to install tkinter based on distribution
    if command -v apt >/dev/null 2>&1; then
        sudo apt update && sudo apt install -y python3-tk
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y python3-tkinter
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S tk
    else
        echo "Please install tkinter manually for your distribution"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ GUI support available"

# Check and install PDF dependencies
echo "📦 Checking PDF processing libraries..."

# Function to install pip package
install_package() {
    local package=$1
    echo "  Installing $package..."
    python3 -m pip install --user "$package" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✅ $package installed"
        return 0
    else
        echo "  ⚠️ Failed to install $package"
        return 1
    fi
}

# Check and install dependencies
deps_needed=false

if ! python3 -c "import fitz" 2>/dev/null; then
    echo "📥 Installing PyMuPDF..."
    install_package "PyMuPDF"
    deps_needed=true
fi

if ! python3 -c "from PIL import Image" 2>/dev/null; then
    echo "📥 Installing Pillow..."
    install_package "Pillow"
    deps_needed=true
fi

if ! python3 -c "import pikepdf" 2>/dev/null; then
    echo "📥 Installing pikepdf..."
    install_package "pikepdf"
    deps_needed=true
fi

if ! python3 -c "from cryptography.fernet import Fernet" 2>/dev/null; then
    echo "📥 Installing cryptography..."
    install_package "cryptography"
    deps_needed=true
fi

if [ "$deps_needed" = true ]; then
    echo "✅ Dependencies installed!"
else
    echo "✅ All dependencies already available"
fi

# Launch ScalPDF
echo "🚀 Starting ScalPDF..."
echo ""

if [ -f "ScalPDF-Portable.py" ]; then
    python3 ScalPDF-Portable.py
elif [ -f "ScalPDF-Linux" ]; then
    python3 ScalPDF-Linux
else
    echo "❌ ScalPDF application files not found!"
    echo "Make sure you're in the correct directory."
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "👋 ScalPDF closed. Thank you for using ScalPDF!"
