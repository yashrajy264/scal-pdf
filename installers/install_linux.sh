#!/bin/bash
# ScalPDF Linux Installer
# Installs ScalPDF with full functionality and desktop integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="ScalPDF"
APP_DIR="$HOME/.local/share/scalpdf"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
VENV_DIR="$APP_DIR/venv"

echo -e "${BLUE}🚀 ScalPDF Linux Installer${NC}"
echo "=================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Run as normal user."
   exit 1
fi

# Check Python version
echo "🔍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    echo "Run: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    print_status "Python $PYTHON_VERSION detected"
else
    print_error "Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    sudo apt update
    sudo apt install -y python3-pip python3-venv python3-dev \
        libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 \
        libgl1-mesa-glx libglib2.0-0 libfontconfig1 libx11-xcb1 \
        libxcb-glx0 libxcb-shape0 libxcb-util1 libxrender1 libxi6 \
        libffi-dev
    print_status "System dependencies installed"
elif command -v dnf &> /dev/null; then
    # Fedora
    sudo dnf install -y python3-pip python3-virtualenv python3-devel \
        libxcb libX11-xcb mesa-libGL glib2 fontconfig libXrender libXi \
        libffi-devel
    print_status "System dependencies installed"
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm python-pip python-virtualenv \
        libxcb libx11 mesa glib2 fontconfig libxrender libxi libffi
    print_status "System dependencies installed"
else
    print_warning "Unknown package manager. You may need to install dependencies manually."
fi

# Create directories
echo "📁 Creating application directories..."
mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"
print_status "Directories created"

# Copy application files
echo "📋 Copying application files..."
cp -r . "$APP_DIR/"
print_status "Application files copied"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
print_status "Virtual environment created"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
print_status "Python dependencies installed"

# Create launcher scripts
echo "🔧 Creating launcher scripts..."

# GUI launcher
cat > "$BIN_DIR/scalpdf" << EOF
#!/bin/bash
# ScalPDF GUI Launcher
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"
python3 main.py "\$@"
EOF

# CLI launcher
cat > "$BIN_DIR/scalpdf-cli" << EOF
#!/bin/bash
# ScalPDF CLI Launcher
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"
python3 -m cli.cli "\$@"
EOF

chmod +x "$BIN_DIR/scalpdf"
chmod +x "$BIN_DIR/scalpdf-cli"
print_status "Launcher scripts created"

# Create desktop entry
echo "🖥️  Creating desktop entry..."
cat > "$DESKTOP_DIR/scalpdf.desktop" << EOF
[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Management Tool
GenericName=PDF Manager
Exec=$BIN_DIR/scalpdf %f
Icon=scalpdf
Categories=Office;Graphics;Photography;Viewer;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
Keywords=PDF;Document;Viewer;Editor;Encryption;Security;
Actions=CLI;

[Desktop Action CLI]
Name=Open CLI
Exec=x-terminal-emulator -e $BIN_DIR/scalpdf-cli
EOF

chmod +x "$DESKTOP_DIR/scalpdf.desktop"
print_status "Desktop entry created"

# Create application icon
echo "🎨 Creating application icon..."
# Create a simple SVG icon if none exists
if [ ! -f "$APP_DIR/assets/icon.png" ]; then
    mkdir -p "$APP_DIR/assets"
    cat > "$APP_DIR/assets/icon.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#2563eb" rx="32"/>
  <rect x="48" y="48" width="160" height="200" fill="white" rx="8"/>
  <rect x="64" y="80" width="128" height="8" fill="#e5e7eb" rx="4"/>
  <rect x="64" y="104" width="96" height="8" fill="#e5e7eb" rx="4"/>
  <rect x="64" y="128" width="112" height="8" fill="#e5e7eb" rx="4"/>
  <rect x="64" y="152" width="80" height="8" fill="#e5e7eb" rx="4"/>
  <circle cx="192" cy="192" r="24" fill="#dc2626"/>
  <path d="M184 192 L192 200 L208 184" stroke="white" stroke-width="3" fill="none"/>
  <text x="128" y="40" text-anchor="middle" fill="white" font-family="Arial" font-size="16" font-weight="bold">ScalPDF</text>
</svg>
EOF
    
    # Convert SVG to PNG if possible
    if command -v convert &> /dev/null; then
        convert "$APP_DIR/assets/icon.svg" -resize 256x256 "$APP_DIR/assets/icon.png"
    elif command -v inkscape &> /dev/null; then
        inkscape "$APP_DIR/assets/icon.svg" --export-png="$APP_DIR/assets/icon.png" --export-width=256 --export-height=256
    fi
fi

# Copy icon to system location
if [ -f "$APP_DIR/assets/icon.png" ]; then
    cp "$APP_DIR/assets/icon.png" "$ICON_DIR/scalpdf.png"
elif [ -f "$APP_DIR/assets/icon.svg" ]; then
    cp "$APP_DIR/assets/icon.svg" "$ICON_DIR/scalpdf.svg"
fi
print_status "Application icon installed"

# Update desktop database
echo "🔄 Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi
print_status "Desktop database updated"

# Add to PATH if not already there
echo "🛤️  Updating PATH..."
SHELL_RC=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi

if [ -f "$SHELL_RC" ] && ! grep -q "$BIN_DIR" "$SHELL_RC"; then
    echo "" >> "$SHELL_RC"
    echo "# ScalPDF" >> "$SHELL_RC"
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
    print_status "Added to PATH in $SHELL_RC"
fi

# Create uninstaller
echo "🗑️  Creating uninstaller..."
cat > "$BIN_DIR/scalpdf-uninstall" << EOF
#!/bin/bash
# ScalPDF Uninstaller

echo "🗑️  Uninstalling ScalPDF..."

# Remove application files
rm -rf "$APP_DIR"

# Remove launchers
rm -f "$BIN_DIR/scalpdf"
rm -f "$BIN_DIR/scalpdf-cli"
rm -f "$BIN_DIR/scalpdf-uninstall"

# Remove desktop entry
rm -f "$DESKTOP_DIR/scalpdf.desktop"

# Remove icon
rm -f "$ICON_DIR/scalpdf.png"
rm -f "$ICON_DIR/scalpdf.svg"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo "✅ ScalPDF uninstalled successfully"
echo "Note: You may need to remove the PATH entry from your shell configuration manually"
EOF

chmod +x "$BIN_DIR/scalpdf-uninstall"
print_status "Uninstaller created"

# Run tests
echo "🧪 Running installation tests..."
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

# Test imports
python3 -c "
try:
    import PySide6; print('✅ PySide6 OK')
    import fitz; print('✅ PyMuPDF OK')
    import pikepdf; print('✅ pikepdf OK')
    import PIL; print('✅ Pillow OK')
    import cryptography; print('✅ cryptography OK')
    import argon2; print('✅ argon2 OK')
    print('✅ All dependencies working!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

print_status "Installation tests passed"

# Final success message
echo ""
echo -e "${GREEN}🎉 ScalPDF installed successfully!${NC}"
echo ""
echo "📖 Usage:"
echo "  • GUI: scalpdf (or find 'ScalPDF' in your application menu)"
echo "  • CLI: scalpdf-cli --help"
echo "  • Uninstall: scalpdf-uninstall"
echo ""
echo "🔧 Installation Details:"
echo "  • Application: $APP_DIR"
echo "  • Executables: $BIN_DIR"
echo "  • Desktop entry: $DESKTOP_DIR/scalpdf.desktop"
echo "  • Icon: $ICON_DIR/scalpdf.png"
echo ""
echo "🔄 To use immediately, either:"
echo "  • Restart your terminal, or"
echo "  • Run: source $SHELL_RC"
echo "  • Or use full path: $BIN_DIR/scalpdf"
echo ""
echo -e "${BLUE}ScalPDF is now ready to use! 🚀${NC}"
