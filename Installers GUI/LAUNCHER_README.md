# ScalPDF Standalone Launcher

**🚀 Double-click to launch ScalPDF without any terminal or command-line knowledge required!**

## 📦 Pre-Built Application Launcher

The ScalPDF Standalone Launcher is a complete GUI application that allows you to:
- **Launch ScalPDF** if already installed
- **Install ScalPDF** using multiple methods
- **Build packages** for distribution
- **Run tests** to verify functionality
- **Access help and documentation**

All without ever opening a terminal or typing commands!

## 🎯 How to Use

### Method 1: Python Launcher (Recommended)
```bash
# Simply double-click this file in your file manager:
scalpdf_launcher.py
```

### Method 2: Shell Script (Alternative)
```bash
# Double-click this file if the Python launcher doesn't work:
launch-scalpdf.sh
```

### Method 3: Desktop File (System Integration)
```bash
# Copy to desktop or applications folder:
ScalPDF-Launcher.desktop
```

## 🖥️ What You'll See

When you launch the standalone launcher, you'll get a beautiful GUI with:

### 📊 Main Dashboard
- **Installation Status** - Shows if ScalPDF is already installed
- **System Information** - Displays your OS and architecture
- **Large Action Buttons** - Launch or Install with one click

### 🚀 Launch Options
If ScalPDF is installed:
- **🚀 Launch ScalPDF** - Start the application immediately
- **🔄 Reinstall** - Update or reinstall ScalPDF
- **❓ Help** - Get help and documentation

### 📦 Installation Options
If ScalPDF is not installed:
- **🚀 Smart Install** - Automatically choose the best method
- **📦 AppImage** - Portable, no installation required
- **🔧 .deb Package** - Native Ubuntu/Debian integration
- **📱 Snap Package** - Universal, sandboxed installation
- **🎨 Package Installer GUI** - Advanced options

### 🛠️ Advanced Features
- **Build Packages** - Create AppImage, .deb, or Snap packages
- **Run Tests** - Verify system compatibility
- **Package Installer** - Open advanced installer GUI
- **Open Project Folder** - Browse project files
- **About & Help** - Documentation and support

## 🎨 Screenshots

The launcher provides a modern, professional interface with:
- **Clean Design** - Easy to understand and use
- **Progress Tracking** - See what's happening during installation
- **Status Updates** - Real-time feedback on operations
- **Tabbed Interface** - Organized advanced options
- **Help Integration** - Built-in documentation

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ or any Linux with GUI
- **Python**: 3.11+ (usually pre-installed)
- **Display**: X11 or Wayland desktop environment
- **Memory**: 256MB RAM for launcher
- **Storage**: 50MB for launcher files

### What's Included
The launcher automatically handles:
- ✅ **System Detection** - Identifies your OS and capabilities
- ✅ **Dependency Checking** - Verifies requirements
- ✅ **Package Building** - Creates installation packages
- ✅ **Installation** - Handles the complete setup process
- ✅ **Desktop Integration** - Adds menu entries and file associations
- ✅ **Error Handling** - Provides helpful error messages

## 🚀 Quick Start Guide

### For Complete Beginners

1. **Navigate to the project folder**
   - Open your file manager
   - Go to the `scal-pdf/Installers GUI/` folder

2. **Double-click the launcher**
   - Try `scalpdf_launcher.py` first
   - If that doesn't work, try `launch-scalpdf.sh`

3. **Follow the GUI**
   - The interface will guide you through everything
   - Click "Install ScalPDF" if not installed
   - Click "Launch ScalPDF" if already installed

4. **Choose installation method**
   - "Smart Install" is recommended for most users
   - It will automatically pick the best option

5. **Wait for completion**
   - Progress bars show the status
   - You'll get a success message when done

6. **Launch ScalPDF**
   - Click the launch button
   - ScalPDF will open as a separate application

### For Advanced Users

The launcher also provides:
- **Individual package builders** for specific formats
- **Test suite** for system validation
- **Advanced installer GUI** for custom options
- **Direct access** to all project tools

## 🛡️ Security & Privacy

The standalone launcher maintains ScalPDF's security principles:
- ✅ **Offline Operation** - No internet required after download
- ✅ **No Telemetry** - No data collection or tracking
- ✅ **Local Processing** - Everything happens on your computer
- ✅ **Open Source** - Code is transparent and auditable

## 🔍 Troubleshooting

### Common Issues

**"Python not found"**
```bash
# Install Python 3
sudo apt update
sudo apt install python3 python3-tk
```

**"No display detected"**
- Make sure you're running in a desktop environment
- Don't run from SSH without X11 forwarding

**"Permission denied"**
```bash
# Make files executable
chmod +x scalpdf_launcher.py
chmod +x launch-scalpdf.sh
```

**"Import errors"**
```bash
# Install GUI libraries
sudo apt install python3-tk
```

### Getting Help

1. **Use the built-in help** - Click the "Help" button in the launcher
2. **Run tests** - Use the "Run Tests" feature to diagnose issues
3. **Check system info** - The launcher shows your system details
4. **Visit GitHub** - https://github.com/yashrajy264/scal-pdf/issues

## 📁 File Structure

```
Installers GUI/
├── scalpdf_launcher.py          # 🚀 Main launcher (double-click this!)
├── launch-scalpdf.sh           # 🔧 Shell script alternative
├── ScalPDF-Launcher.desktop    # 🖥️ Desktop integration file
├── LAUNCHER_README.md          # 📄 This documentation
├── build_appimage.py           # 📦 AppImage builder
├── build_deb.py               # 📦 .deb builder
├── build_snap.py              # 📦 Snap builder
├── package_installer.py       # 🎨 Advanced installer GUI
├── smart_launcher.py          # 🧠 Smart detection system
├── test_packages.py           # 🧪 Test suite
└── README.md                  # 📚 Complete documentation
```

## 🎯 Use Cases

### For End Users
- **Just want to use ScalPDF**: Double-click `scalpdf_launcher.py`
- **First time installation**: Use "Smart Install" option
- **Prefer specific format**: Choose AppImage, .deb, or Snap

### For System Administrators
- **Deploy to multiple machines**: Build .deb packages
- **Portable deployment**: Create AppImages
- **Enterprise security**: Use Snap packages

### For Developers
- **Test builds**: Use the test suite
- **Create packages**: Use individual builders
- **Debug issues**: Access advanced tools

## 🔄 Updates

To update the launcher and ScalPDF:

1. **Pull latest changes**:
   ```bash
   cd scal-pdf
   git pull origin main
   ```

2. **Relaunch the standalone launcher**
   - It will automatically detect updates
   - Reinstall if needed using the GUI

## 📞 Support

- **Built-in Help**: Click "Help" in the launcher
- **Documentation**: See README.md files
- **Issues**: https://github.com/yashrajy264/scal-pdf/issues
- **Discussions**: GitHub Discussions tab

---

**🎉 Enjoy using ScalPDF with the easiest installation experience possible!**

*No terminal knowledge required - just double-click and go!* 🚀
