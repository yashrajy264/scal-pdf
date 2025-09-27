# ScalPDF GUI Installers

Professional graphical installers designed for normal consumers who want an easy, user-friendly installation experience.

## 🎯 **For Normal Users**

These GUI installers provide a **Windows/Mac-style installation experience** with:
- ✅ **Point-and-click interface** - No command line needed
- ✅ **Visual progress tracking** - See exactly what's happening
- ✅ **Customizable options** - Choose what gets installed
- ✅ **Error handling** - Clear error messages and solutions
- ✅ **Professional appearance** - Modern, clean interface

## 🚀 **Quick Start**

### **Cross-Platform Installer (Recommended)**
```bash
python3 gui_installer.py
```
*Automatically detects your platform and runs the appropriate installer*

### **Windows-Specific Installer**
```bash
python windows_installer.py
```
*Advanced Windows installer with native Windows features*

### **Linux-Specific Installer**
```bash
python3 linux_installer.py
```
*Linux installer with distribution-specific package management*

## 📱 **Installer Features**

### **Universal GUI Installer (`gui_installer.py`)**
- **Cross-platform compatibility** (Windows, Linux, macOS)
- **Simple, clean interface** suitable for all users
- **Automatic platform detection**
- **Basic installation options**
- **Progress tracking with detailed logs**

### **Windows Advanced Installer (`windows_installer.py`)**
- **Native Windows look and feel** (Vista/Windows 10+ theme)
- **Windows-specific features**:
  - Start Menu integration
  - Windows registry entries
  - File associations (open PDFs with ScalPDF)
  - Add/Remove Programs integration
  - User vs System installation options
- **Professional installer wizard** interface
- **Administrator privilege handling**
- **Windows shortcuts and icons**

### **Linux Advanced Installer (`linux_installer.py`)**
- **Distribution detection** (Ubuntu, Fedora, Arch, etc.)
- **Package manager integration**:
  - Automatic system dependency installation
  - Distribution-specific package commands
- **Desktop environment integration**:
  - Application menu entries
  - Desktop shortcuts
  - MIME type associations
- **User vs System installation**
- **PATH integration for command-line tools**

## 🖥️ **Installation Options**

### **Installation Types**
- **User Installation** (Recommended)
  - Installs to user directory
  - No administrator rights required
  - Available only to current user
  
- **System Installation**
  - Installs to system directory
  - Requires administrator/root privileges
  - Available to all users

### **Customization Options**
- ✅ **Desktop Shortcut** - Quick access from desktop
- ✅ **Start Menu/App Menu** - Integration with system menus
- ✅ **Command Line Tools** - Add `scalpdf` commands to PATH
- ✅ **File Associations** - Open PDFs with ScalPDF by default
- ✅ **System Dependencies** - Auto-install required libraries

## 📋 **What Gets Installed**

### **Core Application**
- **ScalPDF GUI** - Full-featured PDF management interface
- **CLI Tools** - Command-line utilities for batch operations
- **Python Environment** - Isolated virtual environment with all dependencies

### **Desktop Integration**
- **Application Shortcuts** - Desktop and menu shortcuts
- **File Associations** - PDF files open with ScalPDF
- **System Registration** - Proper uninstaller and system integration

### **Dependencies**
- **Python Packages** - PySide6, PyMuPDF, pikepdf, cryptography, etc.
- **System Libraries** - Qt, graphics libraries, fonts (Linux)
- **Runtime Components** - All required components for offline operation

## 🎨 **User Interface**

### **Modern Design**
- **Clean, professional appearance**
- **Progress indicators** with real-time updates
- **Detailed installation logs** for troubleshooting
- **Help system** with context-sensitive information

### **Platform-Native Look**
- **Windows**: Vista/Windows 10+ theme with native controls
- **Linux**: GTK/Qt theme integration
- **Cross-platform**: Consistent experience across platforms

## 🔧 **Installation Process**

### **Step-by-Step Process**
1. **System Check** - Verify Python and system requirements
2. **Dependency Installation** - Install system packages (if selected)
3. **File Copying** - Copy application files to destination
4. **Environment Setup** - Create Python virtual environment
5. **Package Installation** - Install Python dependencies
6. **Integration** - Create shortcuts, menu entries, file associations
7. **Testing** - Verify installation works correctly
8. **Completion** - Show success message and usage instructions

### **Error Handling**
- **Clear error messages** with suggested solutions
- **Detailed logs** for troubleshooting
- **Graceful fallbacks** when optional features fail
- **Rollback capability** for failed installations

## 🛡️ **Security & Privacy**

### **Safe Installation**
- **No internet required** after initial download
- **Local processing only** - No data sent anywhere
- **Isolated environment** - Uses Python virtual environment
- **User-level permissions** - No unnecessary privilege escalation

### **Privacy Maintained**
- **No telemetry** or usage tracking
- **No registration** or account creation
- **Offline operation** - Works completely offline
- **Local storage** - All data stays on your device

## 🚀 **Usage Examples**

### **For Home Users**
```bash
# Download ScalPDF
git clone https://github.com/yashrajy264/scal-pdf.git
cd scal-pdf

# Run GUI installer
python3 "Installers GUI/gui_installer.py"

# Follow the wizard:
# 1. Choose installation location
# 2. Select options (shortcuts, menu entries)
# 3. Click "Install"
# 4. Wait for completion
# 5. Start using ScalPDF!
```

### **For IT Administrators**
```bash
# Windows deployment
python "Installers GUI/windows_installer.py"
# Choose "Install for all users"
# Customize options for organization needs

# Linux deployment
sudo python3 "Installers GUI/linux_installer.py"
# Choose "System-wide installation"
# Enable system dependency installation
```

## 🔍 **Troubleshooting**

### **Common Issues**

**"Python not found"**
- Install Python 3.11+ from python.org
- Make sure Python is in PATH

**"tkinter not available"**
- Linux: `sudo apt install python3-tk`
- Windows: Reinstall Python with tkinter

**"Permission denied"**
- Choose user installation instead of system
- Or run with appropriate privileges

**"Dependencies failed"**
- Check internet connection
- Try manual dependency installation

### **Getting Help**
- **Installation logs** - Check detailed logs in installer
- **System requirements** - Verify Python 3.11+ and system deps
- **GitHub Issues** - Report problems with logs
- **Documentation** - Check main README.md

## 🎯 **Perfect For**

### **Home Users**
- Want easy, click-to-install experience
- Don't want to use command line
- Need desktop integration (shortcuts, menus)
- Want professional-looking installer

### **Small Businesses**
- Need to deploy to multiple computers
- Want consistent installation experience
- Require system-wide installation options
- Need uninstaller for easy removal

### **Educational Institutions**
- Simple deployment for students/staff
- System-wide installation for shared computers
- Easy uninstallation for lab management
- Professional appearance for institutional use

## 📊 **Comparison**

| Feature | GUI Installer | Command Line | Manual Install |
|---------|---------------|--------------|----------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Visual Feedback** | ✅ | ❌ | ❌ |
| **Error Handling** | ✅ | ⭐ | ❌ |
| **Desktop Integration** | ✅ | ⭐ | ❌ |
| **Customization** | ✅ | ✅ | ✅ |
| **Automation** | ⭐ | ✅ | ❌ |

The GUI installers provide the **best experience for normal consumers** who want a simple, reliable way to install ScalPDF with full desktop integration and professional appearance.

---

**Ready to install ScalPDF?** Just run `python3 gui_installer.py` and follow the wizard! 🚀
