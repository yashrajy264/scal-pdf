#!/usr/bin/env python3
"""
Build script for ScalPDF
Handles cross-platform building with PyInstaller
"""

import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path
import argparse


def get_platform():
    """Get the current platform."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"


def check_dependencies():
    """Check if required build dependencies are installed."""
    print("🔍 Checking build dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    print(f"✅ Python {sys.version}")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install PyInstaller")
        return False
    
    # Check core dependencies
    required_modules = [
        ('PySide6', 'PySide6'),
        ('fitz', 'PyMuPDF'),
        ('pikepdf', 'pikepdf'),
        ('PIL', 'Pillow'),
        ('cryptography', 'cryptography'),
        ('argon2', 'argon2-cffi'),
        ('click', 'click')
    ]
    
    for module, package in required_modules:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not found. Install with: pip install {package}")
            return False
    
    return True


def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Clean .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
    
    print("✅ Build artifacts cleaned")


def build_application(platform_name, debug=False):
    """Build the application using PyInstaller."""
    print(f"🔨 Building ScalPDF for {platform_name}...")
    
    # Select appropriate spec file
    if platform_name == "windows":
        spec_file = "build_windows.spec"
    elif platform_name == "linux":
        spec_file = "build_linux.spec"
    else:
        print(f"❌ Unsupported platform: {platform_name}")
        return False
    
    if not Path(spec_file).exists():
        print(f"❌ Spec file not found: {spec_file}")
        return False
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        spec_file
    ]
    
    if debug:
        cmd.append("--debug=all")
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def create_cli_executable():
    """Create CLI executable."""
    print("🔧 Creating CLI executable...")
    
    platform_name = get_platform()
    
    # CLI spec content
    cli_spec = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cli/cli.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'core.crypto',
        'core.compress', 
        'core.editor',
        'core.annotations',
        'click',
        'cryptography',
        'argon2',
        'pikepdf',
        'fitz'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='scalpdf{"" if platform_name != "windows" else ".exe"}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Write CLI spec file
    cli_spec_file = "build_cli.spec"
    with open(cli_spec_file, 'w') as f:
        f.write(cli_spec)
    
    # Build CLI
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        cli_spec_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ CLI executable created")
        
        # Clean up spec file
        Path(cli_spec_file).unlink()
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI build failed: {e}")
        return False


def package_application(platform_name):
    """Package the built application."""
    print(f"📦 Packaging application for {platform_name}...")
    
    dist_dir = Path("dist/ScalPDF")
    if not dist_dir.exists():
        print("❌ Build directory not found")
        return False
    
    # Create package directory
    package_dir = Path("package")
    package_dir.mkdir(exist_ok=True)
    
    if platform_name == "windows":
        # Create ZIP package for Windows
        import zipfile
        
        zip_path = package_dir / "ScalPDF-Windows.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dist_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(dist_dir.parent)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Windows package created: {zip_path}")
        
    elif platform_name == "linux":
        # Create tar.gz package for Linux
        import tarfile
        
        tar_path = package_dir / "ScalPDF-Linux.tar.gz"
        with tarfile.open(tar_path, 'w:gz') as tar:
            tar.add(dist_dir, arcname="ScalPDF")
        
        print(f"✅ Linux package created: {tar_path}")
        
        # Also create AppImage if script exists
        appimage_script = Path("create_appimage.sh")
        if appimage_script.exists():
            print("📱 Creating AppImage...")
            try:
                subprocess.run(["./create_appimage.sh"], check=True)
                print("✅ AppImage created")
            except subprocess.CalledProcessError:
                print("⚠️  AppImage creation failed (appimagetool may not be available)")
    
    return True


def create_desktop_files():
    """Create desktop integration files."""
    print("🖥️  Creating desktop integration files...")
    
    # Linux desktop file
    desktop_content = """[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Management Tool
Exec=scalpdf
Icon=scalpdf
Categories=Office;Graphics;Photography;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
"""
    
    with open("scalpdf.desktop", 'w') as f:
        f.write(desktop_content)
    
    print("✅ Desktop files created")


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build ScalPDF application")
    parser.add_argument("--platform", choices=["windows", "linux", "auto"], 
                       default="auto", help="Target platform")
    parser.add_argument("--clean", action="store_true", 
                       help="Clean build artifacts before building")
    parser.add_argument("--debug", action="store_true", 
                       help="Build with debug information")
    parser.add_argument("--cli-only", action="store_true", 
                       help="Build only CLI executable")
    parser.add_argument("--no-package", action="store_true", 
                       help="Skip packaging step")
    
    args = parser.parse_args()
    
    # Determine platform
    if args.platform == "auto":
        platform_name = get_platform()
    else:
        platform_name = args.platform
    
    print(f"🚀 Building ScalPDF for {platform_name}")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return 1
    
    # Clean if requested
    if args.clean:
        clean_build()
    
    # Create desktop files
    create_desktop_files()
    
    # Build CLI only if requested
    if args.cli_only:
        if create_cli_executable():
            print("✅ CLI build completed successfully")
            return 0
        else:
            print("❌ CLI build failed")
            return 1
    
    # Build main application
    if not build_application(platform_name, args.debug):
        print("❌ Application build failed")
        return 1
    
    # Build CLI executable
    if not create_cli_executable():
        print("⚠️  CLI build failed, but continuing...")
    
    # Package application
    if not args.no_package:
        if not package_application(platform_name):
            print("❌ Packaging failed")
            return 1
    
    print("\n🎉 Build completed successfully!")
    print("\nBuild artifacts:")
    print(f"  - GUI Application: dist/ScalPDF/")
    print(f"  - CLI Executable: dist/scalpdf{'exe' if platform_name == 'windows' else ''}")
    if not args.no_package:
        print(f"  - Package: package/ScalPDF-{platform_name.title()}.*")
    
    print("\n📖 Usage:")
    print("  GUI: Run the ScalPDF executable in dist/ScalPDF/")
    print("  CLI: Use the scalpdf command for batch operations")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
