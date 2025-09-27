#!/usr/bin/env python3
"""
ScalPDF Smart Launcher
Automatically detects the best installation method and launches ScalPDF.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json
import time

class SmartLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system_info = self.detect_system()
        self.installation_methods = []
        
    def detect_system(self):
        """Detect system information."""
        info = {
            'os': platform.system().lower(),
            'dist': 'unknown',
            'arch': platform.machine(),
            'package_managers': []
        }
        
        if info['os'] == 'linux':
            # Detect Linux distribution
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('ID='):
                            info['dist'] = line.split('=')[1].strip().strip('"')
                            break
            except:
                pass
            
            # Check available package managers
            if shutil.which('apt'):
                info['package_managers'].append('apt')
            if shutil.which('snap'):
                info['package_managers'].append('snap')
            if shutil.which('dpkg'):
                info['package_managers'].append('dpkg')
                
        return info
        
    def scan_available_packages(self):
        """Scan for available ScalPDF packages."""
        packages = {
            'appimage': [],
            'deb': [],
            'snap': [],
            'installed': []
        }
        
        # Check build directory
        build_dir = self.project_root / "build"
        if build_dir.exists():
            # AppImages
            for appimage in build_dir.glob("**/*.AppImage"):
                if appimage.is_file():
                    packages['appimage'].append({
                        'path': appimage,
                        'size': appimage.stat().st_size,
                        'executable': os.access(appimage, os.X_OK)
                    })
            
            # .deb packages
            for deb in build_dir.glob("**/*.deb"):
                if deb.is_file():
                    packages['deb'].append({
                        'path': deb,
                        'size': deb.stat().st_size
                    })
            
            # Snap packages
            for snap in build_dir.glob("**/*.snap"):
                if snap.is_file():
                    packages['snap'].append({
                        'path': snap,
                        'size': snap.stat().st_size
                    })
        
        # Check for installed versions
        installed_locations = [
            '/usr/bin/scalpdf',
            '/usr/local/bin/scalpdf',
            str(Path.home() / 'Applications' / 'scalpdf'),
            str(Path.home() / '.local' / 'bin' / 'scalpdf')
        ]
        
        for location in installed_locations:
            if Path(location).exists():
                packages['installed'].append({
                    'path': Path(location),
                    'type': 'system'
                })
        
        # Check snap installation
        try:
            result = subprocess.run(['snap', 'list', 'scalpdf'], capture_output=True, text=True)
            if result.returncode == 0:
                packages['installed'].append({
                    'path': 'snap',
                    'type': 'snap'
                })
        except:
            pass
            
        return packages
        
    def determine_best_method(self, packages):
        """Determine the best installation/launch method."""
        methods = []
        
        # Priority 1: Already installed versions
        for installed in packages['installed']:
            if installed['type'] == 'snap':
                methods.append({
                    'type': 'launch_snap',
                    'priority': 10,
                    'description': 'Launch installed Snap package',
                    'command': ['scalpdf']
                })
            else:
                methods.append({
                    'type': 'launch_installed',
                    'priority': 9,
                    'description': f'Launch installed version: {installed["path"]}',
                    'command': [str(installed['path'])]
                })
        
        # Priority 2: Ready-to-use AppImages
        for appimage in packages['appimage']:
            if appimage['executable']:
                methods.append({
                    'type': 'launch_appimage',
                    'priority': 8,
                    'description': f'Launch AppImage: {appimage["path"].name}',
                    'command': [str(appimage['path'])],
                    'path': appimage['path']
                })
        
        # Priority 3: Install and launch .deb (if apt available)
        if 'apt' in self.system_info['package_managers'] and packages['deb']:
            deb = packages['deb'][0]  # Use first available
            methods.append({
                'type': 'install_deb',
                'priority': 7,
                'description': f'Install .deb package: {deb["path"].name}',
                'command': ['sudo', 'dpkg', '-i', str(deb['path'])],
                'path': deb['path'],
                'post_install': ['sudo', 'apt-get', 'install', '-f', '-y']
            })
        
        # Priority 4: Install and launch Snap (if snap available)
        if 'snap' in self.system_info['package_managers'] and packages['snap']:
            snap = packages['snap'][0]  # Use first available
            methods.append({
                'type': 'install_snap',
                'priority': 6,
                'description': f'Install Snap package: {snap["path"].name}',
                'command': ['sudo', 'snap', 'install', str(snap['path']), '--dangerous'],
                'path': snap['path']
            })
        
        # Priority 5: Make AppImage executable and launch
        for appimage in packages['appimage']:
            if not appimage['executable']:
                methods.append({
                    'type': 'setup_appimage',
                    'priority': 5,
                    'description': f'Setup and launch AppImage: {appimage["path"].name}',
                    'command': ['chmod', '+x', str(appimage['path'])],
                    'path': appimage['path'],
                    'launch_command': [str(appimage['path'])]
                })
        
        # Priority 6: Build packages
        methods.append({
            'type': 'build_packages',
            'priority': 1,
            'description': 'Build ScalPDF packages',
            'command': [sys.executable, str(self.project_root / "Installers GUI" / "package_installer.py")]
        })
        
        # Sort by priority (higher first)
        methods.sort(key=lambda x: x['priority'], reverse=True)
        return methods
        
    def execute_method(self, method):
        """Execute the selected method."""
        print(f"🚀 {method['description']}")
        
        try:
            if method['type'] == 'launch_snap':
                return self.launch_snap()
            elif method['type'] == 'launch_installed':
                return self.launch_installed(method['command'])
            elif method['type'] == 'launch_appimage':
                return self.launch_appimage(method['path'])
            elif method['type'] == 'install_deb':
                return self.install_and_launch_deb(method)
            elif method['type'] == 'install_snap':
                return self.install_and_launch_snap(method)
            elif method['type'] == 'setup_appimage':
                return self.setup_and_launch_appimage(method)
            elif method['type'] == 'build_packages':
                return self.launch_package_installer(method['command'])
            else:
                print(f"❌ Unknown method type: {method['type']}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to execute {method['type']}: {e}")
            return False
            
    def launch_snap(self):
        """Launch Snap version."""
        print("📦 Launching ScalPDF Snap...")
        try:
            subprocess.Popen(['scalpdf'], start_new_session=True)
            print("✅ ScalPDF Snap launched successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to launch Snap: {e}")
            return False
            
    def launch_installed(self, command):
        """Launch installed version."""
        print(f"🔧 Launching installed ScalPDF: {command[0]}")
        try:
            subprocess.Popen(command, start_new_session=True)
            print("✅ ScalPDF launched successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to launch installed version: {e}")
            return False
            
    def launch_appimage(self, appimage_path):
        """Launch AppImage."""
        print(f"📦 Launching AppImage: {appimage_path.name}")
        try:
            subprocess.Popen([str(appimage_path)], start_new_session=True)
            print("✅ AppImage launched successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to launch AppImage: {e}")
            return False
            
    def install_and_launch_deb(self, method):
        """Install .deb package and launch."""
        print(f"📦 Installing .deb package: {method['path'].name}")
        
        # Install package
        result = subprocess.run(method['command'], capture_output=True, text=True)
        if result.returncode != 0:
            print("🔧 Fixing dependencies...")
            subprocess.run(method['post_install'], check=True)
        
        print("✅ .deb package installed")
        
        # Launch
        return self.launch_installed(['scalpdf'])
        
    def install_and_launch_snap(self, method):
        """Install Snap package and launch."""
        print(f"📦 Installing Snap package: {method['path'].name}")
        
        # Install package
        result = subprocess.run(method['command'], check=True)
        print("✅ Snap package installed")
        
        # Launch
        return self.launch_snap()
        
    def setup_and_launch_appimage(self, method):
        """Setup AppImage and launch."""
        print(f"🔧 Setting up AppImage: {method['path'].name}")
        
        # Make executable
        subprocess.run(method['command'], check=True)
        print("✅ AppImage made executable")
        
        # Launch
        return self.launch_appimage(method['path'])
        
    def launch_package_installer(self, command):
        """Launch the package installer GUI."""
        print("🎨 Launching ScalPDF Package Installer...")
        try:
            subprocess.Popen(command, start_new_session=True)
            print("✅ Package installer launched")
            print("   Use the GUI to build and install ScalPDF packages")
            return True
        except Exception as e:
            print(f"❌ Failed to launch package installer: {e}")
            return False
            
    def show_system_info(self):
        """Show system information."""
        print("🖥️  System Information:")
        print(f"   OS: {self.system_info['os'].title()} ({self.system_info['dist']})")
        print(f"   Architecture: {self.system_info['arch']}")
        print(f"   Package Managers: {', '.join(self.system_info['package_managers']) if self.system_info['package_managers'] else 'None detected'}")
        print()
        
    def show_available_packages(self, packages):
        """Show available packages."""
        print("📦 Available Packages:")
        
        if packages['installed']:
            print("   Installed:")
            for pkg in packages['installed']:
                if pkg['type'] == 'snap':
                    print("     • ScalPDF (Snap)")
                else:
                    print(f"     • {pkg['path']}")
        
        if packages['appimage']:
            print("   AppImages:")
            for pkg in packages['appimage']:
                status = "✅ Ready" if pkg['executable'] else "🔧 Needs setup"
                size_mb = pkg['size'] / (1024 * 1024)
                print(f"     • {pkg['path'].name} ({size_mb:.1f} MB) - {status}")
        
        if packages['deb']:
            print("   .deb Packages:")
            for pkg in packages['deb']:
                size_mb = pkg['size'] / (1024 * 1024)
                print(f"     • {pkg['path'].name} ({size_mb:.1f} MB)")
        
        if packages['snap']:
            print("   Snap Packages:")
            for pkg in packages['snap']:
                size_mb = pkg['size'] / (1024 * 1024)
                print(f"     • {pkg['path'].name} ({size_mb:.1f} MB)")
        
        if not any([packages['installed'], packages['appimage'], packages['deb'], packages['snap']]):
            print("   No packages found. Use --build to create them.")
        
        print()
        
    def run(self, args=None):
        """Main run method."""
        if args is None:
            args = sys.argv[1:]
            
        # Handle command line arguments
        if '--help' in args or '-h' in args:
            self.show_help()
            return
        elif '--build' in args:
            self.launch_package_installer([sys.executable, str(self.project_root / "Installers GUI" / "package_installer.py")])
            return
        elif '--info' in args:
            self.show_system_info()
            packages = self.scan_available_packages()
            self.show_available_packages(packages)
            return
        elif '--list' in args:
            packages = self.scan_available_packages()
            methods = self.determine_best_method(packages)
            print("🎯 Available Launch Methods (in priority order):")
            for i, method in enumerate(methods, 1):
                print(f"   {i}. {method['description']}")
            return
            
        # Normal launch process
        print("🚀 ScalPDF Smart Launcher")
        print("=" * 40)
        
        # Show system info
        self.show_system_info()
        
        # Scan packages
        print("🔍 Scanning for ScalPDF packages...")
        packages = self.scan_available_packages()
        self.show_available_packages(packages)
        
        # Determine best method
        methods = self.determine_best_method(packages)
        
        if not methods:
            print("❌ No launch methods available")
            print("   Run with --build to create packages")
            return
            
        # Try methods in order
        print("🎯 Attempting to launch ScalPDF...")
        for method in methods:
            print(f"\n📋 Trying: {method['description']}")
            
            if self.execute_method(method):
                print("🎉 ScalPDF launched successfully!")
                return
            else:
                print("⚠️  Method failed, trying next option...")
                
        print("\n❌ All launch methods failed")
        print("   Try running with --build to create fresh packages")
        
    def show_help(self):
        """Show help information."""
        print("""
🚀 ScalPDF Smart Launcher

Usage:
    python smart_launcher.py [options]

Options:
    --help, -h     Show this help message
    --build        Launch package builder GUI
    --info         Show system and package information
    --list         List available launch methods

Description:
    The Smart Launcher automatically detects the best way to run ScalPDF
    on your system. It will try the following methods in order:
    
    1. Launch already installed version (Snap or system)
    2. Launch ready-to-use AppImage
    3. Install and launch .deb package (Ubuntu/Debian)
    4. Install and launch Snap package
    5. Setup and launch AppImage
    6. Launch package builder GUI
    
Examples:
    python smart_launcher.py          # Auto-launch ScalPDF
    python smart_launcher.py --build  # Build packages
    python smart_launcher.py --info   # Show system info
    python smart_launcher.py --list   # List launch methods

🛡️  Security Note:
    ScalPDF operates completely offline and never connects to the internet.
    Your documents remain secure and private on your local system.
""")

def main():
    """Main entry point."""
    launcher = SmartLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
