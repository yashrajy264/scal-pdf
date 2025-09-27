#!/usr/bin/env python3
"""
ScalPDF .deb Package Builder
Creates a native Ubuntu/Debian package for easy installation via apt.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
import stat
import json
import hashlib

class DebPackageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build" / "deb"
        self.package_name = "scalpdf"
        self.version = "1.0.0"
        self.architecture = "amd64"
        
        # Package metadata
        self.metadata = {
            "Package": self.package_name,
            "Version": self.version,
            "Architecture": self.architecture,
            "Maintainer": "ScalPDF Team <support@scalpdf.com>",
            "Depends": "python3 (>= 3.11), python3-pip, python3-venv, python3-tk, libgl1-mesa-dri, libxcb-xinerama0, libfontconfig1",
            "Section": "graphics",
            "Priority": "optional",
            "Homepage": "https://github.com/yashrajy264/scal-pdf",
            "Description": "Secure PDF Viewer and Editor",
            "Long-Description": """ScalPDF is a secure, offline PDF viewer and editor with advanced
 encryption capabilities. Features include PDF viewing, annotations,
 merging, splitting, compression, and AES-256-GCM encryption.
 .
 Key Features:
  - Secure PDF viewing and editing
  - Advanced encryption (AES-256-GCM)
  - PDF merging and splitting
  - Compression with quality presets
  - Annotation support
  - Command-line interface
  - Completely offline operation"""
        }
        
    def setup_build_environment(self):
        """Setup the build environment."""
        print("🔧 Setting up .deb build environment...")
        
        # Clean and create build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create package directory structure
        self.package_dir = self.build_dir / f"{self.package_name}_{self.version}_{self.architecture}"
        self.debian_dir = self.package_dir / "DEBIAN"
        
        # Create standard directories
        directories = [
            "DEBIAN",
            "usr/bin",
            "usr/share/applications",
            "usr/share/pixmaps",
            "usr/share/doc/scalpdf",
            "usr/share/scalpdf",
            "usr/lib/scalpdf",
            "etc/scalpdf"
        ]
        
        for directory in directories:
            (self.package_dir / directory).mkdir(parents=True, exist_ok=True)
        
        print("✅ Build environment ready")
        
    def copy_application_files(self):
        """Copy ScalPDF application files."""
        print("📋 Copying application files...")
        
        app_dir = self.package_dir / "usr" / "share" / "scalpdf"
        
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
        
    def create_launcher_script(self):
        """Create the main launcher script."""
        print("🚀 Creating launcher script...")
        
        launcher_script = self.package_dir / "usr" / "bin" / "scalpdf"
        launcher_content = '''#!/bin/bash
# ScalPDF Launcher Script

APP_DIR="/usr/share/scalpdf"
VENV_DIR="/usr/lib/scalpdf/venv"
CONFIG_DIR="$HOME/.config/scalpdf"

# Create user config directory
mkdir -p "$CONFIG_DIR"

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up ScalPDF environment..."
    sudo mkdir -p "$VENV_DIR"
    sudo python3 -m venv "$VENV_DIR"
    sudo "$VENV_DIR/bin/pip" install --upgrade pip
    sudo "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
    sudo chown -R root:root "$VENV_DIR"
    sudo chmod -R 755 "$VENV_DIR"
fi

# Set up environment
export PYTHONPATH="$APP_DIR:$PYTHONPATH"
export SCALPDF_CONFIG_DIR="$CONFIG_DIR"

# Launch the application
exec "$VENV_DIR/bin/python" "$APP_DIR/main.py" "$@"
'''
        
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)
        
        # Create CLI launcher
        cli_launcher = self.package_dir / "usr" / "bin" / "scalpdf-cli"
        cli_content = '''#!/bin/bash
# ScalPDF CLI Launcher

APP_DIR="/usr/share/scalpdf"
VENV_DIR="/usr/lib/scalpdf/venv"

# Set up environment
export PYTHONPATH="$APP_DIR:$PYTHONPATH"

# Launch CLI
exec "$VENV_DIR/bin/python" -m cli.cli "$@"
'''
        
        cli_launcher.write_text(cli_content)
        cli_launcher.chmod(0o755)
        
        print("✅ Launcher scripts created")
        
    def create_desktop_file(self):
        """Create .desktop file for the application."""
        print("🖥️ Creating desktop file...")
        
        desktop_file = self.package_dir / "usr" / "share" / "applications" / "scalpdf.desktop"
        desktop_content = '''[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Viewer and Editor
Exec=scalpdf %f
Icon=scalpdf
Categories=Office;Graphics;Viewer;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
Keywords=PDF;viewer;editor;security;encryption;
Terminal=false
'''
        
        desktop_file.write_text(desktop_content)
        
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
            icon_path = self.package_dir / "usr" / "share" / "pixmaps" / "scalpdf.png"
            icon.save(icon_path, "PNG")
            
            print("✅ Application icon created")
            
        except ImportError:
            print("⚠️ PIL not available, creating placeholder icon")
            icon_path = self.package_dir / "usr" / "share" / "pixmaps" / "scalpdf.png"
            # Create a minimal PNG placeholder
            with open(icon_path, 'wb') as f:
                f.write(bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a4944415478da6300010000050001'))
        
    def create_control_file(self):
        """Create DEBIAN/control file."""
        print("📋 Creating control file...")
        
        # Calculate installed size (approximate)
        total_size = 0
        for root, dirs, files in os.walk(self.package_dir):
            for file in files:
                if not root.endswith('DEBIAN'):
                    file_path = Path(root) / file
                    if file_path.exists():
                        total_size += file_path.stat().st_size
        
        installed_size = total_size // 1024  # Convert to KB
        
        control_content = f"""Package: {self.metadata['Package']}
Version: {self.metadata['Version']}
Architecture: {self.metadata['Architecture']}
Maintainer: {self.metadata['Maintainer']}
Installed-Size: {installed_size}
Depends: {self.metadata['Depends']}
Section: {self.metadata['Section']}
Priority: {self.metadata['Priority']}
Homepage: {self.metadata['Homepage']}
Description: {self.metadata['Description']}
{self.metadata['Long-Description']}
"""
        
        control_file = self.debian_dir / "control"
        control_file.write_text(control_content)
        
        print("✅ Control file created")
        
    def create_postinst_script(self):
        """Create post-installation script."""
        print("🔧 Creating post-installation script...")
        
        postinst_content = '''#!/bin/bash
# ScalPDF post-installation script

set -e

case "$1" in
    configure)
        # Create virtual environment
        VENV_DIR="/usr/lib/scalpdf/venv"
        APP_DIR="/usr/share/scalpdf"
        
        if [ ! -d "$VENV_DIR" ]; then
            echo "Setting up ScalPDF Python environment..."
            python3 -m venv "$VENV_DIR"
            "$VENV_DIR/bin/pip" install --upgrade pip
            "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
        fi
        
        # Set permissions
        chown -R root:root "$VENV_DIR"
        chmod -R 755 "$VENV_DIR"
        
        # Update desktop database
        if command -v update-desktop-database >/dev/null 2>&1; then
            update-desktop-database -q /usr/share/applications
        fi
        
        # Update MIME database
        if command -v update-mime-database >/dev/null 2>&1; then
            update-mime-database /usr/share/mime
        fi
        
        echo "ScalPDF installation completed successfully!"
        echo "You can now launch ScalPDF from the applications menu or run 'scalpdf' in terminal."
        ;;
esac

exit 0
'''
        
        postinst_file = self.debian_dir / "postinst"
        postinst_file.write_text(postinst_content)
        postinst_file.chmod(0o755)
        
        print("✅ Post-installation script created")
        
    def create_prerm_script(self):
        """Create pre-removal script."""
        print("🗑️ Creating pre-removal script...")
        
        prerm_content = '''#!/bin/bash
# ScalPDF pre-removal script

set -e

case "$1" in
    remove|deconfigure)
        # Remove virtual environment
        VENV_DIR="/usr/lib/scalpdf/venv"
        if [ -d "$VENV_DIR" ]; then
            rm -rf "$VENV_DIR"
        fi
        ;;
esac

exit 0
'''
        
        prerm_file = self.debian_dir / "prerm"
        prerm_file.write_text(prerm_content)
        prerm_file.chmod(0o755)
        
        print("✅ Pre-removal script created")
        
    def create_copyright_file(self):
        """Create copyright file."""
        print("📄 Creating copyright file...")
        
        copyright_content = '''Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: ScalPDF
Upstream-Contact: ScalPDF Team <support@scalpdf.com>
Source: https://github.com/yashrajy264/scal-pdf

Files: *
Copyright: 2024 ScalPDF Team
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
'''
        
        copyright_file = self.package_dir / "usr" / "share" / "doc" / "scalpdf" / "copyright"
        copyright_file.write_text(copyright_content)
        
        print("✅ Copyright file created")
        
    def create_changelog(self):
        """Create changelog file."""
        print("📝 Creating changelog...")
        
        changelog_content = '''scalpdf (1.0.0) stable; urgency=medium

  * Initial release of ScalPDF
  * Secure PDF viewer and editor
  * AES-256-GCM encryption support
  * PDF merging, splitting, and compression
  * Annotation support
  * Command-line interface
  * Offline-only operation

 -- ScalPDF Team <support@scalpdf.com>  Sat, 28 Sep 2024 00:00:00 +0000
'''
        
        changelog_file = self.package_dir / "usr" / "share" / "doc" / "scalpdf" / "changelog.Debian"
        changelog_file.write_text(changelog_content)
        
        # Compress changelog
        subprocess.run(['gzip', '-9', str(changelog_file)], check=True)
        
        print("✅ Changelog created")
        
    def build_package(self):
        """Build the .deb package."""
        print("🔨 Building .deb package...")
        
        # Set correct permissions
        for root, dirs, files in os.walk(self.package_dir):
            for directory in dirs:
                dir_path = Path(root) / directory
                dir_path.chmod(0o755)
            for file in files:
                file_path = Path(root) / file
                if file_path.name in ['postinst', 'prerm', 'postrm']:
                    file_path.chmod(0o755)
                else:
                    file_path.chmod(0o644)
        
        # Build package
        package_file = self.build_dir / f"{self.package_name}_{self.version}_{self.architecture}.deb"
        
        result = subprocess.run([
            'dpkg-deb', '--build', str(self.package_dir), str(package_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Package created: {package_file}")
            return package_file
        else:
            print(f"❌ Package build failed: {result.stderr}")
            return None
            
    def create_info_file(self, package_path):
        """Create info file for the package."""
        info_content = f'''# ScalPDF .deb Package

## 📦 Package Information
- **Name**: {self.package_name}
- **Version**: {self.version}
- **Architecture**: {self.architecture}
- **Target**: Ubuntu 24.04+ and Debian-based distributions

## 🚀 Installation
```bash
# Install the package
sudo dpkg -i {package_path.name}

# Install dependencies (if needed)
sudo apt-get install -f

# Verify installation
scalpdf --version
```

## 🗑️ Removal
```bash
# Remove the package
sudo apt-get remove scalpdf

# Remove with configuration files
sudo apt-get purge scalpdf
```

## ✨ Features
- ✅ Native Ubuntu/Debian integration
- ✅ Automatic dependency management
- ✅ Desktop menu integration
- ✅ File association support
- ✅ System-wide installation
- ✅ Clean uninstallation

## 🔧 System Requirements
- Ubuntu 24.04+ or Debian-based distribution
- Python 3.11+
- X11 or Wayland display server

## 📋 Commands
- `scalpdf` - Launch GUI application
- `scalpdf-cli` - Command-line interface

## 🛡️ Security
- Offline-only operation
- AES-256-GCM encryption
- No telemetry or data collection

## 📁 Installation Locations
- Application: `/usr/share/scalpdf/`
- Executables: `/usr/bin/scalpdf`, `/usr/bin/scalpdf-cli`
- Desktop file: `/usr/share/applications/scalpdf.desktop`
- Icon: `/usr/share/pixmaps/scalpdf.png`
- Documentation: `/usr/share/doc/scalpdf/`
'''
        
        info_file = package_path.parent / f"{package_path.stem}.md"
        info_file.write_text(info_content)
        
        return info_file
        
    def build(self):
        """Main build process."""
        print("🏗️ Starting ScalPDF .deb package build...")
        
        try:
            # Check if dpkg-deb is available
            result = subprocess.run(['which', 'dpkg-deb'], capture_output=True)
            if result.returncode != 0:
                print("❌ dpkg-deb not found. Please install dpkg-dev package.")
                return None
            
            # Setup environment
            self.setup_build_environment()
            
            # Copy application files
            self.copy_application_files()
            
            # Create package files
            self.create_launcher_script()
            self.create_desktop_file()
            self.create_application_icon()
            self.create_control_file()
            self.create_postinst_script()
            self.create_prerm_script()
            self.create_copyright_file()
            self.create_changelog()
            
            # Build package
            package_path = self.build_package()
            
            if package_path and package_path.exists():
                # Create info file
                info_file = self.create_info_file(package_path)
                
                print(f"""
🎉 .deb package build completed successfully!

📦 Output files:
   • Package: {package_path}
   • Info: {info_file}

🚀 To install:
   sudo dpkg -i {package_path}
   sudo apt-get install -f

📋 Size: {package_path.stat().st_size / (1024*1024):.1f} MB
""")
                return package_path
            else:
                print("❌ Package build failed")
                return None
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return None

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ScalPDF .deb Package Builder

Usage:
    python build_deb.py [options]

Options:
    --help    Show this help message

This script creates a native .deb package for ScalPDF that can be
installed on Ubuntu 24.04+ and other Debian-based distributions.
""")
        return
    
    builder = DebPackageBuilder()
    package_path = builder.build()
    
    if package_path:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
