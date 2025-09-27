#!/usr/bin/env python3
"""
ScalPDF Installation Script
Simple installer for development and testing
"""

import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Install requirements
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True)
            print("✅ Dependencies installed successfully")
        else:
            print("❌ requirements.txt not found")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_shortcuts():
    """Create desktop shortcuts and start menu entries."""
    system = platform.system().lower()
    
    if system == "windows":
        create_windows_shortcuts()
    elif system == "linux":
        create_linux_shortcuts()
    else:
        print(f"⚠️  Shortcuts not supported on {system}")


def create_windows_shortcuts():
    """Create Windows shortcuts."""
    print("🔗 Creating Windows shortcuts...")
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        # Get paths
        desktop = winshell.desktop()
        start_menu = winshell.start_menu()
        
        # Create desktop shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(Path(desktop) / "ScalPDF.lnk"))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = str(Path.cwd() / "main.py")
        shortcut.WorkingDirectory = str(Path.cwd())
        shortcut.IconLocation = str(Path.cwd() / "assets" / "icon.ico")
        shortcut.save()
        
        print("✅ Windows shortcuts created")
        
    except ImportError:
        print("⚠️  Windows shortcut creation requires pywin32 and winshell")
        print("   Install with: pip install pywin32 winshell")
    except Exception as e:
        print(f"⚠️  Failed to create shortcuts: {e}")


def create_linux_shortcuts():
    """Create Linux desktop entries."""
    print("🔗 Creating Linux desktop entries...")
    
    try:
        # Desktop file content
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Management Tool
Exec={sys.executable} {Path.cwd() / "main.py"}
Icon={Path.cwd() / "assets" / "icon.png"}
Categories=Office;Graphics;
StartupNotify=true
StartupWMClass=ScalPDF
"""
        
        # Create desktop file in user applications
        apps_dir = Path.home() / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = apps_dir / "scalpdf.desktop"
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)
        
        # Also create on desktop if Desktop directory exists
        desktop_dir = Path.home() / "Desktop"
        if desktop_dir.exists():
            desktop_shortcut = desktop_dir / "ScalPDF.desktop"
            desktop_shortcut.write_text(desktop_content)
            desktop_shortcut.chmod(0o755)
        
        print("✅ Linux desktop entries created")
        
    except Exception as e:
        print(f"⚠️  Failed to create desktop entries: {e}")


def run_tests():
    """Run basic tests to verify installation."""
    print("🧪 Running basic tests...")
    
    try:
        # Test core imports
        import core.crypto
        import core.viewer
        import core.compress
        import core.editor
        import core.annotations
        
        print("✅ Core modules imported successfully")
        
        # Test CLI
        from cli.cli import cli
        print("✅ CLI module imported successfully")
        
        # Test GUI imports (may fail in headless environments)
        try:
            import ui.main_window
            print("✅ GUI modules imported successfully")
        except ImportError as e:
            print(f"⚠️  GUI import failed (may be normal in headless environment): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main installation function."""
    print("🚀 ScalPDF Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but installation may still work")
    
    # Create shortcuts
    create_shortcuts()
    
    print("\n🎉 Installation completed!")
    print("\n📖 Usage:")
    print(f"  GUI: python {Path.cwd() / 'main.py'}")
    print(f"  CLI: python -m cli.cli --help")
    
    print("\n🔧 Development:")
    print("  Run tests: pytest")
    print("  Build app: python build.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
