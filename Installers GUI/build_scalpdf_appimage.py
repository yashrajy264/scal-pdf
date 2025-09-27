#!/usr/bin/env python3
"""
ScalPDF AppImage Builder - Direct Application
Creates a single AppImage that runs ScalPDF directly (not an installer).
"""

import os
import sys
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
import stat

class ScalPDFAppImageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build" / "scalpdf_appimage"
        self.appdir = self.build_dir / "ScalPDF.AppDir"
        
        # AppImage tools URLs
        self.appimagetool_url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        
    def setup_build_environment(self):
        """Setup the build environment."""
        print("🔧 Setting up ScalPDF AppImage build environment...")
        
        # Clean and create build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create AppDir structure
        self.appdir.mkdir(exist_ok=True)
        (self.appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
        (self.appdir / "usr" / "lib").mkdir(parents=True, exist_ok=True)
        (self.appdir / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
        (self.appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(parents=True, exist_ok=True)
        
        print("✅ Build environment ready")
        
    def download_appimagetool(self):
        """Download AppImage build tool."""
        print("📥 Downloading AppImage tools...")
        
        tools_dir = self.build_dir / "tools"
        tools_dir.mkdir(exist_ok=True)
        
        # Download appimagetool
        appimagetool_path = tools_dir / "appimagetool"
        if not appimagetool_path.exists():
            print("  📦 Downloading appimagetool...")
            urllib.request.urlretrieve(self.appimagetool_url, appimagetool_path)
            appimagetool_path.chmod(0o755)
        
        print("✅ Tools downloaded")
        return appimagetool_path
        
    def create_python_environment(self):
        """Create embedded Python environment."""
        print("🐍 Creating embedded Python environment...")
        
        # Create virtual environment
        venv_dir = self.appdir / "usr" / "python"
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_dir)
        ], check=True)
        
        # Install dependencies
        pip_path = venv_dir / "bin" / "pip"
        requirements_file = self.project_root / "requirements.txt"
        
        subprocess.run([
            str(pip_path), "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            str(pip_path), "install", "-r", str(requirements_file)
        ], check=True)
        
        print("✅ Python environment created")
        return venv_dir
        
    def copy_application_files(self):
        """Copy ScalPDF application files."""
        print("📋 Copying ScalPDF application files...")
        
        app_dir = self.appdir / "usr" / "share" / "scalpdf"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Files and directories to copy
        items_to_copy = [
            "main.py", "requirements.txt", "setup.py", "LICENSE", "README.md",
            "core", "ui", "cli", "tests"
        ]
        
        for item in items_to_copy:
            source_item = self.project_root / item
            if source_item.exists():
                dest_item = app_dir / item
                if source_item.is_file():
                    shutil.copy2(source_item, dest_item)
                else:
                    shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
        
        print("✅ Application files copied")
        return app_dir
        
    def create_launcher_script(self, venv_dir, app_dir):
        """Create the main launcher script that runs ScalPDF directly."""
        print("🚀 Creating ScalPDF launcher script...")
        
        launcher_script = self.appdir / "usr" / "bin" / "scalpdf"
        launcher_content = f'''#!/bin/bash
# ScalPDF Direct Launcher - Runs the actual application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
APP_DIR="$SCRIPT_DIR/../share/scalpdf"
PYTHON_DIR="$SCRIPT_DIR/../python"

# Set up environment variables
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="$PYTHON_DIR/lib/python*/site-packages/PySide6/Qt/plugins"
export SCALPDF_APPIMAGE=1

# Change to app directory
cd "$APP_DIR"

# Launch ScalPDF directly (not an installer)
exec "$PYTHON_DIR/bin/python" main.py "$@"
'''
        
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)
        
        print("✅ Launcher script created")
        
    def create_desktop_file(self):
        """Create .desktop file for the application."""
        print("🖥️ Creating desktop file...")
        
        desktop_file = self.appdir / "scalpdf.desktop"
        desktop_content = '''[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Viewer and Editor
Exec=scalpdf
Icon=scalpdf
Categories=Office;Graphics;Viewer;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
Keywords=PDF;viewer;editor;security;encryption;
Terminal=false
'''
        
        desktop_file.write_text(desktop_content)
        
        # Also copy to applications directory
        apps_desktop = self.appdir / "usr" / "share" / "applications" / "scalpdf.desktop"
        shutil.copy2(desktop_file, apps_desktop)
        
        print("✅ Desktop file created")
        
    def create_application_icon(self):
        """Create application icon."""
        print("🎨 Creating application icon...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 256x256 icon
            size = 256
            icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # Background circle with gradient effect
            margin = 20
            # Main circle
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill=(220, 53, 69), outline=(176, 42, 55), width=6)
            
            # Inner highlight circle
            highlight_margin = margin + 15
            draw.ellipse([highlight_margin, highlight_margin, size-highlight_margin, size-highlight_margin], 
                        fill=None, outline=(255, 255, 255, 80), width=3)
            
            # PDF text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 52)
                except:
                    font = ImageFont.load_default()
            
            text = "PDF"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2 - 15
            
            # Text shadow
            draw.text((text_x + 3, text_y + 3), text, fill=(0, 0, 0, 100), font=font)
            # Main text
            draw.text((text_x, text_y), text, fill='white', font=font)
            
            # Security shield
            shield_points = [
                (size//2, margin + 25),
                (size//2 + 30, margin + 42),
                (size//2 + 30, margin + 75),
                (size//2, margin + 92),
                (size//2 - 30, margin + 75),
                (size//2 - 30, margin + 42)
            ]
            draw.polygon(shield_points, fill=(255, 193, 7), outline=(255, 152, 0), width=3)
            
            # Shield highlight
            shield_highlight = [
                (size//2, margin + 30),
                (size//2 + 25, margin + 45),
                (size//2 + 25, margin + 65),
                (size//2, margin + 75),
                (size//2 - 25, margin + 65),
                (size//2 - 25, margin + 45)
            ]
            draw.polygon(shield_highlight, fill=(255, 255, 255, 60))
            
            # Save icon
            icon_path = self.appdir / "scalpdf.png"
            icon.save(icon_path, "PNG")
            
            # Copy to icons directory
            hicolor_icon = self.appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "scalpdf.png"
            shutil.copy2(icon_path, hicolor_icon)
            
            print("✅ Application icon created")
            
        except ImportError:
            print("⚠️ PIL not available, creating simple icon")
            # Create a simple text-based icon
            icon_path = self.appdir / "scalpdf.png"
            # Create a minimal PNG (this is a placeholder)
            with open(icon_path, 'wb') as f:
                # Minimal PNG header for a 1x1 transparent pixel
                f.write(bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a4944415478da6300010000050001'))
        
    def create_apprun_script(self):
        """Create AppRun script."""
        print("🔧 Creating AppRun script...")
        
        apprun_script = self.appdir / "AppRun"
        apprun_content = '''#!/bin/bash
# ScalPDF AppRun Script - Launches the actual application

# Get the directory where this AppImage is mounted
HERE="$(dirname "$(readlink -f "${0}")")"

# Set up environment
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/share/scalpdf:${PYTHONPATH}"

# Qt environment
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/python/lib/python*/site-packages/PySide6/Qt/plugins"
export QT_PLUGIN_PATH="${HERE}/usr/python/lib/python*/site-packages/PySide6/Qt/plugins"

# ScalPDF specific
export SCALPDF_APPIMAGE=1
export SCALPDF_DATA_DIR="${HERE}/usr/share/scalpdf"

# Launch ScalPDF directly
exec "${HERE}/usr/bin/scalpdf" "$@"
'''
        
        apprun_script.write_text(apprun_content)
        apprun_script.chmod(0o755)
        
        print("✅ AppRun script created")
        
    def build_appimage(self, appimagetool_path):
        """Build the final AppImage."""
        print("🔨 Building ScalPDF AppImage...")
        
        output_path = self.build_dir / "ScalPDF-x86_64.AppImage"
        
        # Build AppImage
        env = os.environ.copy()
        env['ARCH'] = 'x86_64'
        
        result = subprocess.run([
            str(appimagetool_path),
            str(self.appdir),
            str(output_path)
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ ScalPDF AppImage created: {output_path}")
            return output_path
        else:
            print(f"❌ AppImage build failed: {result.stderr}")
            return None
            
    def create_usage_info(self, appimage_path):
        """Create usage information file."""
        info_content = f'''# 🚀 ScalPDF - Ready to Use!

## 📦 What You Have

**File**: `{appimage_path.name}`
**Type**: Portable AppImage Application
**Size**: {appimage_path.stat().st_size / (1024*1024):.1f} MB

## 🎯 How to Use

### **Simple Usage:**
```bash
# Make executable (one-time)
chmod +x {appimage_path.name}

# Double-click to run, or:
./{appimage_path.name}
```

### **System Integration (Optional):**
```bash
# Move to applications folder
sudo mv {appimage_path.name} /usr/local/bin/scalpdf

# Now you can run from anywhere
scalpdf
```

## ✨ What This AppImage Does

- ✅ **Launches ScalPDF directly** (not an installer)
- ✅ **Complete PDF viewer and editor**
- ✅ **All features included**: view, annotate, merge, split, encrypt
- ✅ **No installation required** - just run it
- ✅ **Portable** - works on any Linux distribution
- ✅ **Offline** - no internet connection needed

## 🎨 Features Included

### **PDF Viewing:**
- Multi-page viewing with thumbnails
- Zoom, rotate, fit-to-width/height
- Tabbed document interface
- Search within documents

### **PDF Editing:**
- Merge multiple PDFs
- Split PDFs by page ranges
- Reorder and delete pages
- Extract specific pages

### **Annotations:**
- Highlight text
- Add sticky notes
- Underline and strikethrough
- Save annotations in XFDF format

### **Security:**
- AES-256-GCM encryption
- Password-based encryption
- Argon2id key derivation
- Secure document handling

### **Compression:**
- Multiple quality presets
- Image recompression
- File size optimization
- Lossless and lossy options

## 🔧 System Requirements

- **OS**: Any Linux distribution with GUI
- **Architecture**: x86_64 (64-bit)
- **Display**: X11 or Wayland
- **Memory**: 512MB RAM minimum
- **Storage**: 200MB free space

## 🛡️ Security & Privacy

- ✅ **Completely offline** - no internet required
- ✅ **No telemetry** - no data collection
- ✅ **Local processing** - files never leave your computer
- ✅ **Open source** - transparent and auditable

## 🆘 Troubleshooting

### **"Permission denied"**
```bash
chmod +x {appimage_path.name}
```

### **"No such file or directory"**
- Make sure you're in the correct directory
- Check the file exists: `ls -la {appimage_path.name}`

### **GUI doesn't start**
- Make sure you're in a desktop environment
- Check display: `echo $DISPLAY`

### **Missing libraries**
The AppImage includes all dependencies, but if you get errors:
```bash
sudo apt install libgl1-mesa-dri libxcb-xinerama0
```

## 🎉 Enjoy ScalPDF!

This is the complete ScalPDF application packaged as a portable AppImage.
No installation, no setup - just run and use!

**Double-click to start using ScalPDF immediately!** 🚀
'''
        
        info_file = appimage_path.parent / f"README-{appimage_path.stem}.md"
        info_file.write_text(info_content)
        
        return info_file
        
    def build(self):
        """Main build process."""
        print("🏗️ Building ScalPDF AppImage (Direct Application)...")
        print("=" * 60)
        
        try:
            # Setup environment
            self.setup_build_environment()
            
            # Download tools
            appimagetool_path = self.download_appimagetool()
            
            # Create Python environment
            venv_dir = self.create_python_environment()
            
            # Copy application files
            app_dir = self.copy_application_files()
            
            # Create launcher and desktop files
            self.create_launcher_script(venv_dir, app_dir)
            self.create_desktop_file()
            self.create_application_icon()
            self.create_apprun_script()
            
            # Build AppImage
            appimage_path = self.build_appimage(appimagetool_path)
            
            if appimage_path and appimage_path.exists():
                # Make it executable
                appimage_path.chmod(0o755)
                
                # Create usage info
                info_file = self.create_usage_info(appimage_path)
                
                print("\n" + "=" * 60)
                print("🎉 ScalPDF AppImage Build Completed Successfully!")
                print("=" * 60)
                print(f"📦 AppImage: {appimage_path}")
                print(f"📄 Usage Guide: {info_file}")
                print(f"📏 Size: {appimage_path.stat().st_size / (1024*1024):.1f} MB")
                print()
                print("🚀 To use:")
                print(f"   chmod +x {appimage_path.name}")
                print(f"   ./{appimage_path.name}")
                print()
                print("✨ This AppImage runs ScalPDF directly - no installer needed!")
                print("=" * 60)
                
                return appimage_path
            else:
                print("❌ AppImage build failed")
                return None
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ScalPDF AppImage Builder (Direct Application)

Usage:
    python build_scalpdf_appimage.py

This script creates a single AppImage that runs ScalPDF directly.
No installer GUI - just the actual PDF application.

The resulting AppImage can be double-clicked to launch ScalPDF
immediately with all features available.
""")
        return
    
    builder = ScalPDFAppImageBuilder()
    appimage_path = builder.build()
    
    if appimage_path:
        print(f"\n🎊 SUCCESS! ScalPDF AppImage ready at: {appimage_path}")
        sys.exit(0)
    else:
        print("\n💥 FAILED! AppImage build unsuccessful")
        sys.exit(1)

if __name__ == "__main__":
    main()
