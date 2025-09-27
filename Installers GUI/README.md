# ScalPDF Package System

Complete package management system for ScalPDF with multiple installation formats and a modern GUI installer.

## 🚀 Quick Start

### For End Users (Ubuntu 24.04)

**Option 1: Smart Launcher (Recommended)**
```bash
cd scal-pdf
python3 "Installers GUI/smart_launcher.py"
```

**Option 2: GUI Package Installer**
```bash
cd scal-pdf
python3 "Installers GUI/package_installer.py"
```

**Option 3: Build and Install Automatically**
```bash
cd scal-pdf
python3 "Installers GUI/smart_launcher.py" --build
```

## 📦 Available Package Formats

### 1. AppImage (Universal Linux)
- **File**: `ScalPDF-x86_64.AppImage`
- **Target**: All Linux distributions
- **Advantages**: Portable, no installation required
- **Usage**: `chmod +x ScalPDF-x86_64.AppImage && ./ScalPDF-x86_64.AppImage`

### 2. .deb Package (Ubuntu/Debian)
- **File**: `scalpdf_1.0.0_amd64.deb`
- **Target**: Ubuntu 24.04+, Debian-based distributions
- **Advantages**: Native integration, dependency management
- **Usage**: `sudo dpkg -i scalpdf_1.0.0_amd64.deb`

### 3. Snap Package (Universal Linux)
- **File**: `scalpdf_1.0.0_amd64.snap`
- **Target**: Any Linux with Snap support
- **Advantages**: Sandboxed, automatic updates
- **Usage**: `sudo snap install scalpdf_1.0.0_amd64.snap --dangerous`

## 🛠️ Building Packages

### Build All Packages
```bash
# Using GUI installer
python3 "Installers GUI/package_installer.py"
# Click "Build Packages" button

# Using individual builders
python3 "Installers GUI/build_appimage.py"
python3 "Installers GUI/build_deb.py"
python3 "Installers GUI/build_snap.py"
```

### Build Requirements

**For AppImage:**
- Python 3.11+
- Internet connection (to download AppImage tools)
- All Python dependencies

**For .deb Package:**
- `dpkg-dev` package
- `gzip` command
- Ubuntu/Debian system (recommended)

**For Snap Package:**
- `snapcraft` installed (`sudo snap install snapcraft --classic`)
- Optional: Docker or LXD for containerized builds

## 🎯 Tools Overview

### 1. Smart Launcher (`smart_launcher.py`)
Automatically detects and launches ScalPDF using the best available method.

**Features:**
- Auto-detects installed versions
- Prioritizes system installations
- Falls back to portable formats
- Launches package builder if needed

**Usage:**
```bash
python3 smart_launcher.py           # Auto-launch ScalPDF
python3 smart_launcher.py --build   # Build packages
python3 smart_launcher.py --info    # Show system info
python3 smart_launcher.py --list    # List launch methods
```

### 2. Package Installer GUI (`package_installer.py`)
Modern GUI for building and installing ScalPDF packages.

**Features:**
- System detection and compatibility checking
- Package building with progress tracking
- Installation with multiple formats
- Desktop integration setup
- Installation testing

### 3. Package Builders

#### AppImage Builder (`build_appimage.py`)
Creates portable AppImage packages.

**Output:**
- `build/ScalPDF-x86_64.AppImage` - Portable executable
- `build/ScalPDF-x86_64.md` - Usage instructions

#### .deb Builder (`build_deb.py`)
Creates native Ubuntu/Debian packages.

**Output:**
- `build/scalpdf_1.0.0_amd64.deb` - Debian package
- `build/scalpdf_1.0.0_amd64.md` - Installation guide

#### Snap Builder (`build_snap.py`)
Creates Snap packages for universal Linux distribution.

**Output:**
- `build/scalpdf_1.0.0_amd64.snap` - Snap package
- `build/scalpdf_1.0.0_amd64.md` - Installation guide

### 4. Test Suite (`test_packages.py`)
Comprehensive testing for all packages and tools.

**Tests:**
- Build environment validation
- Package builder functionality
- GUI installer testing
- Smart launcher testing
- Existing package validation

**Usage:**
```bash
python3 test_packages.py
```

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 24.04+ or compatible Linux distribution
- **Python**: 3.11+
- **Architecture**: x86_64 (amd64)
- **Display**: X11 or Wayland
- **Memory**: 512MB RAM
- **Storage**: 100MB free space

### Recommended Requirements
- **OS**: Ubuntu 24.04 LTS
- **Python**: 3.11+
- **Memory**: 2GB RAM
- **Storage**: 1GB free space
- **Network**: For downloading build tools (build-time only)

### Dependencies

**Runtime Dependencies:**
```
python3 (>= 3.11)
python3-tk
libgl1-mesa-dri
libxcb-xinerama0
libfontconfig1
libglib2.0-0
```

**Build Dependencies:**
```
python3-dev
python3-pip
python3-venv
build-essential
libffi-dev
```

**Optional Build Tools:**
```
dpkg-dev          # For .deb packages
snapcraft         # For Snap packages
docker            # For containerized builds
```

## 📋 Installation Methods Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **AppImage** | ✅ Portable<br>✅ No root required<br>✅ Works everywhere | ❌ Manual updates<br>❌ No system integration | Testing, portable use |
| **.deb Package** | ✅ Native integration<br>✅ Dependency management<br>✅ System updates | ❌ Ubuntu/Debian only<br>❌ Requires root | Ubuntu/Debian users |
| **Snap Package** | ✅ Universal Linux<br>✅ Sandboxed<br>✅ Auto-updates | ❌ Larger size<br>❌ Snap dependency | Security-focused users |

## 🛡️ Security Features

### Package Security
- **Code Signing**: All packages include checksums
- **Dependency Isolation**: Each package includes its dependencies
- **Minimal Permissions**: Packages request only necessary permissions
- **Offline Operation**: No network access required after installation

### Application Security
- **AES-256-GCM Encryption**: Military-grade document encryption
- **Argon2id Key Derivation**: Secure password-based encryption
- **No Telemetry**: Complete offline operation
- **Memory Protection**: Secure key handling and memory wiping

## 🔍 Troubleshooting

### Common Issues

**"Package build failed"**
```bash
# Check system requirements
python3 "Installers GUI/test_packages.py"

# Install missing dependencies
sudo apt update
sudo apt install python3-dev python3-pip python3-venv build-essential
```

**"AppImage won't run"**
```bash
# Make executable
chmod +x ScalPDF-x86_64.AppImage

# Check dependencies
ldd ScalPDF-x86_64.AppImage
```

**".deb installation failed"**
```bash
# Fix dependencies
sudo apt-get install -f

# Check package
dpkg-deb --info scalpdf_1.0.0_amd64.deb
```

**"Snap installation failed"**
```bash
# Check snap system
sudo systemctl status snapd

# Install with force
sudo snap install scalpdf_1.0.0_amd64.snap --dangerous --devmode
```

### Getting Help

1. **Run Tests**: `python3 "Installers GUI/test_packages.py"`
2. **Check System**: `python3 "Installers GUI/smart_launcher.py" --info`
3. **View Logs**: Check `build/test_report.json` for detailed information
4. **GitHub Issues**: Report issues at https://github.com/yashrajy264/scal-pdf/issues

## 📁 File Structure

```
Installers GUI/
├── build_appimage.py      # AppImage builder
├── build_deb.py          # .deb package builder
├── build_snap.py         # Snap package builder
├── package_installer.py  # GUI installer
├── smart_launcher.py     # Smart launcher
├── test_packages.py      # Test suite
└── README.md            # This file

build/                    # Build outputs (created during build)
├── appimage/            # AppImage build files
├── deb/                 # .deb build files
├── snap/                # Snap build files
├── ScalPDF-x86_64.AppImage
├── scalpdf_1.0.0_amd64.deb
├── scalpdf_1.0.0_amd64.snap
└── test_report.json     # Test results
```

## 🎯 Usage Examples

### For Developers
```bash
# Test everything
python3 "Installers GUI/test_packages.py"

# Build all packages
python3 "Installers GUI/package_installer.py"

# Test specific package
chmod +x build/ScalPDF-x86_64.AppImage
./build/ScalPDF-x86_64.AppImage
```

### For End Users
```bash
# Easy installation
python3 "Installers GUI/smart_launcher.py"

# Manual package selection
python3 "Installers GUI/package_installer.py"

# Direct AppImage use
chmod +x ScalPDF-x86_64.AppImage
./ScalPDF-x86_64.AppImage
```

### For System Administrators
```bash
# System-wide .deb installation
sudo dpkg -i scalpdf_1.0.0_amd64.deb
sudo apt-get install -f

# Snap installation for all users
sudo snap install scalpdf_1.0.0_amd64.snap --dangerous

# Verify installation
scalpdf --version
```

## 🔄 Updates and Maintenance

### Updating ScalPDF

**AppImage**: Download new version and replace old file
**Debian Package**: `sudo apt update && sudo apt upgrade scalpdf`
**Snap Package**: `sudo snap refresh scalpdf` (if from store)

### Uninstalling ScalPDF

**AppImage**: Simply delete the file
**Debian Package**: `sudo apt remove scalpdf`
**Snap Package**: `sudo snap remove scalpdf`

## 📞 Support

- **Documentation**: See main README.md
- **Issues**: https://github.com/yashrajy264/scal-pdf/issues
- **Security**: Report security issues privately via GitHub
- **License**: MIT License (see LICENSE file)

---

**ScalPDF**: Secure, offline PDF management for everyone. 🛡️📄
