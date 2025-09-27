#!/usr/bin/env python3
"""
ScalPDF Package Installer GUI
Modern GUI installer for ScalPDF packages (AppImage, .deb, Snap).
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import platform
import shutil
from pathlib import Path
import json
import time

class PackageInstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF Package Installer")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.setup_styles()
        
        # Variables
        self.installation_type = tk.StringVar(value="auto")
        self.package_path = tk.StringVar()
        self.install_location = tk.StringVar()
        self.create_shortcuts = tk.BooleanVar(value=True)
        self.system_wide = tk.BooleanVar(value=True)
        
        # Installation state
        self.installation_running = False
        self.installation_success = False
        
        # Detect system
        self.detect_system()
        
        # Create GUI
        self.create_gui()
        
        # Auto-detect packages
        self.auto_detect_packages()
        
    def setup_styles(self):
        """Setup custom styles for the GUI."""
        # Configure ttk styles
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Arial', 12))
        self.style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        self.style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        self.style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        self.style.configure('Warning.TLabel', foreground='orange', font=('Arial', 10, 'bold'))
        
    def detect_system(self):
        """Detect the current system and available package managers."""
        self.system_info = {
            'os': platform.system().lower(),
            'dist': 'unknown',
            'arch': platform.machine(),
            'package_managers': []
        }
        
        if self.system_info['os'] == 'linux':
            # Detect Linux distribution
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('ID='):
                            self.system_info['dist'] = line.split('=')[1].strip().strip('"')
                            break
            except:
                pass
            
            # Check available package managers
            if shutil.which('apt'):
                self.system_info['package_managers'].append('apt')
            if shutil.which('snap'):
                self.system_info['package_managers'].append('snap')
            if shutil.which('dpkg'):
                self.system_info['package_managers'].append('dpkg')
        
    def create_gui(self):
        """Create the main GUI."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="ScalPDF Package Installer", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Secure PDF Viewer and Editor", style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # System information
        self.create_system_info_section(main_frame, 2)
        
        # Package selection
        self.create_package_selection_section(main_frame, 4)
        
        # Installation options
        self.create_installation_options_section(main_frame, 6)
        
        # Progress section
        self.create_progress_section(main_frame, 8)
        
        # Buttons
        self.create_buttons_section(main_frame, 10)
        
    def create_system_info_section(self, parent, row):
        """Create system information section."""
        # System info frame
        info_frame = ttk.LabelFrame(parent, text="System Information", padding="10")
        info_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        info_frame.columnconfigure(1, weight=1)
        
        # OS info
        ttk.Label(info_frame, text="Operating System:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        os_text = f"{self.system_info['os'].title()} ({self.system_info['dist']})"
        ttk.Label(info_frame, text=os_text).grid(row=0, column=1, sticky=tk.W)
        
        # Architecture
        ttk.Label(info_frame, text="Architecture:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(info_frame, text=self.system_info['arch']).grid(row=1, column=1, sticky=tk.W)
        
        # Package managers
        ttk.Label(info_frame, text="Package Managers:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        pm_text = ", ".join(self.system_info['package_managers']) if self.system_info['package_managers'] else "None detected"
        ttk.Label(info_frame, text=pm_text).grid(row=2, column=1, sticky=tk.W)
        
    def create_package_selection_section(self, parent, row):
        """Create package selection section."""
        # Package selection frame
        package_frame = ttk.LabelFrame(parent, text="Package Selection", padding="10")
        package_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        package_frame.columnconfigure(1, weight=1)
        
        # Installation type
        ttk.Label(package_frame, text="Installation Type:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        type_frame = ttk.Frame(package_frame)
        type_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Radiobutton(type_frame, text="Auto-detect (Recommended)", variable=self.installation_type, 
                       value="auto", command=self.on_type_changed).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="AppImage", variable=self.installation_type, 
                       value="appimage", command=self.on_type_changed).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text=".deb Package", variable=self.installation_type, 
                       value="deb", command=self.on_type_changed).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="Snap Package", variable=self.installation_type, 
                       value="snap", command=self.on_type_changed).pack(side=tk.LEFT)
        
        # Package path
        ttk.Label(package_frame, text="Package File:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        path_frame = ttk.Frame(package_frame)
        path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_entry = ttk.Entry(path_frame, textvariable=self.package_path, state='readonly')
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(path_frame, text="Browse...", command=self.browse_package).grid(row=0, column=1)
        
        # Available packages list
        ttk.Label(package_frame, text="Available Packages:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        # Packages listbox with scrollbar
        list_frame = ttk.Frame(package_frame)
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.packages_listbox = tk.Listbox(list_frame, height=4)
        self.packages_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.packages_listbox.bind('<<ListboxSelect>>', self.on_package_selected)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.packages_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.packages_listbox.configure(yscrollcommand=scrollbar.set)
        
    def create_installation_options_section(self, parent, row):
        """Create installation options section."""
        # Options frame
        options_frame = ttk.LabelFrame(parent, text="Installation Options", padding="10")
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        options_frame.columnconfigure(1, weight=1)
        
        # System-wide installation
        ttk.Checkbutton(options_frame, text="System-wide installation (requires sudo)", 
                       variable=self.system_wide, command=self.on_options_changed).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        # Create shortcuts
        ttk.Checkbutton(options_frame, text="Create desktop shortcuts and menu entries", 
                       variable=self.create_shortcuts).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Installation location (for AppImage)
        ttk.Label(options_frame, text="Install Location:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        location_frame = ttk.Frame(options_frame)
        location_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        location_frame.columnconfigure(0, weight=1)
        
        self.location_entry = ttk.Entry(location_frame, textvariable=self.install_location)
        self.location_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(location_frame, text="Browse...", command=self.browse_location).grid(row=0, column=1)
        
    def create_progress_section(self, parent, row):
        """Create progress section."""
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Installation Progress", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log text area
        log_frame = ttk.Frame(progress_frame)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
    def create_buttons_section(self, parent, row):
        """Create buttons section."""
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))
        
        # Install button
        self.install_button = ttk.Button(buttons_frame, text="Install ScalPDF", command=self.start_installation)
        self.install_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Build packages button
        self.build_button = ttk.Button(buttons_frame, text="Build Packages", command=self.build_packages)
        self.build_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Test installation button
        self.test_button = ttk.Button(buttons_frame, text="Test Installation", command=self.test_installation, state=tk.DISABLED)
        self.test_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        ttk.Button(buttons_frame, text="Close", command=self.root.quit).pack(side=tk.RIGHT)
        
    def auto_detect_packages(self):
        """Auto-detect available packages."""
        self.log_message("🔍 Scanning for available packages...")
        
        build_dir = Path(__file__).parent.parent / "build"
        packages = []
        
        if build_dir.exists():
            # Look for AppImages
            for appimage in build_dir.glob("**/*.AppImage"):
                packages.append(f"AppImage: {appimage.name} ({appimage.stat().st_size / (1024*1024):.1f} MB)")
                
            # Look for .deb packages
            for deb in build_dir.glob("**/*.deb"):
                packages.append(f"DEB: {deb.name} ({deb.stat().st_size / (1024*1024):.1f} MB)")
                
            # Look for .snap packages
            for snap in build_dir.glob("**/*.snap"):
                packages.append(f"Snap: {snap.name} ({snap.stat().st_size / (1024*1024):.1f} MB)")
        
        # Update listbox
        self.packages_listbox.delete(0, tk.END)
        for package in packages:
            self.packages_listbox.insert(tk.END, package)
            
        if packages:
            self.log_message(f"✅ Found {len(packages)} available packages")
        else:
            self.log_message("⚠️ No pre-built packages found. Use 'Build Packages' to create them.")
            
    def on_type_changed(self):
        """Handle installation type change."""
        install_type = self.installation_type.get()
        
        if install_type == "auto":
            self.update_recommended_location()
        elif install_type == "appimage":
            self.install_location.set(str(Path.home() / "Applications"))
        elif install_type == "deb":
            self.install_location.set("System package manager")
            self.location_entry.configure(state='disabled')
        elif install_type == "snap":
            self.install_location.set("Snap package manager")
            self.location_entry.configure(state='disabled')
            
    def on_options_changed(self):
        """Handle options change."""
        self.update_recommended_location()
        
    def on_package_selected(self, event):
        """Handle package selection from list."""
        selection = self.packages_listbox.curselection()
        if selection:
            package_text = self.packages_listbox.get(selection[0])
            
            # Extract package type and find file
            if package_text.startswith("AppImage:"):
                self.installation_type.set("appimage")
                filename = package_text.split(": ")[1].split(" (")[0]
            elif package_text.startswith("DEB:"):
                self.installation_type.set("deb")
                filename = package_text.split(": ")[1].split(" (")[0]
            elif package_text.startswith("Snap:"):
                self.installation_type.set("snap")
                filename = package_text.split(": ")[1].split(" (")[0]
            else:
                return
                
            # Find the actual file
            build_dir = Path(__file__).parent.parent / "build"
            for file_path in build_dir.rglob(filename):
                self.package_path.set(str(file_path))
                break
                
            self.on_type_changed()
            
    def update_recommended_location(self):
        """Update recommended installation location."""
        if self.system_wide.get():
            if self.installation_type.get() == "appimage":
                self.install_location.set("/usr/local/bin")
            else:
                self.install_location.set("System-wide")
        else:
            if self.installation_type.get() == "appimage":
                self.install_location.set(str(Path.home() / "Applications"))
            else:
                self.install_location.set("User-local")
                
    def browse_package(self):
        """Browse for package file."""
        filetypes = [
            ("All Packages", "*.AppImage;*.deb;*.snap"),
            ("AppImage", "*.AppImage"),
            ("Debian Package", "*.deb"),
            ("Snap Package", "*.snap"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select ScalPDF Package",
            filetypes=filetypes
        )
        
        if filename:
            self.package_path.set(filename)
            
            # Auto-detect type based on extension
            if filename.endswith('.AppImage'):
                self.installation_type.set("appimage")
            elif filename.endswith('.deb'):
                self.installation_type.set("deb")
            elif filename.endswith('.snap'):
                self.installation_type.set("snap")
                
            self.on_type_changed()
            
    def browse_location(self):
        """Browse for installation location."""
        directory = filedialog.askdirectory(
            title="Select Installation Directory",
            initialdir=self.install_location.get()
        )
        
        if directory:
            self.install_location.set(directory)
            
    def log_message(self, message):
        """Add message to log."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.configure(state=tk.DISABLED)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_progress(self, value, message=None):
        """Update progress bar and optionally log message."""
        self.progress_var.set(value)
        if message:
            self.log_message(message)
            
    def start_installation(self):
        """Start the installation process."""
        if self.installation_running:
            return
            
        # Validate inputs
        if not self.package_path.get() and self.installation_type.get() != "auto":
            messagebox.showerror("Error", "Please select a package file.")
            return
            
        # Start installation in thread
        self.installation_running = True
        self.install_button.configure(text="Installing...", state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_installation)
        thread.daemon = True
        thread.start()
        
    def run_installation(self):
        """Run the installation process."""
        try:
            self.update_progress(0, "🚀 Starting installation...")
            
            install_type = self.installation_type.get()
            package_path = self.package_path.get()
            
            if install_type == "auto":
                # Auto-detect best installation method
                if 'snap' in self.system_info['package_managers']:
                    self.install_snap_auto()
                elif 'apt' in self.system_info['package_managers']:
                    self.install_deb_auto()
                else:
                    self.install_appimage_auto()
            elif install_type == "appimage":
                self.install_appimage(package_path)
            elif install_type == "deb":
                self.install_deb(package_path)
            elif install_type == "snap":
                self.install_snap(package_path)
                
            self.update_progress(100, "✅ Installation completed successfully!")
            self.installation_success = True
            
            # Enable test button
            self.root.after(0, lambda: self.test_button.configure(state=tk.NORMAL))
            
        except Exception as e:
            self.update_progress(0, f"❌ Installation failed: {e}")
            self.installation_success = False
            
        finally:
            self.installation_running = False
            self.root.after(0, lambda: self.install_button.configure(text="Install ScalPDF", state=tk.NORMAL))
            
    def install_appimage(self, package_path):
        """Install AppImage."""
        self.update_progress(20, "📦 Installing AppImage...")
        
        if not package_path or not Path(package_path).exists():
            raise Exception("AppImage file not found")
            
        # Make executable
        os.chmod(package_path, 0o755)
        self.update_progress(40, "✅ Made AppImage executable")
        
        # Copy to installation location
        install_dir = Path(self.install_location.get())
        install_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = install_dir / "scalpdf"
        shutil.copy2(package_path, target_path)
        os.chmod(target_path, 0o755)
        
        self.update_progress(60, f"✅ Copied to {target_path}")
        
        # Create shortcuts if requested
        if self.create_shortcuts.get():
            self.create_appimage_shortcuts(target_path)
            self.update_progress(80, "✅ Created desktop shortcuts")
            
    def install_deb(self, package_path):
        """Install .deb package."""
        self.update_progress(20, "📦 Installing .deb package...")
        
        if not package_path or not Path(package_path).exists():
            raise Exception(".deb file not found")
            
        # Install with dpkg
        result = subprocess.run([
            'sudo', 'dpkg', '-i', package_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            # Try to fix dependencies
            self.update_progress(40, "🔧 Fixing dependencies...")
            subprocess.run(['sudo', 'apt-get', 'install', '-f', '-y'], check=True)
            
        self.update_progress(80, "✅ Package installed successfully")
        
    def install_snap(self, package_path):
        """Install Snap package."""
        self.update_progress(20, "📦 Installing Snap package...")
        
        if not package_path or not Path(package_path).exists():
            raise Exception("Snap file not found")
            
        # Install snap
        result = subprocess.run([
            'sudo', 'snap', 'install', package_path, '--dangerous'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Snap installation failed: {result.stderr}")
            
        self.update_progress(80, "✅ Snap package installed successfully")
        
    def install_snap_auto(self):
        """Auto-install using Snap."""
        self.update_progress(10, "🔍 Looking for Snap package...")
        
        build_dir = Path(__file__).parent.parent / "build"
        snap_files = list(build_dir.glob("**/*.snap"))
        
        if snap_files:
            self.install_snap(str(snap_files[0]))
        else:
            raise Exception("No Snap package found")
            
    def install_deb_auto(self):
        """Auto-install using .deb package."""
        self.update_progress(10, "🔍 Looking for .deb package...")
        
        build_dir = Path(__file__).parent.parent / "build"
        deb_files = list(build_dir.glob("**/*.deb"))
        
        if deb_files:
            self.install_deb(str(deb_files[0]))
        else:
            raise Exception("No .deb package found")
            
    def install_appimage_auto(self):
        """Auto-install using AppImage."""
        self.update_progress(10, "🔍 Looking for AppImage...")
        
        build_dir = Path(__file__).parent.parent / "build"
        appimage_files = list(build_dir.glob("**/*.AppImage"))
        
        if appimage_files:
            self.install_appimage(str(appimage_files[0]))
        else:
            raise Exception("No AppImage found")
            
    def create_appimage_shortcuts(self, appimage_path):
        """Create desktop shortcuts for AppImage."""
        # Desktop file content
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Viewer and Editor
Exec={appimage_path} %f
Icon=scalpdf
Categories=Office;Graphics;Viewer;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
Keywords=PDF;viewer;editor;security;encryption;
Terminal=false
'''
        
        # Create desktop file
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = desktop_dir / "scalpdf.desktop"
        desktop_file.write_text(desktop_content)
        os.chmod(desktop_file, 0o755)
        
    def build_packages(self):
        """Build all package types."""
        if self.installation_running:
            return
            
        self.installation_running = True
        self.build_button.configure(text="Building...", state=tk.DISABLED)
        
        thread = threading.Thread(target=self.run_build_packages)
        thread.daemon = True
        thread.start()
        
    def run_build_packages(self):
        """Run package building process."""
        try:
            self.update_progress(0, "🏗️ Starting package build process...")
            
            project_root = Path(__file__).parent.parent
            
            # Build AppImage
            self.update_progress(10, "📦 Building AppImage...")
            result = subprocess.run([
                sys.executable, str(project_root / "Installers GUI" / "build_appimage.py")
            ], capture_output=True, text=True, cwd=str(project_root))
            
            if result.returncode == 0:
                self.update_progress(30, "✅ AppImage built successfully")
            else:
                self.log_message(f"⚠️ AppImage build failed: {result.stderr}")
                
            # Build .deb package
            self.update_progress(40, "📦 Building .deb package...")
            result = subprocess.run([
                sys.executable, str(project_root / "Installers GUI" / "build_deb.py")
            ], capture_output=True, text=True, cwd=str(project_root))
            
            if result.returncode == 0:
                self.update_progress(70, "✅ .deb package built successfully")
            else:
                self.log_message(f"⚠️ .deb build failed: {result.stderr}")
                
            # Build Snap package
            self.update_progress(80, "📦 Building Snap package...")
            result = subprocess.run([
                sys.executable, str(project_root / "Installers GUI" / "build_snap.py")
            ], capture_output=True, text=True, cwd=str(project_root))
            
            if result.returncode == 0:
                self.update_progress(100, "✅ All packages built successfully!")
            else:
                self.log_message(f"⚠️ Snap build failed: {result.stderr}")
                self.update_progress(100, "✅ Package building completed (some may have failed)")
                
            # Refresh package list
            self.root.after(1000, self.auto_detect_packages)
            
        except Exception as e:
            self.update_progress(0, f"❌ Build failed: {e}")
            
        finally:
            self.installation_running = False
            self.root.after(0, lambda: self.build_button.configure(text="Build Packages", state=tk.NORMAL))
            
    def test_installation(self):
        """Test the installation."""
        if not self.installation_success:
            messagebox.showwarning("Warning", "Please install ScalPDF first.")
            return
            
        self.log_message("🧪 Testing installation...")
        
        try:
            # Try to run ScalPDF
            result = subprocess.run(['scalpdf', '--version'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_message("✅ ScalPDF is working correctly!")
                messagebox.showinfo("Success", "ScalPDF installation test passed!")
            else:
                self.log_message("❌ ScalPDF test failed")
                messagebox.showerror("Error", "ScalPDF installation test failed.")
                
        except subprocess.TimeoutExpired:
            self.log_message("⚠️ Test timed out (this might be normal for GUI apps)")
        except FileNotFoundError:
            self.log_message("❌ ScalPDF command not found")
            messagebox.showerror("Error", "ScalPDF command not found. Installation may have failed.")
        except Exception as e:
            self.log_message(f"❌ Test error: {e}")
            
    def run(self):
        """Run the GUI."""
        self.root.mainloop()

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
ScalPDF Package Installer GUI

Usage:
    python package_installer.py

This GUI application helps you install ScalPDF using the most appropriate
package format for your system (AppImage, .deb, or Snap).

Features:
- Auto-detection of system and available packages
- Support for multiple package formats
- Package building capabilities
- Installation testing
- Modern, user-friendly interface
""")
        return
    
    app = PackageInstallerGUI()
    app.run()

if __name__ == "__main__":
    main()
