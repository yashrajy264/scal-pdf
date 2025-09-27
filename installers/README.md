# ScalPDF Installers

This directory contains platform-specific installers for ScalPDF that provide full local installation with desktop integration.

## 🐧 Linux Installation

### Quick Install
```bash
chmod +x install_linux.sh
./install_linux.sh
```

### What it does:
- ✅ **System Dependencies**: Installs required system packages (Qt, graphics libraries)
- ✅ **Python Environment**: Creates isolated virtual environment
- ✅ **Full Installation**: Installs to `~/.local/share/scalpdf`
- ✅ **Desktop Integration**: Adds to application menu and creates desktop shortcut
- ✅ **PATH Integration**: Adds `scalpdf` and `scalpdf-cli` commands
- ✅ **Icon Creation**: Generates application icon
- ✅ **Uninstaller**: Creates `scalpdf-uninstall` command

### Supported Distributions:
- **Ubuntu/Debian** (apt)
- **Fedora/RHEL** (dnf)
- **Arch Linux** (pacman)
- **Other distributions** (manual dependency installation)

### Usage after installation:
```bash
# GUI Application
scalpdf

# CLI Interface  
scalpdf-cli --help

# Uninstall
scalpdf-uninstall
```

## 🪟 Windows Installation

### Option 1: PowerShell (Recommended)
```powershell
# Run as Administrator (optional, for system-wide installation)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\install_windows.ps1
```

### Option 2: Batch File
```cmd
# Double-click or run from Command Prompt
install_windows.bat
```

### What it does:
- ✅ **Python Check**: Verifies Python 3.11+ installation
- ✅ **Virtual Environment**: Creates isolated Python environment
- ✅ **Full Installation**: Installs to `%LOCALAPPDATA%\ScalPDF`
- ✅ **Start Menu**: Creates Start Menu shortcuts
- ✅ **Desktop Shortcut**: Adds desktop shortcut
- ✅ **PATH Integration**: Adds to system PATH
- ✅ **Icon Creation**: Generates application icon
- ✅ **Uninstaller**: Creates uninstaller in Start Menu

### Usage after installation:
- **GUI**: Find "ScalPDF" in Start Menu or Desktop
- **CLI**: Open Command Prompt → "ScalPDF CLI"
- **Uninstall**: Find "Uninstall ScalPDF" in Start Menu

## 🔧 Installation Details

### Linux Installation Locations:
```
~/.local/share/scalpdf/          # Application files
~/.local/bin/scalpdf             # GUI launcher
~/.local/bin/scalpdf-cli         # CLI launcher
~/.local/bin/scalpdf-uninstall   # Uninstaller
~/.local/share/applications/     # Desktop entry
~/.local/share/icons/            # Application icon
```

### Windows Installation Locations:
```
%LOCALAPPDATA%\ScalPDF\          # Application files
%APPDATA%\Microsoft\Windows\Start Menu\Programs\  # Shortcuts
%USERPROFILE%\Desktop\           # Desktop shortcut
```

## 🚀 Features Installed

### Complete Application:
- **GUI Application** with full PySide6 interface
- **CLI Tools** for batch operations
- **PDF Viewing** with zoom, navigation, thumbnails
- **Annotations** (highlights, notes, comments)
- **PDF Editing** (merge, split, reorder, delete pages)
- **Compression** with quality presets
- **Encryption** with AES-256-GCM + Argon2id
- **Desktop Integration** (app menu, file associations)

### Security Features:
- **Offline Operation** - No internet connectivity
- **Local Processing** - All operations on your device
- **Encrypted Storage** - Secure password-based encryption
- **Memory Protection** - Keys wiped after use
- **No Telemetry** - Zero data collection

## 🔍 Troubleshooting

### Linux Issues:

**Missing system dependencies:**
```bash
# Ubuntu/Debian
sudo apt install python3-dev libxcb-xinerama0 libgl1-mesa-glx

# Fedora
sudo dnf install python3-devel libxcb mesa-libGL

# Arch
sudo pacman -S python libxcb mesa
```

**GUI not starting:**
```bash
# Check display
echo $DISPLAY

# Install additional Qt packages
sudo apt install qt6-base-dev  # Ubuntu
sudo dnf install qt6-qtbase-devel  # Fedora
```

**Permission issues:**
```bash
# Fix permissions
chmod +x ~/.local/bin/scalpdf
xhost +local:
```

### Windows Issues:

**Python not found:**
- Install Python 3.11+ from [python.org](https://python.org)
- Check "Add Python to PATH" during installation
- Restart Command Prompt after installation

**PowerShell execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Missing Visual C++ redistributables:**
- Install Microsoft Visual C++ Redistributable
- Available from Microsoft Download Center

**GUI not starting:**
- Check Windows Defender/Antivirus settings
- Ensure Python and pip are in PATH
- Try running as Administrator

## 🧪 Testing Installation

### Verify Installation:
```bash
# Linux
scalpdf --version
scalpdf-cli --help

# Windows (Command Prompt)
ScalPDF-CLI --help
```

### Test GUI:
```bash
# Linux
scalpdf

# Windows
# Use Start Menu or Desktop shortcut
```

### Test Dependencies:
```python
python -c "
import PySide6; print('✅ GUI OK')
import fitz; print('✅ PDF processing OK') 
import cryptography; print('✅ Encryption OK')
print('✅ Installation successful!')
"
```

## 🔄 Updating

### Linux:
```bash
# Uninstall old version
scalpdf-uninstall

# Install new version
./install_linux.sh
```

### Windows:
1. Use "Uninstall ScalPDF" from Start Menu
2. Run new installer

## 📞 Support

If you encounter issues:

1. **Check Requirements**: Python 3.11+, system dependencies
2. **Check Logs**: Installation output for error messages
3. **Test Dependencies**: Run dependency test commands above
4. **File Issues**: Report problems on GitHub with:
   - Operating system and version
   - Python version
   - Error messages
   - Installation log output

## 🎯 What's Next

After installation, you can:

1. **Open PDFs**: Drag and drop or File → Open
2. **Try Encryption**: Security → Encrypt PDF
3. **Test Compression**: Tools → Compress PDF
4. **Add Annotations**: Use annotation tools panel
5. **Use CLI**: Explore batch operations with CLI

The installers provide a complete, production-ready installation of ScalPDF with full desktop integration!
