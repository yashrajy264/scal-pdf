#!/usr/bin/env python3
"""
ScalPDF Cross-Platform Installer Launcher
Detects platform and runs appropriate installer
"""

import sys
import os
import platform
import subprocess
from pathlib import Path


def detect_platform():
    """Detect the current platform."""
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"


def print_banner():
    """Print installation banner."""
    print("🚀 ScalPDF Cross-Platform Installer")
    print("=" * 40)
    print("Secure, Offline PDF Management Tool")
    print()


def install_linux():
    """Run Linux installer."""
    installer_path = Path(__file__).parent / "install_linux.sh"
    
    if not installer_path.exists():
        print("❌ Linux installer not found!")
        return False
    
    print("🐧 Detected Linux - Running Linux installer...")
    print()
    
    # Make executable
    os.chmod(installer_path, 0o755)
    
    # Run installer
    try:
        result = subprocess.run([str(installer_path)], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False


def install_windows():
    """Run Windows installer."""
    # Try PowerShell installer first
    ps_installer = Path(__file__).parent / "install_windows.ps1"
    bat_installer = Path(__file__).parent / "install_windows.bat"
    
    print("🪟 Detected Windows - Running Windows installer...")
    print()
    
    # Try PowerShell first
    if ps_installer.exists():
        print("Using PowerShell installer (recommended)...")
        try:
            result = subprocess.run([
                "powershell.exe", 
                "-ExecutionPolicy", "Bypass",
                "-File", str(ps_installer)
            ], check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            print("PowerShell installer failed, trying batch installer...")
        except FileNotFoundError:
            print("PowerShell not found, trying batch installer...")
    
    # Fallback to batch installer
    if bat_installer.exists():
        print("Using batch installer...")
        try:
            result = subprocess.run([str(bat_installer)], check=True, shell=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed with exit code {e.returncode}")
            return False
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    print("❌ No Windows installer found!")
    return False


def install_macos():
    """Handle macOS installation."""
    print("🍎 Detected macOS")
    print()
    print("ScalPDF can run on macOS, but automatic installation is not yet supported.")
    print("Please use manual installation:")
    print()
    print("1. Install dependencies:")
    print("   pip3 install -r requirements.txt")
    print()
    print("2. Run the application:")
    print("   python3 main.py")
    print()
    print("For CLI usage:")
    print("   python3 -m cli.cli --help")
    print()
    return False


def main():
    """Main installer function."""
    print_banner()
    
    # Detect platform
    current_platform = detect_platform()
    
    if current_platform == "linux":
        success = install_linux()
    elif current_platform == "windows":
        success = install_windows()
    elif current_platform == "macos":
        success = install_macos()
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        print("Supported platforms: Linux, Windows")
        success = False
    
    if success:
        print()
        print("🎉 Installation completed successfully!")
        print("ScalPDF is now ready to use.")
    else:
        print()
        print("❌ Installation failed or not completed.")
        print("Please check the error messages above.")
        print()
        print("For manual installation, see:")
        print("- README.md")
        print("- installers/README.md")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
