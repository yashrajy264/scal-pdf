# 🐧 ScalPDF Linux - Ready to Use!

## 🚀 **Quick Start**

### **Method 1: Direct Python Execution (Recommended)**
```bash
# In your VM terminal:
cd scal-pdf/Installers\ GUI/
python3 ScalPDF-Linux.py
```

### **Method 2: Make it Executable**
```bash
# In your VM terminal:
cd scal-pdf/Installers\ GUI/
chmod +x ScalPDF-Linux.py
./ScalPDF-Linux.py
```

## 🔧 **What This Does**

✅ **Auto-installs dependencies** - No manual pip install needed!  
✅ **Works on any Linux** - Ubuntu, Debian, CentOS, etc.  
✅ **Full GUI application** - Tkinter-based, works everywhere  
✅ **All PDF features** - View, merge, split, compress, encrypt  
✅ **Completely offline** - No internet required after first run  

## 📦 **Dependencies Auto-Installed**

The application will automatically install these if missing:
- `PyMuPDF` - PDF processing and viewing
- `Pillow` - Image handling  
- `pikepdf` - Advanced PDF operations
- `cryptography` - Encryption support
- `argon2-cffi` - Secure key derivation

## 🎯 **Features**

### **PDF Viewer**
- 📖 View PDFs with zoom and navigation
- 🔍 Zoom in/out and fit to width
- ⏮️⏭️ Page navigation controls
- 📊 Document information panel

### **PDF Operations**
- 🔀 **Merge** multiple PDFs
- ✂️ **Split** PDFs by page range
- 🗜️ **Compress** PDFs to reduce size
- 🔒 **Encrypt** with AES-256 encryption
- 🔓 **Decrypt** password-protected PDFs

### **Security & Privacy**
- 🛡️ **Completely offline** - no internet required
- 🔐 **AES-256 encryption** for sensitive documents
- 🚫 **No telemetry** or data collection
- 💾 **Local processing** only

## 🖥️ **System Requirements**

- **Linux** (any distribution)
- **Python 3.6+** (usually pre-installed)
- **Internet connection** (only for first-time dependency installation)
- **GUI environment** (X11, Wayland)

## 🆘 **Troubleshooting**

### **If you get "python3: command not found":**
```bash
# Ubuntu/Debian:
sudo apt update && sudo apt install python3 python3-pip python3-tk

# CentOS/RHEL:
sudo yum install python3 python3-pip tkinter

# Arch Linux:
sudo pacman -S python python-pip tk
```

### **If GUI doesn't appear:**
```bash
# Make sure you have GUI support:
echo $DISPLAY

# If empty, you might be in a headless environment
# Use X11 forwarding if connecting via SSH:
ssh -X username@hostname
```

### **Permission denied:**
```bash
chmod +x ScalPDF-Linux.py
```

## 🎉 **Success!**

Once running, you'll see:
- 🔒 **ScalPDF Linux** window with modern GUI
- 📂 **Open button** to load PDF files
- 🛠️ **Toolbar** with all PDF operations
- ✅ **Status bar** showing dependency status

**No more "cannot execute binary file" errors!** 🎊

---

**Built for Linux • Privacy-First • Completely Offline**
