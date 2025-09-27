#!/usr/bin/env python3
"""
ScalPDF AppImage Builder
Creates a portable AppImage for Ubuntu 24.04+ and other Linux distributions.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path
import stat
import json

class AppImageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build" / "appimage"
        self.appdir = self.build_dir / "ScalPDF.AppDir"
        
        # AppImage tools URLs
        self.appimagetool_url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        self.linuxdeploy_url = "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
        
    def setup_build_environment(self):
        """Setup the build environment."""
        print("🔧 Setting up AppImage build environment...")
        
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
        
    def download_tools(self):
        """Download AppImage build tools."""
        print("📥 Downloading AppImage tools...")
        
        tools_dir = self.build_dir / "tools"
        tools_dir.mkdir(exist_ok=True)
        
        # Download appimagetool
        appimagetool_path = tools_dir / "appimagetool"
        if not appimagetool_path.exists():
            print("  📦 Downloading appimagetool...")
            urllib.request.urlretrieve(self.appimagetool_url, appimagetool_path)
            appimagetool_path.chmod(0o755)
        
        # Download linuxdeploy
        linuxdeploy_path = tools_dir / "linuxdeploy"
        if not linuxdeploy_path.exists():
            print("  📦 Downloading linuxdeploy...")
            urllib.request.urlretrieve(self.linuxdeploy_url, linuxdeploy_path)
            linuxdeploy_path.chmod(0o755)
        
        print("✅ Tools downloaded")
        return appimagetool_path, linuxdeploy_path
        
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
        print("📋 Copying application files...")
        
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
        """Create the main launcher script."""
        print("🚀 Creating launcher script...")
        
        launcher_script = self.appdir / "usr" / "bin" / "scalpdf"
        launcher_content = f'''#!/bin/bash
# ScalPDF AppImage Launcher

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
APP_DIR="$SCRIPT_DIR/../share/scalpdf"
PYTHON_DIR="$SCRIPT_DIR/../python"

# Set up environment
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="$PYTHON_DIR/lib/python*/site-packages/PySide6/Qt/plugins"

# Launch the application
exec "$PYTHON_DIR/bin/python" "$APP_DIR/main.py" "$@"
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
            
            # Background circle
            margin = 20
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill=(220, 53, 69), outline=(176, 42, 55), width=4)
            
            # PDF text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            text = "PDF"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2 - 10
            
            draw.text((text_x, text_y), text, fill='white', font=font)
            
            # Security shield
            shield_points = [
                (size//2, margin + 30),
                (size//2 + 25, margin + 45),
                (size//2 + 25, margin + 70),
                (size//2, margin + 85),
                (size//2 - 25, margin + 70),
                (size//2 - 25, margin + 45)
            ]
            draw.polygon(shield_points, fill=(255, 193, 7), outline=(255, 152, 0), width=2)
            
            # Save icon
            icon_path = self.appdir / "scalpdf.png"
            icon.save(icon_path, "PNG")
            
            # Copy to icons directory
            hicolor_icon = self.appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / "scalpdf.png"
            shutil.copy2(icon_path, hicolor_icon)
            
            print("✅ Application icon created")
            
        except ImportError:
            print("⚠️ PIL not available, using text-based icon")
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
# ScalPDF AppRun Script

# Get the directory where this AppImage is mounted
HERE="$(dirname "$(readlink -f "${0}")")"

# Set up environment
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONPATH="${HERE}/usr/share/scalpdf:${PYTHONPATH}"

# Qt environment
export QT_QPA_PLATFORM_PLUGIN_PATH="${HERE}/usr/python/lib/python*/site-packages/PySide6/Qt/plugins"
export QT_PLUGIN_PATH="${HERE}/usr/python/lib/python*/site-packages/PySide6/Qt/plugins"

# Launch the application
exec "${HERE}/usr/bin/scalpdf" "$@"
'''
        
        apprun_script.write_text(apprun_content)
        apprun_script.chmod(0o755)
        
        print("✅ AppRun script created")
        
    def build_appimage(self, appimagetool_path):
        """Build the final AppImage."""
        print("🔨 Building AppImage...")
        
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
            print(f"✅ AppImage created: {output_path}")
            return output_path
        else:
            print(f"❌ AppImage build failed: {result.stderr}")
            return None
            
    def create_info_file(self, appimage_path):
        """Create info file for the AppImage."""
        info_content = f'''# ScalPDF AppImage

## 📦 Package Information
- **Name**: ScalPDF
- **Version**: 1.0.0
- **Architecture**: x86_64
- **Target**: Ubuntu 24.04+ and compatible Linux distributions

## 🚀 Usage
```bash
# Make executable
chmod +x {appimage_path.name}

# Run directly
./{appimage_path.name}

# Or install system-wide
sudo mv {appimage_path.name} /usr/local/bin/scalpdf
scalpdf
```

## ✨ Features
- ✅ Portable - runs on any Linux distribution
- ✅ No installation required
- ✅ Includes all dependencies
- ✅ Desktop integration support
- ✅ File association support

## 🔧 System Requirements
- Ubuntu 24.04+ or compatible Linux distribution
- X11 or Wayland display server
- 64-bit architecture

## 🛡️ Security
- Offline-only operation
- AES-256-GCM encryption
- No telemetry or data collection

## 📋 File Associations
The AppImage supports automatic file associations for PDF files.
To enable, run: `{appimage_path.name} --install-desktop`
'''
        
        info_file = appimage_path.parent / f"{appimage_path.stem}.md"
        info_file.write_text(info_content)
        
        return info_file
        
    def build(self):
        """Main build process."""
        print("🏗️ Starting ScalPDF AppImage build...")
        
        try:
            # Setup environment
            self.setup_build_environment()
            
            # Download tools
            appimagetool_path, linuxdeploy_path = self.download_tools()
            
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
                # Create info file
                info_file = self.create_info_file(appimage_path)
                
                print(f"""
🎉 AppImage build completed successfully!

📦 Output files:
   • AppImage: {appimage_path}
   • Info: {info_file}

🚀 To test:
   chmod +x {appimage_path}
   ./{appimage_path}

📋 Size: {appimage_path.stat().st_size / (1024*1024):.1f} MB
""")
                return appimage_path
            else:
                print("❌ AppImage build failed")
                return None
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return None

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ScalPDF AppImage Builder

Usage:
    python build_appimage.py [options]

Options:
    --help    Show this help message

This script creates a portable AppImage for ScalPDF that can run
on Ubuntu 24.04+ and other compatible Linux distributions.
""")
        return
    
    builder = AppImageBuilder()
    appimage_path = builder.build()
    
    if appimage_path:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
