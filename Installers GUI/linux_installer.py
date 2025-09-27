#!/usr/bin/env python3
"""
ScalPDF Linux GUI Installer
Linux-specific GUI installer with native Linux features
"""

import sys
import os
import platform
import subprocess
import threading
import tempfile
import shutil
from pathlib import Path
import json
import pwd
import grp

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    print("Error: tkinter not available. Please install python3-tk")
    print("Ubuntu/Debian: sudo apt install python3-tk")
    print("Fedora: sudo dnf install tkinter")
    sys.exit(1)


class LinuxScalPDFInstaller:
    """Linux-specific GUI installer for ScalPDF."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF Installer")
        self.root.geometry("650x550")
        self.root.resizable(False, False)
        
        # Configure Linux-style theme
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
            self.style.theme_use('alt')
        
        # Installation state
        self.install_path = Path.home() / ".local" / "share" / "scalpdf"
        self.system_install = tk.BooleanVar(value=False)  # User install by default
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_app_menu = tk.BooleanVar(value=True)
        self.add_to_path = tk.BooleanVar(value=True)
        self.install_system_deps = tk.BooleanVar(value=True)
        self.installing = False
        
        # Detect distribution
        self.distro = self.detect_distribution()
        
        # Update install path based on system/user choice
        self.update_install_path()
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def detect_distribution(self):
        """Detect Linux distribution."""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'ubuntu' in content.lower() or 'debian' in content.lower():
                    return 'debian'
                elif 'fedora' in content.lower() or 'rhel' in content.lower() or 'centos' in content.lower():
                    return 'fedora'
                elif 'arch' in content.lower():
                    return 'arch'
                elif 'opensuse' in content.lower():
                    return 'opensuse'
        except:
            pass
        return 'unknown'
    
    def update_install_path(self):
        """Update install path based on system/user installation choice."""
        if self.system_install.get():
            self.install_path = Path("/opt/scalpdf")
        else:
            self.install_path = Path.home() / ".local" / "share" / "scalpdf"
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.root.winfo_screenheight() // 2) - (550 // 2)
        self.root.geometry(f"650x550+{x}+{y}")
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Logo/Icon
        logo_label = ttk.Label(header_frame, text="📄", font=("DejaVu Sans", 36))
        logo_label.grid(row=0, column=0, padx=(0, 15), rowspan=3)
        
        # Title and description
        title_label = ttk.Label(header_frame, text="ScalPDF Installer", 
                               font=("DejaVu Sans", 16, "bold"))
        title_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        desc_label = ttk.Label(header_frame, 
                              text="Install ScalPDF - Secure PDF Management Tool",
                              font=("DejaVu Sans", 10))
        desc_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(3, 0))
        
        # Distribution info
        distro_text = f"Detected: {self.get_distro_name()}"
        distro_label = ttk.Label(header_frame, text=distro_text, 
                                font=("DejaVu Sans", 8), foreground="gray")
        distro_label.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(2, 0))
        
        # Installation type
        install_type_frame = ttk.LabelFrame(main_frame, text="Installation Type", padding="10")
        install_type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Radiobutton(install_type_frame, text="Install for current user (Recommended)", 
                       variable=self.system_install, value=False, 
                       command=self.on_install_type_changed).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        user_desc = ttk.Label(install_type_frame, 
                             text="Installs to ~/.local/share/scalpdf - No root privileges required",
                             font=("DejaVu Sans", 8), foreground="gray")
        user_desc.grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        
        ttk.Radiobutton(install_type_frame, text="System-wide installation", 
                       variable=self.system_install, value=True,
                       command=self.on_install_type_changed).grid(row=2, column=0, sticky=tk.W, pady=(8, 2))
        
        system_desc = ttk.Label(install_type_frame, 
                               text="Installs to /opt/scalpdf - Requires root privileges (sudo)",
                               font=("DejaVu Sans", 8), foreground="gray")
        system_desc.grid(row=3, column=0, sticky=tk.W, padx=(20, 0))
        
        # Installation location
        location_frame = ttk.LabelFrame(main_frame, text="Installation Location", padding="10")
        location_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        location_frame.columnconfigure(1, weight=1)
        
        ttk.Label(location_frame, text="Install to:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        path_frame = ttk.Frame(location_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, font=("monospace", 9))
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_install_path)
        browse_btn.grid(row=0, column=1)
        
        # Space info
        space_label = ttk.Label(location_frame, text="Space required: ~150 MB", 
                               font=("DejaVu Sans", 8), foreground="gray")
        space_label.grid(row=2, column=0, sticky=tk.W)
        
        # Installation options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Checkbutton(options_frame, text="Create desktop shortcut", 
                       variable=self.create_desktop_shortcut).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Add to application menu", 
                       variable=self.create_app_menu).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Add to PATH (enables 'scalpdf' command)", 
                       variable=self.add_to_path).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Install system dependencies (Qt, graphics libraries)", 
                       variable=self.install_system_deps).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # System dependencies info
        deps_info = self.get_dependencies_info()
        if deps_info:
            deps_label = ttk.Label(options_frame, text=deps_info, 
                                  font=("DejaVu Sans", 8), foreground="gray")
            deps_label.grid(row=4, column=0, sticky=tk.W, padx=(20, 0))
        
        # Features summary
        features_frame = ttk.LabelFrame(main_frame, text="Features", padding="10")
        features_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        features_text = """✓ PDF viewer with zoom, rotation, and page navigation
✓ Annotation tools (highlights, underlines, sticky notes)
✓ PDF editing (merge, split, reorder, delete pages)
✓ Smart compression with quality presets
✓ AES-256-GCM encryption with Argon2id key derivation
✓ Command-line interface for batch operations
✓ Completely offline - no internet connection required
✓ Privacy-first design with zero data collection"""
        
        features_label = ttk.Label(features_frame, text=features_text, justify=tk.LEFT, 
                                  font=("DejaVu Sans", 9))
        features_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress frame (initially hidden)
        self.progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", padding="10")
        self.progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready to install...")
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Log area (initially hidden)
        self.log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="5")
        self.log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        self.log_text = ScrolledText(self.log_frame, height=8, font=("monospace", 8), 
                                    state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initially hide progress and log
        self.progress_frame.grid_remove()
        self.log_frame.grid_remove()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Help button (left side)
        help_btn = ttk.Button(button_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        
        # Main buttons (right side)
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_installation)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        self.install_btn = ttk.Button(button_frame, text="Install ScalPDF", 
                                     command=self.start_installation)
        self.install_btn.pack(side=tk.RIGHT)
    
    def get_distro_name(self):
        """Get friendly distribution name."""
        distro_names = {
            'debian': 'Ubuntu/Debian',
            'fedora': 'Fedora/RHEL',
            'arch': 'Arch Linux',
            'opensuse': 'openSUSE',
            'unknown': 'Unknown Linux'
        }
        return distro_names.get(self.distro, 'Unknown Linux')
    
    def get_dependencies_info(self):
        """Get distribution-specific dependencies info."""
        if self.distro == 'debian':
            return "Will install: python3-tk libxcb-xinerama0 libgl1-mesa-glx libfontconfig1"
        elif self.distro == 'fedora':
            return "Will install: tkinter libxcb mesa-libGL fontconfig"
        elif self.distro == 'arch':
            return "Will install: tk libxcb mesa glib2 fontconfig"
        else:
            return "System dependencies may need manual installation"
    
    def on_install_type_changed(self):
        """Handle installation type change."""
        self.update_install_path()
        self.path_var.set(str(self.install_path))
    
    def browse_install_path(self):
        """Browse for installation directory."""
        if self.installing:
            return
        
        initial_dir = Path(self.path_var.get()).parent
        selected_dir = filedialog.askdirectory(
            title="Select Installation Directory",
            initialdir=str(initial_dir)
        )
        
        if selected_dir:
            self.install_path = Path(selected_dir) / "scalpdf"
            self.path_var.set(str(self.install_path))
    
    def show_help(self):
        """Show help dialog."""
        help_text = f"""ScalPDF Linux Installer Help

Installation Types:
• Current User: Installs to ~/.local/share/scalpdf
  - No root privileges required
  - Only available to your user account
  - Recommended for most users

• System-wide: Installs to /opt/scalpdf
  - Requires root privileges (sudo)
  - Available to all users on this system
  - Choose for shared systems

Options:
• Desktop Shortcut: Creates shortcut on desktop
• Application Menu: Adds to system application menu
• PATH: Adds 'scalpdf' and 'scalpdf-cli' commands
• System Dependencies: Installs required system packages

Detected Distribution: {self.get_distro_name()}

System Requirements:
• Python 3.11 or higher
• Qt libraries (will be installed if selected)
• 150 MB free disk space

For support, visit: https://github.com/yashrajy264/scal-pdf"""
        
        messagebox.showinfo("Installer Help", help_text)
    
    def log_message(self, message):
        """Add message to log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_progress(self, message):
        """Update progress label."""
        self.progress_label.config(text=message)
        self.root.update_idletasks()
    
    def start_installation(self):
        """Start the installation process."""
        if self.installing:
            return
        
        # Check if system installation requires root
        if self.system_install.get():
            if os.geteuid() != 0:
                result = messagebox.askyesno(
                    "Root Privileges Required",
                    "System-wide installation requires root privileges.\n\n"
                    "Would you like to switch to user installation instead?\n\n"
                    "Click 'No' to exit and restart with sudo."
                )
                if result:
                    self.system_install.set(False)
                    self.on_install_type_changed()
                else:
                    return
        
        # Validate installation path
        install_path = Path(self.path_var.get())
        
        # Check if path already exists and has content
        if install_path.exists() and any(install_path.iterdir()):
            result = messagebox.askyesno(
                "Directory Exists",
                f"The directory '{install_path}' already exists and is not empty.\n\n"
                "Do you want to continue? This will overwrite existing files."
            )
            if not result:
                return
        
        # Show progress UI
        self.progress_frame.grid()
        self.log_frame.grid()
        main_frame = self.progress_frame.master
        main_frame.rowconfigure(6, weight=1)  # Make log frame expandable
        
        # Update UI state
        self.installing = True
        self.install_btn.config(text="Installing...", state=tk.DISABLED)
        self.cancel_btn.config(text="Cancel", state=tk.DISABLED)
        
        # Start progress animation
        self.progress_bar.start(10)
        
        # Start installation in separate thread
        install_thread = threading.Thread(target=self.run_installation)
        install_thread.daemon = True
        install_thread.start()
    
    def run_installation(self):
        """Run the actual installation process."""
        try:
            self.update_progress("Checking system requirements...")
            self.log_message("🔍 Checking system requirements...")
            
            # Check Python
            if not self.check_python():
                return
            
            # Install system dependencies
            if self.install_system_deps.get():
                self.update_progress("Installing system dependencies...")
                self.log_message("📦 Installing system dependencies...")
                self.install_system_dependencies()
            
            # Create installation directory
            self.update_progress("Creating installation directory...")
            self.log_message(f"📁 Creating directory: {self.install_path}")
            
            install_path = Path(self.path_var.get())
            install_path.mkdir(parents=True, exist_ok=True)
            
            # Copy application files
            self.update_progress("Copying application files...")
            self.log_message("📋 Copying application files...")
            
            source_dir = Path(__file__).parent.parent
            self.copy_application_files(source_dir, install_path)
            
            # Create virtual environment
            self.update_progress("Setting up Python environment...")
            self.log_message("🐍 Creating Python virtual environment...")
            
            venv_path = install_path / "venv"
            self.create_virtual_environment(venv_path)
            
            # Install dependencies
            self.update_progress("Installing Python packages...")
            self.log_message("📦 Installing Python dependencies...")
            
            self.install_dependencies(venv_path, install_path)
            
            # Create application icon
            self.update_progress("Creating application resources...")
            self.log_message("🎨 Creating application icon...")
            self.create_application_icon(install_path)
            
            # Create shortcuts
            if self.create_desktop_shortcut.get():
                self.update_progress("Creating desktop shortcut...")
                self.log_message("🖥️ Creating desktop shortcut...")
                self.create_desktop_shortcut_file(install_path)
            
            if self.create_app_menu.get():
                self.update_progress("Adding to application menu...")
                self.log_message("📱 Adding to application menu...")
                self.create_app_menu_entries(install_path)
            
            # Add to PATH
            if self.add_to_path.get():
                self.update_progress("Adding to PATH...")
                self.log_message("🛤️ Adding to PATH...")
                self.add_to_system_path(install_path)
            
            # Create uninstaller
            self.update_progress("Creating uninstaller...")
            self.log_message("🗑️ Creating uninstaller...")
            self.create_uninstaller(install_path)
            
            # Update desktop database
            self.update_progress("Updating system databases...")
            self.log_message("🔄 Updating desktop database...")
            self.update_desktop_database()
            
            # Test installation
            self.update_progress("Testing installation...")
            self.log_message("🧪 Testing installation...")
            self.test_installation(install_path)
            
            # Installation complete
            self.installation_complete()
            
        except Exception as e:
            self.installation_failed(str(e))
    
    def check_python(self):
        """Check Python installation."""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_message(f"✅ Found {version}")
                
                # Check version
                version_info = sys.version_info
                if version_info >= (3, 11):
                    self.log_message("✅ Python version is compatible")
                    return True
                else:
                    self.log_message(f"❌ Python 3.11+ required, found {version_info.major}.{version_info.minor}")
                    self.installation_failed("Python 3.11 or higher is required")
                    return False
            else:
                self.installation_failed("Python not found")
                return False
        except Exception as e:
            self.installation_failed(f"Error checking Python: {e}")
            return False
    
    def install_system_dependencies(self):
        """Install system dependencies."""
        try:
            if self.distro == 'debian':
                # Ubuntu/Debian
                cmd = [
                    "sudo", "apt", "update", "&&",
                    "sudo", "apt", "install", "-y",
                    "python3-pip", "python3-venv", "python3-dev",
                    "libxcb-xinerama0", "libxcb-cursor0", "libxkbcommon-x11-0",
                    "libgl1-mesa-glx", "libglib2.0-0", "libfontconfig1",
                    "libx11-xcb1", "libxcb-glx0", "libxcb-shape0",
                    "libxcb-util1", "libxrender1", "libxi6", "libffi-dev"
                ]
                
                # Run as shell command to handle &&
                result = subprocess.run(
                    " ".join(cmd), shell=True, capture_output=True, text=True
                )
                
            elif self.distro == 'fedora':
                # Fedora/RHEL
                cmd = [
                    "sudo", "dnf", "install", "-y",
                    "python3-pip", "python3-virtualenv", "python3-devel",
                    "libxcb", "libX11-xcb", "mesa-libGL", "glib2",
                    "fontconfig", "libXrender", "libXi", "libffi-devel"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            elif self.distro == 'arch':
                # Arch Linux
                cmd = [
                    "sudo", "pacman", "-S", "--noconfirm",
                    "python-pip", "python-virtualenv",
                    "libxcb", "libx11", "mesa", "glib2",
                    "fontconfig", "libxrender", "libxi", "libffi"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            else:
                self.log_message("⚠️ Unknown distribution - skipping system dependencies")
                return
            
            if result.returncode == 0:
                self.log_message("✅ System dependencies installed")
            else:
                self.log_message(f"⚠️ System dependencies warning: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"⚠️ System dependencies failed: {e}")
    
    def copy_application_files(self, source_dir, install_path):
        """Copy application files to installation directory."""
        try:
            # Files and directories to copy
            items_to_copy = [
                "main.py", "requirements.txt", "setup.py", "LICENSE", "README.md",
                "core", "ui", "cli", "tests"
            ]
            
            for item in items_to_copy:
                source_item = source_dir / item
                if source_item.exists():
                    dest_item = install_path / item
                    if source_item.is_file():
                        shutil.copy2(source_item, dest_item)
                    else:
                        shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
                    self.log_message(f"✅ Copied {item}")
                else:
                    self.log_message(f"⚠️ Skipped missing {item}")
            
        except Exception as e:
            raise Exception(f"Failed to copy files: {e}")
    
    def create_virtual_environment(self, venv_path):
        """Create Python virtual environment."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("✅ Virtual environment created")
            else:
                raise Exception(f"venv creation failed: {result.stderr}")
        except Exception as e:
            raise Exception(f"Failed to create virtual environment: {e}")
    
    def install_dependencies(self, venv_path, install_path):
        """Install Python dependencies."""
        try:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
            
            # Upgrade pip
            result = subprocess.run([
                str(pip_exe), "install", "--upgrade", "pip"
            ], capture_output=True, text=True, cwd=str(install_path))
            
            if result.returncode == 0:
                self.log_message("✅ pip upgraded")
            else:
                self.log_message(f"⚠️ pip upgrade warning: {result.stderr}")
            
            # Install requirements
            requirements_file = install_path / "requirements.txt"
            if requirements_file.exists():
                result = subprocess.run([
                    str(pip_exe), "install", "-r", str(requirements_file)
                ], capture_output=True, text=True, cwd=str(install_path))
                
                if result.returncode == 0:
                    self.log_message("✅ Dependencies installed")
                else:
                    raise Exception(f"pip install failed: {result.stderr}")
            else:
                raise Exception("requirements.txt not found")
                
        except Exception as e:
            raise Exception(f"Failed to install dependencies: {e}")
    
    def create_application_icon(self, install_path):
        """Create application icon."""
        try:
            assets_dir = install_path / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Create SVG icon
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#2563eb" rx="32"/>
  <rect x="48" y="48" width="160" height="200" fill="white" rx="8"/>
  <rect x="64" y="80" width="128" height="8" fill="#e5e7eb" rx="4"/>
  <rect x="64" y="104" width="96" height="8" fill="#e5e7eb" rx="4"/>
  <rect x="64" y="128" width="112" height="8" fill="#e5e7eb" rx="4"/>
  <rect x="64" y="152" width="80" height="8" fill="#e5e7eb" rx="4"/>
  <circle cx="192" cy="192" r="24" fill="#dc2626"/>
  <path d="M184 192 L192 200 L208 184" stroke="white" stroke-width="3" fill="none"/>
  <text x="128" y="40" text-anchor="middle" fill="white" font-family="Arial" font-size="16" font-weight="bold">ScalPDF</text>
</svg>'''
            
            icon_svg = assets_dir / "icon.svg"
            icon_svg.write_text(svg_content)
            
            # Try to convert to PNG if possible
            try:
                # Try with convert (ImageMagick)
                result = subprocess.run([
                    "convert", str(icon_svg), "-resize", "256x256", str(assets_dir / "icon.png")
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Try with inkscape
                    subprocess.run([
                        "inkscape", str(icon_svg), "--export-png", str(assets_dir / "icon.png"),
                        "--export-width", "256", "--export-height", "256"
                    ], capture_output=True, text=True)
                
                self.log_message("✅ Application icon created")
                
            except:
                self.log_message("✅ SVG icon created (PNG conversion not available)")
                
        except Exception as e:
            self.log_message(f"⚠️ Icon creation failed: {e}")
    
    def create_desktop_shortcut_file(self, install_path):
        """Create desktop shortcut."""
        try:
            desktop_dir = Path.home() / "Desktop"
            desktop_dir.mkdir(exist_ok=True)
            
            desktop_file = desktop_dir / "ScalPDF.desktop"
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Management Tool
Exec={install_path}/venv/bin/python {install_path}/main.py
Icon={install_path}/assets/icon.png
Categories=Office;Graphics;Photography;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
"""
            
            desktop_file.write_text(desktop_content)
            desktop_file.chmod(0o755)
            
            self.log_message("✅ Desktop shortcut created")
        except Exception as e:
            self.log_message(f"⚠️ Desktop shortcut failed: {e}")
    
    def create_app_menu_entries(self, install_path):
        """Create application menu entries."""
        try:
            if self.system_install.get():
                apps_dir = Path("/usr/share/applications")
            else:
                apps_dir = Path.home() / ".local" / "share" / "applications"
            
            apps_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = apps_dir / "scalpdf.desktop"
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Management Tool
Exec={install_path}/venv/bin/python {install_path}/main.py
Icon={install_path}/assets/icon.png
Categories=Office;Graphics;Photography;Viewer;
MimeType=application/pdf;
StartupNotify=true
StartupWMClass=ScalPDF
Keywords=PDF;Document;Viewer;Editor;Encryption;Security;
Actions=CLI;

[Desktop Action CLI]
Name=Open CLI
Exec=x-terminal-emulator -e {install_path}/venv/bin/python -m cli.cli
"""
            
            desktop_file.write_text(desktop_content)
            desktop_file.chmod(0o755)
            
            self.log_message("✅ Application menu entry created")
        except Exception as e:
            self.log_message(f"⚠️ Application menu failed: {e}")
    
    def add_to_system_path(self, install_path):
        """Add installation to system PATH."""
        try:
            if self.system_install.get():
                # System-wide installation
                bin_dir = Path("/usr/local/bin")
            else:
                # User installation
                bin_dir = Path.home() / ".local" / "bin"
            
            bin_dir.mkdir(parents=True, exist_ok=True)
            
            # Create launcher scripts
            gui_launcher = bin_dir / "scalpdf"
            cli_launcher = bin_dir / "scalpdf-cli"
            
            gui_content = f'''#!/bin/bash
cd "{install_path}"
source "venv/bin/activate"
python main.py "$@"
'''
            
            cli_content = f'''#!/bin/bash
cd "{install_path}"
source "venv/bin/activate"
python -m cli.cli "$@"
'''
            
            gui_launcher.write_text(gui_content)
            cli_launcher.write_text(cli_content)
            gui_launcher.chmod(0o755)
            cli_launcher.chmod(0o755)
            
            # Add to shell profile if user installation
            if not self.system_install.get():
                shell_profiles = [
                    Path.home() / ".bashrc",
                    Path.home() / ".zshrc",
                    Path.home() / ".profile"
                ]
                
                for profile in shell_profiles:
                    if profile.exists():
                        content = profile.read_text()
                        if str(bin_dir) not in content:
                            with profile.open('a') as f:
                                f.write(f'\n# ScalPDF\nexport PATH="{bin_dir}:$PATH"\n')
                            break
            
            self.log_message("✅ Added to PATH")
        except Exception as e:
            self.log_message(f"⚠️ PATH addition failed: {e}")
    
    def create_uninstaller(self, install_path):
        """Create uninstaller."""
        try:
            uninstaller_content = f'''#!/bin/bash
echo "ScalPDF Uninstaller"
echo "=================="
echo

echo "Removing application files..."
rm -rf "{install_path}"
echo "✅ Application files removed"

echo "Removing shortcuts..."
rm -f "$HOME/Desktop/ScalPDF.desktop"
echo "✅ Desktop shortcut removed"

echo "Removing application menu entries..."
rm -f "$HOME/.local/share/applications/scalpdf.desktop"
if [ -f "/usr/share/applications/scalpdf.desktop" ]; then
    sudo rm -f "/usr/share/applications/scalpdf.desktop"
fi
echo "✅ Menu entries removed"

echo "Removing PATH entries..."
rm -f "$HOME/.local/bin/scalpdf"
rm -f "$HOME/.local/bin/scalpdf-cli"
rm -f "/usr/local/bin/scalpdf"
rm -f "/usr/local/bin/scalpdf-cli"
echo "✅ PATH entries removed"

echo "Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi
echo "✅ Desktop database updated"

echo
echo "ScalPDF has been uninstalled successfully."
echo "You may need to restart your terminal for PATH changes to take effect."
'''
            
            uninstaller = install_path / "uninstall.sh"
            uninstaller.write_text(uninstaller_content)
            uninstaller.chmod(0o755)
            
            self.log_message("✅ Uninstaller created")
        except Exception as e:
            self.log_message(f"⚠️ Uninstaller creation failed: {e}")
    
    def update_desktop_database(self):
        """Update desktop database."""
        try:
            # Update desktop database
            if shutil.which("update-desktop-database"):
                subprocess.run([
                    "update-desktop-database", 
                    str(Path.home() / ".local" / "share" / "applications")
                ], capture_output=True)
            
            # Update icon cache
            if shutil.which("gtk-update-icon-cache"):
                subprocess.run([
                    "gtk-update-icon-cache", 
                    str(Path.home() / ".local" / "share" / "icons" / "hicolor")
                ], capture_output=True)
            
            self.log_message("✅ Desktop database updated")
        except Exception as e:
            self.log_message(f"⚠️ Desktop database update failed: {e}")
    
    def test_installation(self, install_path):
        """Test the installation."""
        try:
            python_exe = install_path / "venv" / "bin" / "python"
            
            # Test imports
            test_script = '''
try:
    import PySide6; print("✅ PySide6 OK")
    import fitz; print("✅ PyMuPDF OK")
    import pikepdf; print("✅ pikepdf OK")
    import PIL; print("✅ Pillow OK")
    import cryptography; print("✅ cryptography OK")
    import argon2; print("✅ argon2 OK")
    print("✅ All dependencies working!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
'''
            
            result = subprocess.run([
                str(python_exe), "-c", test_script
            ], capture_output=True, text=True, cwd=str(install_path))
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.log_message(line)
            else:
                raise Exception(f"Dependency test failed: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"⚠️ Installation test failed: {e}")
    
    def installation_complete(self):
        """Handle successful installation."""
        self.progress_bar.stop()
        self.update_progress("Installation completed successfully!")
        self.log_message("")
        self.log_message("🎉 ScalPDF installed successfully!")
        self.log_message("")
        self.log_message("You can now:")
        
        if self.create_desktop_shortcut.get():
            self.log_message("• Use the desktop shortcut to launch ScalPDF")
        
        if self.create_app_menu.get():
            self.log_message("• Find ScalPDF in your application menu")
        
        if self.add_to_path.get():
            self.log_message("• Run 'scalpdf' from terminal (after restart)")
        
        self.log_message("• Run the uninstaller: ./uninstall.sh")
        
        self.install_btn.config(text="Installation Complete", state=tk.DISABLED)
        self.cancel_btn.config(text="Close", state=tk.NORMAL)
        
        # Show success message
        messagebox.showinfo(
            "Installation Complete",
            "ScalPDF has been installed successfully!\n\n"
            "You can now use ScalPDF to manage your PDF files securely.\n\n"
            "Restart your terminal to use command-line tools."
        )
    
    def installation_failed(self, error_message):
        """Handle failed installation."""
        self.progress_bar.stop()
        self.update_progress("Installation failed!")
        self.log_message(f"❌ Installation failed: {error_message}")
        
        self.install_btn.config(text="Installation Failed", state=tk.DISABLED)
        self.cancel_btn.config(text="Close", state=tk.NORMAL)
        
        messagebox.showerror(
            "Installation Failed",
            f"Installation failed with error:\n\n{error_message}\n\n"
            "Please check the installation log for more details."
        )
    
    def cancel_installation(self):
        """Cancel installation or close window."""
        if self.installing:
            result = messagebox.askyesno(
                "Cancel Installation",
                "Are you sure you want to cancel the installation?"
            )
            if result:
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Run the installer."""
        self.root.mainloop()


def main():
    """Main function."""
    # Check if running on Linux
    if platform.system() != "Linux":
        print("This installer is designed for Linux only.")
        return 1
    
    # Check if tkinter is available
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter is not available.")
        print("Please install tkinter:")
        print("  Ubuntu/Debian: sudo apt install python3-tk")
        print("  Fedora: sudo dnf install tkinter")
        print("  Arch: sudo pacman -S tk")
        return 1
    
    # Create and run installer
    installer = LinuxScalPDFInstaller()
    installer.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
