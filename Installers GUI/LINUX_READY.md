# 🐧 ScalPDF for Linux - Ready to Use!

## ❌ **Binary Compatibility Issue Fixed!**

The `ScalPDF` binary was built for macOS and won't work on Linux. Here are the **Linux-compatible solutions**:

## 🚀 **Linux Solutions (Choose One)**

### **🎯 Option 1: Auto-Installing Launcher (Recommended)**
```bash
# Just run this - it handles everything automatically!
./run-scalpdf-linux.sh
```
**What it does:**
- ✅ Checks Python and tkinter
- ✅ Installs missing dependencies automatically
- ✅ Launches ScalPDF with full functionality
- ✅ Works on Ubuntu, Fedora, Arch, and other Linux distros

### **🔧 Option 2: Python Launcher with Auto-Install**
```bash
# Run the Python auto-installer
python3 ScalPDF-Linux
```
**What it does:**
- ✅ Checks and installs PyMuPDF, Pillow, pikepdf, cryptography
- ✅ Automatically handles pip installation
- ✅ Launches the portable ScalPDF application

### **📱 Option 3: Manual Dependency Install**
```bash
# Install dependencies manually
pip install --user PyMuPDF Pillow pikepdf cryptography

# Then run the portable version
python3 ScalPDF-Portable.py
```

## 🎯 **Quick Start for Your VM**

### **Super Simple (One Command):**
```bash
cd "scal-pdf/Installers GUI"
./run-scalpdf-linux.sh
```

### **If Permission Denied:**
```bash
chmod +x run-scalpdf-linux.sh
chmod +x ScalPDF-Linux
./run-scalpdf-linux.sh
```

## ✨ **What You'll Get**

### **🔒 Complete PDF Application:**
- **PDF Viewing** - Multi-page navigation, zoom, rotation
- **PDF Editing** - Merge, split, extract pages
- **PDF Security** - AES-256 encryption/decryption  
- **PDF Compression** - Reduce file sizes
- **Modern GUI** - Professional interface with panels
- **Keyboard Shortcuts** - Full desktop experience

### **🛡️ Linux-Optimized Features:**
- **Auto-dependency installation** - No manual setup
- **Distribution detection** - Works on Ubuntu, Fedora, Arch
- **Package manager integration** - Uses apt, dnf, pacman
- **User-space installation** - No root required for Python packages
- **Error handling** - Clear messages and solutions

## 🔧 **System Requirements**

### **Minimum:**
- **OS**: Any Linux distribution with GUI
- **Python**: 3.7+ (usually pre-installed)
- **Display**: X11 or Wayland desktop environment
- **Memory**: 512 MB RAM
- **Storage**: 100 MB free space

### **Dependencies (Auto-Installed):**
- **PyMuPDF** - PDF processing
- **Pillow** - Image handling
- **pikepdf** - Advanced PDF operations
- **cryptography** - Encryption support
- **tkinter** - GUI framework (system package)

## 🎊 **Why This Works Better**

### **❌ Binary Issues (Fixed):**
- macOS ARM64 binary won't run on Linux x86_64
- Cross-compilation complexity
- Architecture mismatches

### **✅ Python Solution (Better):**
- **Universal compatibility** - works on any Linux
- **Auto-dependency handling** - installs what's needed
- **Better error messages** - tells you exactly what to do
- **Easier maintenance** - no binary compatibility issues
- **Smaller download** - dependencies installed as needed

## 🆘 **Troubleshooting**

### **"Permission denied":**
```bash
chmod +x run-scalpdf-linux.sh
chmod +x ScalPDF-Linux
```

### **"Python not found":**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-tk

# Fedora
sudo dnf install python3 python3-pip python3-tkinter

# Arch
sudo pacman -S python python-pip tk
```

### **"pip install failed":**
```bash
# Upgrade pip
python3 -m pip install --upgrade pip --user

# Install manually
python3 -m pip install --user PyMuPDF Pillow pikepdf cryptography
```

### **"GUI doesn't appear":**
```bash
# Check display
echo $DISPLAY

# Install GUI libraries
sudo apt install python3-tk libgl1-mesa-dri
```

## 📋 **File Guide**

| File | Purpose | Usage |
|------|---------|-------|
| `run-scalpdf-linux.sh` | **Auto-installer script** | `./run-scalpdf-linux.sh` |
| `ScalPDF-Linux` | **Python auto-installer** | `python3 ScalPDF-Linux` |
| `ScalPDF-Portable.py` | **Main application** | `python3 ScalPDF-Portable.py` |
| ~~`ScalPDF`~~ | ❌ macOS binary (won't work) | Don't use on Linux |

## 🎉 **Success Path**

1. **Update repository**: `git pull origin main`
2. **Navigate to folder**: `cd "scal-pdf/Installers GUI"`
3. **Run auto-installer**: `./run-scalpdf-linux.sh`
4. **Enjoy ScalPDF**: Complete PDF application launches!

**The auto-installer handles everything - dependencies, GUI setup, and launching ScalPDF with full functionality!** 🚀

---

**ScalPDF - Now Linux-Ready with Auto-Installation!** 🐧🔒
