#!/usr/bin/env python3
"""
ScalPDF Snap Package Builder
Creates a Snap package for universal Linux distribution.
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
import yaml
import json

class SnapPackageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build" / "snap"
        self.snap_dir = self.build_dir / "snap"
        
        # Snap metadata
        self.snap_metadata = {
            "name": "scalpdf",
            "version": "1.0.0",
            "summary": "Secure PDF Viewer and Editor",
            "description": """
ScalPDF is a secure, offline PDF viewer and editor with advanced encryption capabilities.

Key Features:
• Secure PDF viewing and editing
• Advanced encryption (AES-256-GCM)
• PDF merging and splitting
• Compression with quality presets
• Annotation support
• Command-line interface
• Completely offline operation

ScalPDF prioritizes security and privacy, operating entirely offline with no telemetry or data collection.
            """.strip(),
            "grade": "stable",
            "confinement": "strict",
            "base": "core22",
            "architectures": ["amd64"],
            "license": "MIT",
            "contact": "https://github.com/yashrajy264/scal-pdf/issues",
            "website": "https://github.com/yashrajy264/scal-pdf"
        }
        
    def setup_build_environment(self):
        """Setup the build environment."""
        print("🔧 Setting up Snap build environment...")
        
        # Clean and create build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create snap directory
        self.snap_dir.mkdir(exist_ok=True)
        
        print("✅ Build environment ready")
        
    def create_snapcraft_yaml(self):
        """Create snapcraft.yaml file."""
        print("📋 Creating snapcraft.yaml...")
        
        snapcraft_config = {
            "name": self.snap_metadata["name"],
            "version": self.snap_metadata["version"],
            "summary": self.snap_metadata["summary"],
            "description": self.snap_metadata["description"],
            "grade": self.snap_metadata["grade"],
            "confinement": self.snap_metadata["confinement"],
            "base": self.snap_metadata["base"],
            "architectures": [{"build-on": arch, "build-for": arch} for arch in self.snap_metadata["architectures"]],
            "license": self.snap_metadata["license"],
            "contact": self.snap_metadata["contact"],
            "website": self.snap_metadata["website"],
            
            "apps": {
                "scalpdf": {
                    "command": "bin/scalpdf-wrapper",
                    "desktop": "usr/share/applications/scalpdf.desktop",
                    "plugs": [
                        "home",
                        "desktop",
                        "desktop-legacy",
                        "wayland",
                        "x11",
                        "opengl",
                        "audio-playback",
                        "removable-media"
                    ],
                    "environment": {
                        "PYTHONPATH": "$SNAP/usr/share/scalpdf:$PYTHONPATH",
                        "QT_QPA_PLATFORM_PLUGIN_PATH": "$SNAP/usr/lib/python3/dist-packages/PySide6/Qt/plugins"
                    }
                },
                "cli": {
                    "command": "bin/scalpdf-cli-wrapper",
                    "plugs": [
                        "home",
                        "removable-media"
                    ]
                }
            },
            
            "parts": {
                "scalpdf": {
                    "plugin": "python",
                    "source": ".",
                    "source-type": "local",
                    "python-requirements": ["requirements.txt"],
                    "stage-packages": [
                        "python3-tk",
                        "libgl1-mesa-dri",
                        "libxcb-xinerama0",
                        "libxcb-cursor0",
                        "libxkbcommon-x11-0",
                        "libglib2.0-0",
                        "libfontconfig1",
                        "libx11-xcb1",
                        "libxcb-glx0",
                        "libxcb-shape0",
                        "libxcb-util1",
                        "libxrender1",
                        "libxi6",
                        "libegl1-mesa",
                        "libgl1-mesa-dev"
                    ],
                    "build-packages": [
                        "python3-dev",
                        "python3-pip",
                        "python3-setuptools",
                        "build-essential",
                        "libffi-dev"
                    ],
                    "override-build": """
                        craftctl default
                        
                        # Copy application files
                        mkdir -p $CRAFTCTL_PART_INSTALL/usr/share/scalpdf
                        cp -r main.py requirements.txt setup.py LICENSE README.md $CRAFTCTL_PART_INSTALL/usr/share/scalpdf/
                        cp -r core ui cli tests $CRAFTCTL_PART_INSTALL/usr/share/scalpdf/
                        
                        # Create wrapper scripts
                        mkdir -p $CRAFTCTL_PART_INSTALL/bin
                        
                        # GUI wrapper
                        cat > $CRAFTCTL_PART_INSTALL/bin/scalpdf-wrapper << 'EOF'
#!/bin/bash
export PYTHONPATH="$SNAP/usr/share/scalpdf:$PYTHONPATH"
export QT_QPA_PLATFORM_PLUGIN_PATH="$SNAP/usr/lib/python3/dist-packages/PySide6/Qt/plugins"
export SCALPDF_CONFIG_DIR="$SNAP_USER_DATA"
cd "$SNAP/usr/share/scalpdf"
exec "$SNAP/usr/bin/python3" main.py "$@"
EOF
                        chmod +x $CRAFTCTL_PART_INSTALL/bin/scalpdf-wrapper
                        
                        # CLI wrapper
                        cat > $CRAFTCTL_PART_INSTALL/bin/scalpdf-cli-wrapper << 'EOF'
#!/bin/bash
export PYTHONPATH="$SNAP/usr/share/scalpdf:$PYTHONPATH"
cd "$SNAP/usr/share/scalpdf"
exec "$SNAP/usr/bin/python3" -m cli.cli "$@"
EOF
                        chmod +x $CRAFTCTL_PART_INSTALL/bin/scalpdf-cli-wrapper
                        
                        # Create desktop file
                        mkdir -p $CRAFTCTL_PART_INSTALL/usr/share/applications
                        cat > $CRAFTCTL_PART_INSTALL/usr/share/applications/scalpdf.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Viewer and Editor
Exec=scalpdf %f
Icon=${SNAP}/usr/share/pixmaps/scalpdf.png
Categories=Office;Graphics;Viewer;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
Keywords=PDF;viewer;editor;security;encryption;
Terminal=false
EOF
                        
                        # Create icon
                        mkdir -p $CRAFTCTL_PART_INSTALL/usr/share/pixmaps
                        python3 -c "
import sys
sys.path.insert(0, '$CRAFTCTL_PART_INSTALL/usr/share/scalpdf')
try:
    from PIL import Image, ImageDraw, ImageFont
    
    size = 256
    icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    
    # Background circle
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(220, 53, 69), outline=(176, 42, 55), width=4)
    
    # PDF text
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
    except:
        font = ImageFont.load_default()
    
    text = 'PDF'
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
    
    icon.save('$CRAFTCTL_PART_INSTALL/usr/share/pixmaps/scalpdf.png', 'PNG')
    print('Icon created successfully')
except ImportError:
    # Create placeholder
    with open('$CRAFTCTL_PART_INSTALL/usr/share/pixmaps/scalpdf.png', 'wb') as f:
        f.write(bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a4944415478da6300010000050001'))
    print('Placeholder icon created')
"
                    """
                }
            }
        }
        
        snapcraft_file = self.snap_dir / "snapcraft.yaml"
        with open(snapcraft_file, 'w') as f:
            yaml.dump(snapcraft_config, f, default_flow_style=False, sort_keys=False)
        
        print("✅ snapcraft.yaml created")
        return snapcraft_file
        
    def copy_source_files(self):
        """Copy source files to build directory."""
        print("📋 Copying source files...")
        
        # Files and directories to copy
        items_to_copy = [
            "main.py", "requirements.txt", "setup.py", "LICENSE", "README.md",
            "core", "ui", "cli", "tests"
        ]
        
        for item in items_to_copy:
            source_item = self.project_root / item
            if source_item.exists():
                dest_item = self.build_dir / item
                if source_item.is_file():
                    shutil.copy2(source_item, dest_item)
                else:
                    shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
        
        print("✅ Source files copied")
        
    def build_snap(self):
        """Build the Snap package."""
        print("🔨 Building Snap package...")
        
        # Check if snapcraft is available
        result = subprocess.run(['which', 'snapcraft'], capture_output=True)
        if result.returncode != 0:
            print("❌ snapcraft not found. Please install snapcraft.")
            print("   sudo snap install snapcraft --classic")
            return None
        
        # Build the snap
        result = subprocess.run([
            'snapcraft', 'pack'
        ], cwd=str(self.build_dir), capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find the generated snap file
            snap_files = list(self.build_dir.glob("*.snap"))
            if snap_files:
                snap_file = snap_files[0]
                print(f"✅ Snap package created: {snap_file}")
                return snap_file
            else:
                print("❌ Snap file not found after build")
                return None
        else:
            print(f"❌ Snap build failed: {result.stderr}")
            # Try alternative build method
            print("🔄 Trying alternative build method...")
            return self.build_snap_alternative()
            
    def build_snap_alternative(self):
        """Alternative snap build method using docker."""
        print("🐳 Building Snap with Docker...")
        
        # Check if docker is available
        result = subprocess.run(['which', 'docker'], capture_output=True)
        if result.returncode != 0:
            print("❌ Docker not available for alternative build")
            return None
        
        # Build with docker
        result = subprocess.run([
            'snapcraft', 'pack', '--use-lxd'
        ], cwd=str(self.build_dir), capture_output=True, text=True)
        
        if result.returncode == 0:
            snap_files = list(self.build_dir.glob("*.snap"))
            if snap_files:
                return snap_files[0]
        
        print("❌ Alternative build also failed")
        return None
        
    def create_info_file(self, snap_path):
        """Create info file for the Snap package."""
        info_content = f'''# ScalPDF Snap Package

## 📦 Package Information
- **Name**: {self.snap_metadata["name"]}
- **Version**: {self.snap_metadata["version"]}
- **Confinement**: {self.snap_metadata["confinement"]}
- **Base**: {self.snap_metadata["base"]}
- **Target**: Universal Linux distributions

## 🚀 Installation
```bash
# Install from local file
sudo snap install {snap_path.name} --dangerous

# Or install from Snap Store (when published)
sudo snap install scalpdf
```

## 🔧 Usage
```bash
# Launch GUI
scalpdf

# Use CLI
scalpdf.cli --help
```

## 🗑️ Removal
```bash
# Remove the snap
sudo snap remove scalpdf
```

## ✨ Features
- ✅ Universal Linux compatibility
- ✅ Automatic updates (when from store)
- ✅ Sandboxed security
- ✅ Desktop integration
- ✅ File association support
- ✅ Confined execution environment

## 🔧 System Requirements
- Any Linux distribution with Snap support
- X11 or Wayland display server
- 64-bit architecture

## 🛡️ Security
- Strict confinement for enhanced security
- Limited file system access
- Offline-only operation
- AES-256-GCM encryption
- No telemetry or data collection

## 📋 Permissions
The snap requires the following permissions:
- `home` - Access to user home directory
- `desktop` - Desktop integration
- `x11/wayland` - Display server access
- `opengl` - Hardware acceleration
- `removable-media` - Access to USB drives, etc.

## 🔍 Troubleshooting
If the application doesn't start:
```bash
# Check snap logs
sudo journalctl -u snapd

# Check app logs
snap logs scalpdf

# Verify permissions
snap connections scalpdf
```

## 📁 Data Location
User data is stored in: `~/snap/scalpdf/current/`
'''
        
        info_file = snap_path.parent / f"{snap_path.stem}.md"
        info_file.write_text(info_content)
        
        return info_file
        
    def build(self):
        """Main build process."""
        print("🏗️ Starting ScalPDF Snap package build...")
        
        try:
            # Setup environment
            self.setup_build_environment()
            
            # Copy source files
            self.copy_source_files()
            
            # Create snapcraft.yaml
            self.create_snapcraft_yaml()
            
            # Build snap
            snap_path = self.build_snap()
            
            if snap_path and snap_path.exists():
                # Create info file
                info_file = self.create_info_file(snap_path)
                
                print(f"""
🎉 Snap package build completed successfully!

📦 Output files:
   • Snap: {snap_path}
   • Info: {info_file}

🚀 To install:
   sudo snap install {snap_path} --dangerous

📋 Size: {snap_path.stat().st_size / (1024*1024):.1f} MB
""")
                return snap_path
            else:
                print("❌ Snap build failed")
                return None
                
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return None

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ScalPDF Snap Package Builder

Usage:
    python build_snap.py [options]

Options:
    --help    Show this help message

This script creates a Snap package for ScalPDF that can be
installed on any Linux distribution with Snap support.

Requirements:
    - snapcraft (sudo snap install snapcraft --classic)
    - Optional: docker or lxd for containerized builds
""")
        return
    
    builder = SnapPackageBuilder()
    snap_path = builder.build()
    
    if snap_path:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
