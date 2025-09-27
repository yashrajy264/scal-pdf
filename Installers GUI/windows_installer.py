#!/usr/bin/env python3
"""
ScalPDF Windows GUI Installer
Windows-specific GUI installer with native Windows features
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
import winreg
import ctypes
from ctypes import wintypes

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    print("Error: tkinter not available. Please install Python with tkinter support.")
    sys.exit(1)


class WindowsScalPDFInstaller:
    """Windows-specific GUI installer for ScalPDF."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF Setup")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Set Windows-specific properties
        try:
            # Set window icon (if available)
            self.root.iconbitmap(default="installer.ico")
        except:
            pass
        
        # Configure Windows-style theme
        self.style = ttk.Style()
        try:
            self.style.theme_use('vista')  # Windows Vista/7+ theme
        except:
            self.style.theme_use('clam')
        
        # Installation state
        self.install_path = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "ScalPDF"
        self.user_install = tk.BooleanVar(value=True)  # Install for current user by default
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.add_to_path = tk.BooleanVar(value=True)
        self.associate_pdf = tk.BooleanVar(value=False)  # Don't associate by default
        self.installing = False
        
        # Update install path based on user/system choice
        self.update_install_path()
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def update_install_path(self):
        """Update install path based on user/system installation choice."""
        if self.user_install.get():
            self.install_path = Path(os.environ.get("LOCALAPPDATA", "")) / "ScalPDF"
        else:
            self.install_path = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "ScalPDF"
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"700x600+{x}+{y}")
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame with Windows-style padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header with Windows-style layout
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 25))
        header_frame.columnconfigure(1, weight=1)
        
        # Logo/Icon
        logo_label = ttk.Label(header_frame, text="📄", font=("Segoe UI", 42))
        logo_label.grid(row=0, column=0, padx=(0, 20), rowspan=3)
        
        # Title and description
        title_label = ttk.Label(header_frame, text="ScalPDF Setup Wizard", 
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        desc_label = ttk.Label(header_frame, 
                              text="This wizard will install ScalPDF on your computer.",
                              font=("Segoe UI", 9))
        desc_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        
        version_label = ttk.Label(header_frame, text="Version 1.0.0 • Secure PDF Management", 
                                 font=("Segoe UI", 8), foreground="gray")
        version_label.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(2, 0))
        
        # Installation type
        install_type_frame = ttk.LabelFrame(main_frame, text="Installation Type", padding="12")
        install_type_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Radiobutton(install_type_frame, text="Install for current user only (Recommended)", 
                       variable=self.user_install, value=True, 
                       command=self.on_install_type_changed).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        user_desc = ttk.Label(install_type_frame, 
                             text="Installs to your user directory. No administrator rights required.",
                             font=("Segoe UI", 8), foreground="gray")
        user_desc.grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        
        ttk.Radiobutton(install_type_frame, text="Install for all users", 
                       variable=self.user_install, value=False,
                       command=self.on_install_type_changed).grid(row=2, column=0, sticky=tk.W, pady=(8, 2))
        
        system_desc = ttk.Label(install_type_frame, 
                               text="Installs to Program Files. Requires administrator rights.",
                               font=("Segoe UI", 8), foreground="gray")
        system_desc.grid(row=3, column=0, sticky=tk.W, padx=(20, 0))
        
        # Installation location
        location_frame = ttk.LabelFrame(main_frame, text="Installation Location", padding="12")
        location_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        location_frame.columnconfigure(1, weight=1)
        
        ttk.Label(location_frame, text="Destination folder:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        path_frame = ttk.Frame(location_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, font=("Consolas", 9))
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_install_path)
        browse_btn.grid(row=0, column=1)
        
        # Space required info
        space_label = ttk.Label(location_frame, text="Space required: ~150 MB", 
                               font=("Segoe UI", 8), foreground="gray")
        space_label.grid(row=2, column=0, sticky=tk.W)
        
        # Installation options
        options_frame = ttk.LabelFrame(main_frame, text="Additional Options", padding="12")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Checkbutton(options_frame, text="Create desktop shortcut", 
                       variable=self.create_desktop_shortcut).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Add to Start Menu", 
                       variable=self.create_start_menu).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Add to system PATH (enables command-line usage)", 
                       variable=self.add_to_path).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Associate with PDF files (open PDFs with ScalPDF)", 
                       variable=self.associate_pdf).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Features summary
        features_frame = ttk.LabelFrame(main_frame, text="What's Included", padding="12")
        features_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        features_text = """✓ PDF Viewer with zoom, rotation, and navigation
✓ Annotation tools (highlights, notes, comments)
✓ PDF editing (merge, split, reorder pages)
✓ Advanced compression with quality presets
✓ Military-grade AES-256 encryption
✓ Command-line tools for batch operations
✓ Completely offline - no internet required
✓ Privacy-first design with no data collection"""
        
        features_label = ttk.Label(features_frame, text=features_text, justify=tk.LEFT, 
                                  font=("Segoe UI", 9))
        features_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress frame (initially hidden)
        self.progress_frame = ttk.LabelFrame(main_frame, text="Installation Progress", padding="12")
        self.progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready to install...")
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Log area (initially hidden)
        self.log_frame = ttk.LabelFrame(main_frame, text="Installation Details", padding="8")
        self.log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        self.log_text = ScrolledText(self.log_frame, height=10, font=("Consolas", 8), 
                                    state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initially hide progress and log
        self.progress_frame.grid_remove()
        self.log_frame.grid_remove()
        
        # Buttons with Windows-style layout
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Help button (left side)
        help_btn = ttk.Button(button_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        
        # Main buttons (right side)
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_installation)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(8, 0))
        
        self.install_btn = ttk.Button(button_frame, text="Install", 
                                     command=self.start_installation)
        self.install_btn.pack(side=tk.RIGHT)
        
        # Make install button prominent
        self.style.configure("Install.TButton", font=("Segoe UI", 9, "bold"))
        self.install_btn.configure(style="Install.TButton")
    
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
            self.install_path = Path(selected_dir) / "ScalPDF"
            self.path_var.set(str(self.install_path))
    
    def show_help(self):
        """Show help dialog."""
        help_text = """ScalPDF Setup Help

Installation Types:
• Current User: Installs to your user directory (%LOCALAPPDATA%\\ScalPDF)
  - No administrator rights required
  - Only available to your user account
  - Recommended for most users

• All Users: Installs to Program Files
  - Requires administrator rights
  - Available to all users on this computer
  - Choose this for shared computers

Options:
• Desktop Shortcut: Creates a shortcut on your desktop
• Start Menu: Adds ScalPDF to the Start Menu
• System PATH: Allows running 'scalpdf' from Command Prompt
• PDF Association: Makes ScalPDF the default PDF viewer

System Requirements:
• Windows 7 or later
• Python 3.11 or higher
• 150 MB free disk space
• Internet connection for initial setup (downloads dependencies)

For support, visit: https://github.com/yashrajy264/scal-pdf"""
        
        messagebox.showinfo("Setup Help", help_text)
    
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
    
    def check_admin_rights(self):
        """Check if running with administrator rights."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def start_installation(self):
        """Start the installation process."""
        if self.installing:
            return
        
        # Check if system installation requires admin rights
        if not self.user_install.get() and not self.check_admin_rights():
            result = messagebox.askyesno(
                "Administrator Rights Required",
                "Installing for all users requires administrator rights.\n\n"
                "Would you like to switch to user installation instead?\n\n"
                "Click 'No' to exit and restart as administrator."
            )
            if result:
                self.user_install.set(True)
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
            
            if self.create_start_menu.get():
                self.update_progress("Adding to Start Menu...")
                self.log_message("📱 Adding to Start Menu...")
                self.create_start_menu_entries(install_path)
            
            # Add to PATH
            if self.add_to_path.get():
                self.update_progress("Adding to system PATH...")
                self.log_message("🛤️ Adding to system PATH...")
                self.add_to_system_path(install_path)
            
            # File associations
            if self.associate_pdf.get():
                self.update_progress("Setting up file associations...")
                self.log_message("📄 Setting up PDF file associations...")
                self.create_file_associations(install_path)
            
            # Create uninstaller
            self.update_progress("Creating uninstaller...")
            self.log_message("🗑️ Creating uninstaller...")
            self.create_uninstaller(install_path)
            
            # Register in Windows Programs
            self.update_progress("Registering application...")
            self.log_message("📝 Registering in Windows Programs...")
            self.register_application(install_path)
            
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
                    self.installation_failed("Python 3.11 or higher is required.\n\nPlease install Python from https://python.org")
                    return False
            else:
                self.installation_failed("Python not found.\n\nPlease install Python from https://python.org")
                return False
        except Exception as e:
            self.installation_failed(f"Error checking Python: {e}")
            return False
    
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
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
            
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
            
            # Create a simple icon using PIL if available
            try:
                from PIL import Image, ImageDraw, ImageFont
                
                # Create 256x256 icon
                img = Image.new('RGBA', (256, 256), (37, 99, 235, 255))
                draw = ImageDraw.Draw(img)
                
                # Draw white rectangle (paper)
                draw.rectangle([48, 48, 208, 248], fill=(255, 255, 255, 255))
                
                # Draw text "PDF"
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except:
                    font = ImageFont.load_default()
                
                draw.text((128, 140), "PDF", fill=(37, 99, 235, 255), 
                         font=font, anchor="mm")
                
                # Draw lock symbol
                draw.ellipse([180, 180, 220, 220], outline=(220, 38, 127, 255), width=4)
                draw.rectangle([185, 195, 215, 215], outline=(220, 38, 127, 255), width=4)
                
                # Save as ICO
                icon_path = assets_dir / "icon.ico"
                img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                
                # Also save as PNG
                png_path = assets_dir / "icon.png"
                img.save(png_path, format='PNG')
                
                self.log_message("✅ Application icon created")
                
            except ImportError:
                # Fallback: create a simple text-based icon file
                icon_path = assets_dir / "icon.txt"
                icon_path.write_text("ScalPDF Icon Placeholder")
                self.log_message("⚠️ Created placeholder icon (PIL not available)")
                
        except Exception as e:
            self.log_message(f"⚠️ Icon creation failed: {e}")
    
    def create_desktop_shortcut_file(self, install_path):
        """Create desktop shortcut."""
        try:
            desktop = Path.home() / "Desktop"
            
            # Create VBS script to create shortcut
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{desktop}\\ScalPDF.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{install_path}\\venv\\Scripts\\python.exe"
oLink.Arguments = "{install_path}\\main.py"
oLink.WorkingDirectory = "{install_path}"
oLink.Description = "ScalPDF - Secure PDF Management Tool"
oLink.IconLocation = "{install_path}\\assets\\icon.ico"
oLink.WindowStyle = 1
oLink.Save
'''
            
            vbs_file = install_path / "create_shortcut.vbs"
            vbs_file.write_text(vbs_script)
            
            # Execute VBS script
            subprocess.run(["cscript", "//nologo", str(vbs_file)], 
                          capture_output=True, cwd=str(install_path))
            
            # Clean up VBS file
            vbs_file.unlink()
            
            self.log_message("✅ Desktop shortcut created")
        except Exception as e:
            self.log_message(f"⚠️ Desktop shortcut failed: {e}")
    
    def create_start_menu_entries(self, install_path):
        """Create Start Menu entries."""
        try:
            if self.user_install.get():
                start_menu = Path(os.environ.get("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            else:
                start_menu = Path(os.environ.get("PROGRAMDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            
            start_menu.mkdir(parents=True, exist_ok=True)
            
            # Create VBS script for GUI shortcut
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{start_menu}\\ScalPDF.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{install_path}\\venv\\Scripts\\python.exe"
oLink.Arguments = "{install_path}\\main.py"
oLink.WorkingDirectory = "{install_path}"
oLink.Description = "ScalPDF - Secure PDF Management Tool"
oLink.IconLocation = "{install_path}\\assets\\icon.ico"
oLink.WindowStyle = 1
oLink.Save
'''
            
            vbs_file = install_path / "create_start_menu.vbs"
            vbs_file.write_text(vbs_script)
            
            # Execute VBS script
            subprocess.run(["cscript", "//nologo", str(vbs_file)], 
                          capture_output=True, cwd=str(install_path))
            
            # Clean up VBS file
            vbs_file.unlink()
            
            self.log_message("✅ Start Menu entry created")
        except Exception as e:
            self.log_message(f"⚠️ Start Menu creation failed: {e}")
    
    def add_to_system_path(self, install_path):
        """Add installation to system PATH."""
        try:
            # Create batch launchers
            gui_launcher = install_path / "scalpdf.bat"
            cli_launcher = install_path / "scalpdf-cli.bat"
            
            gui_content = f'''@echo off
cd /d "{install_path}"
call "venv\\Scripts\\activate.bat"
python main.py %*
'''
            
            cli_content = f'''@echo off
cd /d "{install_path}"
call "venv\\Scripts\\activate.bat"
python -m cli.cli %*
'''
            
            gui_launcher.write_text(gui_content)
            cli_launcher.write_text(cli_content)
            
            # Add to PATH
            if self.user_install.get():
                # User PATH
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "PATH")
                    except FileNotFoundError:
                        current_path = ""
                    
                    if str(install_path) not in current_path:
                        new_path = f"{current_path};{install_path}" if current_path else str(install_path)
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            else:
                # System PATH (requires admin)
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment", 
                                   0, winreg.KEY_ALL_ACCESS) as key:
                    current_path, _ = winreg.QueryValueEx(key, "PATH")
                    if str(install_path) not in current_path:
                        new_path = f"{current_path};{install_path}"
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            
            self.log_message("✅ Added to system PATH")
        except Exception as e:
            self.log_message(f"⚠️ PATH addition failed: {e}")
    
    def create_file_associations(self, install_path):
        """Create PDF file associations."""
        try:
            # Register file association
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\.pdf") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "ScalPDF.Document")
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\ScalPDF.Document") as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "PDF Document")
            
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                 "Software\\Classes\\ScalPDF.Document\\shell\\open\\command") as key:
                command = f'"{install_path}\\venv\\Scripts\\python.exe" "{install_path}\\main.py" "%1"'
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, command)
            
            self.log_message("✅ PDF file associations created")
        except Exception as e:
            self.log_message(f"⚠️ File associations failed: {e}")
    
    def register_application(self, install_path):
        """Register application in Windows Programs list."""
        try:
            app_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ScalPDF"
            
            if self.user_install.get():
                root_key = winreg.HKEY_CURRENT_USER
            else:
                root_key = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.CreateKey(root_key, app_key) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "ScalPDF")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "ScalPDF Team")
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, 
                                 f'"{install_path}\\Uninstall.exe"')
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, 
                                 f'"{install_path}\\assets\\icon.ico"')
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            self.log_message("✅ Application registered")
        except Exception as e:
            self.log_message(f"⚠️ Application registration failed: {e}")
    
    def create_uninstaller(self, install_path):
        """Create uninstaller."""
        try:
            uninstaller_content = f'''@echo off
title ScalPDF Uninstaller
echo.
echo ScalPDF Uninstaller
echo ==================
echo.
echo This will remove ScalPDF from your computer.
echo.
pause

echo Removing application files...
if exist "{install_path}" (
    rmdir /s /q "{install_path}"
    echo ✅ Application files removed
)

echo Removing shortcuts...
del "%USERPROFILE%\\Desktop\\ScalPDF.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ScalPDF.lnk" 2>nul
echo ✅ Shortcuts removed

echo Removing registry entries...
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ScalPDF" /f 2>nul
reg delete "HKCU\\Software\\Classes\\.pdf" /f 2>nul
reg delete "HKCU\\Software\\Classes\\ScalPDF.Document" /f 2>nul
echo ✅ Registry entries removed

echo.
echo ScalPDF has been successfully uninstalled.
echo.
pause
'''
            
            uninstaller = install_path / "Uninstall.bat"
            uninstaller.write_text(uninstaller_content)
            
            self.log_message("✅ Uninstaller created")
        except Exception as e:
            self.log_message(f"⚠️ Uninstaller creation failed: {e}")
    
    def test_installation(self, install_path):
        """Test the installation."""
        try:
            python_exe = install_path / "venv" / "Scripts" / "python.exe"
            
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
        
        if self.create_start_menu.get():
            self.log_message("• Find ScalPDF in the Start Menu")
        
        if self.add_to_path.get():
            self.log_message("• Run 'scalpdf' from Command Prompt (after restart)")
        
        if self.associate_pdf.get():
            self.log_message("• Double-click PDF files to open with ScalPDF")
        
        self.install_btn.config(text="Installation Complete", state=tk.DISABLED)
        self.cancel_btn.config(text="Finish", state=tk.NORMAL)
        
        # Show success message
        messagebox.showinfo(
            "Installation Complete",
            "ScalPDF has been installed successfully!\n\n"
            "You can now use ScalPDF to manage your PDF files securely.\n\n"
            "Click 'Finish' to close the installer."
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
    # Check if running on Windows
    if platform.system() != "Windows":
        print("This installer is designed for Windows only.")
        return 1
    
    # Check if tkinter is available
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter is not available.")
        print("Please install Python with tkinter support.")
        return 1
    
    # Create and run installer
    installer = WindowsScalPDFInstaller()
    installer.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
