#!/usr/bin/env python3
"""
ScalPDF Standalone Launcher
Pre-built application launcher that can be run directly without CLI/terminal.
Double-click to launch ScalPDF or install it on your system.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import platform
import shutil
import tempfile
from pathlib import Path
import json
import time
import webbrowser

class ScalPDFLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF - Secure PDF Viewer & Editor")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Set window icon and properties
        self.setup_window()
        
        # Variables
        self.project_root = Path(__file__).parent.parent
        self.current_operation = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()
        
        # State
        self.scalpdf_running = False
        self.installation_status = self.check_installation_status()
        
        # Create GUI
        self.create_gui()
        
        # Auto-detect packages on startup
        self.root.after(1000, self.auto_detect_packages)
        
    def setup_window(self):
        """Setup window properties."""
        try:
            # Try to set window icon
            self.root.iconname("ScalPDF")
            
            # Center window on screen
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Set minimum size
            self.root.minsize(800, 600)
            
        except Exception:
            pass  # Ignore icon/positioning errors
            
    def check_installation_status(self):
        """Check if ScalPDF is already installed."""
        status = {
            'installed': False,
            'type': None,
            'location': None,
            'version': None
        }
        
        # Check for system installation
        if shutil.which('scalpdf'):
            status['installed'] = True
            status['type'] = 'system'
            status['location'] = shutil.which('scalpdf')
            
        # Check for snap installation
        try:
            result = subprocess.run(['snap', 'list', 'scalpdf'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                status['installed'] = True
                status['type'] = 'snap'
                status['location'] = 'snap'
        except:
            pass
            
        # Check for local AppImage
        possible_locations = [
            Path.home() / "Applications" / "scalpdf",
            Path.home() / ".local" / "bin" / "scalpdf",
            self.project_root / "build" / "ScalPDF-x86_64.AppImage"
        ]
        
        for location in possible_locations:
            if location.exists() and os.access(location, os.X_OK):
                status['installed'] = True
                status['type'] = 'appimage'
                status['location'] = str(location)
                break
                
        return status
        
    def create_gui(self):
        """Create the main GUI."""
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 20, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12))
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'))
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        style.configure('Big.TButton', font=('Arial', 12, 'bold'), padding=10)
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header section
        self.create_header_section(main_frame, 0)
        
        # Status section
        self.create_status_section(main_frame, 1)
        
        # Main action buttons
        self.create_action_buttons(main_frame, 2)
        
        # Advanced options
        self.create_advanced_section(main_frame, 3)
        
        # Progress section
        self.create_progress_section(main_frame, 4)
        
        # Footer
        self.create_footer_section(main_frame, 5)
        
    def create_header_section(self, parent, row):
        """Create header section."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="ScalPDF", style='Title.TLabel')
        title_label.grid(row=0, column=0)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, 
                                 text="Secure PDF Viewer & Editor • Offline • Privacy-First", 
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Description
        desc_text = ("ScalPDF is a secure, offline PDF viewer and editor with advanced encryption.\n"
                    "View, annotate, merge, split, compress, and encrypt PDF documents safely.")
        desc_label = ttk.Label(header_frame, text=desc_text, justify=tk.CENTER)
        desc_label.grid(row=2, column=0, pady=(10, 0))
        
    def create_status_section(self, parent, row):
        """Create status section."""
        status_frame = ttk.LabelFrame(parent, text="Installation Status", padding="15")
        status_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        status_frame.columnconfigure(1, weight=1)
        
        # Installation status
        ttk.Label(status_frame, text="Status:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        if self.installation_status['installed']:
            status_text = f"✅ Installed ({self.installation_status['type']})"
            status_style = 'Success.TLabel'
        else:
            status_text = "❌ Not installed"
            status_style = 'Error.TLabel'
            
        self.status_label = ttk.Label(status_frame, text=status_text, style=status_style)
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Location
        if self.installation_status['installed'] and self.installation_status['location']:
            ttk.Label(status_frame, text="Location:", style='Header.TLabel').grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            location_text = str(self.installation_status['location'])
            if len(location_text) > 60:
                location_text = "..." + location_text[-57:]
            ttk.Label(status_frame, text=location_text).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # System info
        ttk.Label(status_frame, text="System:", style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        system_text = f"{platform.system()} {platform.release()}"
        ttk.Label(status_frame, text=system_text).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
    def create_action_buttons(self, parent, row):
        """Create main action buttons."""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=row, column=0, pady=(0, 20))
        
        if self.installation_status['installed']:
            # Launch button (primary)
            self.launch_button = ttk.Button(action_frame, text="🚀 Launch ScalPDF", 
                                          command=self.launch_scalpdf, style='Big.TButton')
            self.launch_button.pack(side=tk.LEFT, padx=(0, 15))
            
            # Reinstall button
            ttk.Button(action_frame, text="🔄 Reinstall", 
                      command=self.show_installation_options).pack(side=tk.LEFT, padx=(0, 15))
        else:
            # Install button (primary)
            ttk.Button(action_frame, text="📦 Install ScalPDF", 
                      command=self.show_installation_options, style='Big.TButton').pack(side=tk.LEFT, padx=(0, 15))
            
        # Help button
        ttk.Button(action_frame, text="❓ Help", 
                  command=self.show_help).pack(side=tk.LEFT)
                  
    def create_advanced_section(self, parent, row):
        """Create advanced options section."""
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="10")
        advanced_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(advanced_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Installation tab
        install_tab = ttk.Frame(notebook)
        notebook.add(install_tab, text="Installation")
        
        install_buttons = ttk.Frame(install_tab)
        install_buttons.pack(pady=10)
        
        ttk.Button(install_buttons, text="Build AppImage", 
                  command=lambda: self.build_package('appimage')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(install_buttons, text="Build .deb Package", 
                  command=lambda: self.build_package('deb')).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(install_buttons, text="Build Snap Package", 
                  command=lambda: self.build_package('snap')).pack(side=tk.LEFT, padx=(0, 10))
        
        # Tools tab
        tools_tab = ttk.Frame(notebook)
        notebook.add(tools_tab, text="Tools")
        
        tools_buttons = ttk.Frame(tools_tab)
        tools_buttons.pack(pady=10)
        
        ttk.Button(tools_buttons, text="Run Tests", 
                  command=self.run_tests).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(tools_buttons, text="Package Installer", 
                  command=self.open_package_installer).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(tools_buttons, text="Open Project Folder", 
                  command=self.open_project_folder).pack(side=tk.LEFT)
        
        # About tab
        about_tab = ttk.Frame(notebook)
        notebook.add(about_tab, text="About")
        
        about_text = tk.Text(about_tab, height=4, wrap=tk.WORD, state=tk.DISABLED)
        about_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        about_content = """ScalPDF v1.0.0
Secure PDF Viewer and Editor

• AES-256-GCM encryption
• Offline operation (no internet required)
• PDF viewing, annotation, merging, splitting
• Cross-platform compatibility
• Open source (MIT License)

Visit: https://github.com/yashrajy264/scal-pdf"""
        
        about_text.configure(state=tk.NORMAL)
        about_text.insert(tk.END, about_content)
        about_text.configure(state=tk.DISABLED)
        
    def create_progress_section(self, parent, row):
        """Create progress section."""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.progress_status = ttk.Label(progress_frame, textvariable=self.current_operation)
        self.progress_status.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def create_footer_section(self, parent, row):
        """Create footer section."""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=row, column=0, sticky=(tk.W, tk.E))
        footer_frame.columnconfigure(1, weight=1)
        
        # Security notice
        security_text = "🛡️ ScalPDF operates completely offline. Your documents remain secure and private."
        ttk.Label(footer_frame, text=security_text, font=('Arial', 9)).grid(row=0, column=0, columnspan=2, pady=(10, 5))
        
        # Buttons
        ttk.Button(footer_frame, text="GitHub", 
                  command=lambda: webbrowser.open("https://github.com/yashrajy264/scal-pdf")).grid(row=1, column=0, sticky=tk.W)
        
        ttk.Button(footer_frame, text="Exit", 
                  command=self.root.quit).grid(row=1, column=1, sticky=tk.E)
                  
    def auto_detect_packages(self):
        """Auto-detect available packages."""
        self.update_status("Scanning for packages...")
        
        build_dir = self.project_root / "build"
        if build_dir.exists():
            packages = []
            packages.extend(build_dir.glob("**/*.AppImage"))
            packages.extend(build_dir.glob("**/*.deb"))
            packages.extend(build_dir.glob("**/*.snap"))
            
            if packages:
                self.update_status(f"Found {len(packages)} pre-built packages")
            else:
                self.update_status("No pre-built packages found")
        else:
            self.update_status("Ready - No build directory found")
            
    def update_status(self, message):
        """Update status message."""
        self.current_operation.set(message)
        self.root.update_idletasks()
        
    def update_progress(self, value):
        """Update progress bar."""
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def launch_scalpdf(self):
        """Launch ScalPDF application."""
        if self.scalpdf_running:
            messagebox.showinfo("Info", "ScalPDF is already running!")
            return
            
        self.update_status("Launching ScalPDF...")
        self.update_progress(50)
        
        def launch_thread():
            try:
                location = self.installation_status['location']
                install_type = self.installation_status['type']
                
                if install_type == 'snap':
                    cmd = ['scalpdf']
                elif install_type == 'system':
                    cmd = ['scalpdf']
                elif install_type == 'appimage':
                    cmd = [str(location)]
                else:
                    raise Exception("Unknown installation type")
                
                # Launch ScalPDF
                process = subprocess.Popen(cmd, start_new_session=True)
                
                self.scalpdf_running = True
                self.root.after(0, lambda: self.update_status("ScalPDF launched successfully!"))
                self.root.after(0, lambda: self.update_progress(100))
                
                # Update launch button
                self.root.after(0, lambda: self.launch_button.configure(text="🟢 ScalPDF Running"))
                
                # Wait a bit then reset
                time.sleep(3)
                self.root.after(0, lambda: self.update_status("Ready"))
                self.root.after(0, lambda: self.update_progress(0))
                self.root.after(0, lambda: self.launch_button.configure(text="🚀 Launch ScalPDF"))
                self.scalpdf_running = False
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Launch Error", f"Failed to launch ScalPDF:\n{e}"))
                self.root.after(0, lambda: self.update_status("Launch failed"))
                self.root.after(0, lambda: self.update_progress(0))
                self.scalpdf_running = False
        
        thread = threading.Thread(target=launch_thread)
        thread.daemon = True
        thread.start()
        
    def show_installation_options(self):
        """Show installation options dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Install ScalPDF")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Choose Installation Method", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Installation options
        options = [
            ("🚀 Smart Install (Recommended)", "Auto-detect best method", self.smart_install),
            ("📦 AppImage (Portable)", "No installation required, runs anywhere", lambda: self.install_method('appimage')),
            ("🔧 .deb Package (Ubuntu/Debian)", "Native system integration", lambda: self.install_method('deb')),
            ("📱 Snap Package (Universal)", "Sandboxed, secure installation", lambda: self.install_method('snap')),
            ("🎨 Package Installer GUI", "Advanced installation options", self.open_package_installer)
        ]
        
        for title, desc, command in options:
            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.X, pady=5)
            
            btn = ttk.Button(frame, text=title, command=lambda cmd=command: [dialog.destroy(), cmd()])
            btn.pack(side=tk.LEFT)
            
            ttk.Label(frame, text=desc, font=('Arial', 9)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Cancel button
        ttk.Button(main_frame, text="Cancel", command=dialog.destroy).pack(pady=(20, 0))
        
    def smart_install(self):
        """Smart installation - auto-detect best method."""
        self.update_status("Starting smart installation...")
        
        def install_thread():
            try:
                # Run smart launcher
                script_path = self.project_root / "Installers GUI" / "smart_launcher.py"
                
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, cwd=str(self.project_root))
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.installation_complete())
                else:
                    self.root.after(0, lambda: messagebox.showerror("Installation Error", 
                                                                   f"Smart installation failed:\n{result.stderr}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Installation failed: {e}"))
            
            self.root.after(0, lambda: self.update_status("Ready"))
            self.root.after(0, lambda: self.update_progress(0))
        
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
    def install_method(self, method):
        """Install using specific method."""
        self.update_status(f"Installing ScalPDF using {method}...")
        
        def install_thread():
            try:
                if method == 'appimage':
                    script_path = self.project_root / "Installers GUI" / "build_appimage.py"
                elif method == 'deb':
                    script_path = self.project_root / "Installers GUI" / "build_deb.py"
                elif method == 'snap':
                    script_path = self.project_root / "Installers GUI" / "build_snap.py"
                else:
                    raise Exception(f"Unknown method: {method}")
                
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, cwd=str(self.project_root))
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.installation_complete())
                else:
                    self.root.after(0, lambda: messagebox.showerror("Build Error", 
                                                                   f"Package build failed:\n{result.stderr}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Installation failed: {e}"))
            
            self.root.after(0, lambda: self.update_status("Ready"))
            self.root.after(0, lambda: self.update_progress(0))
        
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
    def build_package(self, package_type):
        """Build specific package type."""
        self.update_status(f"Building {package_type} package...")
        
        def build_thread():
            try:
                script_name = f"build_{package_type}.py"
                script_path = self.project_root / "Installers GUI" / script_name
                
                if not script_path.exists():
                    raise Exception(f"Builder script not found: {script_name}")
                
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, cwd=str(self.project_root))
                
                if result.returncode == 0:
                    self.root.after(0, lambda: messagebox.showinfo("Success", 
                                                                  f"{package_type} package built successfully!"))
                    self.root.after(0, self.auto_detect_packages)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Build Error", 
                                                                   f"Build failed:\n{result.stderr}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Build failed: {e}"))
            
            self.root.after(0, lambda: self.update_status("Ready"))
            self.root.after(0, lambda: self.update_progress(0))
        
        thread = threading.Thread(target=build_thread)
        thread.daemon = True
        thread.start()
        
    def run_tests(self):
        """Run test suite."""
        self.update_status("Running tests...")
        
        def test_thread():
            try:
                script_path = self.project_root / "Installers GUI" / "test_packages.py"
                
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, cwd=str(self.project_root))
                
                # Show results in a dialog
                self.root.after(0, lambda: self.show_test_results(result))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Test failed: {e}"))
            
            self.root.after(0, lambda: self.update_status("Ready"))
            self.root.after(0, lambda: self.update_progress(0))
        
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
        
    def show_test_results(self, result):
        """Show test results in a dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Test Results")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text
        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert results
        output = result.stdout if result.stdout else result.stderr
        text_widget.insert(tk.END, output)
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        
    def open_package_installer(self):
        """Open the package installer GUI."""
        try:
            script_path = self.project_root / "Installers GUI" / "package_installer.py"
            subprocess.Popen([sys.executable, str(script_path)], start_new_session=True)
            self.update_status("Package installer opened")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open package installer: {e}")
            
    def open_project_folder(self):
        """Open project folder in file manager."""
        try:
            if platform.system() == "Linux":
                subprocess.Popen(["xdg-open", str(self.project_root)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", str(self.project_root)])
            elif platform.system() == "Windows":
                subprocess.Popen(["explorer", str(self.project_root)])
            else:
                messagebox.showinfo("Info", f"Project folder: {self.project_root}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")
            
    def installation_complete(self):
        """Handle installation completion."""
        # Refresh installation status
        self.installation_status = self.check_installation_status()
        
        # Update GUI
        if self.installation_status['installed']:
            self.status_label.configure(text="✅ Installation completed!", style='Success.TLabel')
            messagebox.showinfo("Success", "ScalPDF has been installed successfully!\n\nYou can now launch it from the main window.")
        else:
            messagebox.showwarning("Warning", "Installation may not have completed successfully.\n\nPlease check the console output for details.")
        
        # Recreate GUI to reflect new status
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_gui()
        
    def show_help(self):
        """Show help dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("ScalPDF Help")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = tk.Text(frame, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_content = """ScalPDF Launcher Help

QUICK START:
1. Click "Launch ScalPDF" if already installed
2. Click "Install ScalPDF" to install for the first time
3. Choose your preferred installation method

INSTALLATION METHODS:

Smart Install (Recommended)
• Automatically detects the best installation method for your system
• Handles dependencies and system integration

AppImage (Portable)
• No installation required
• Works on any Linux distribution
• Perfect for testing or portable use

.deb Package (Ubuntu/Debian)
• Native system integration
• Automatic updates through package manager
• Desktop menu entries and file associations

Snap Package (Universal)
• Works on any Linux distribution with Snap support
• Sandboxed for enhanced security
• Automatic updates

FEATURES:
• PDF viewing with zoom, rotation, thumbnails
• Annotations (highlight, underline, notes)
• PDF editing (merge, split, reorder pages)
• Compression with quality presets
• AES-256-GCM encryption and decryption
• Command-line interface for automation
• Completely offline operation

SECURITY:
• No internet connection required
• No telemetry or data collection
• Your documents remain on your local system
• Military-grade encryption for sensitive documents

TROUBLESHOOTING:
• Use "Run Tests" to check system compatibility
• Check system requirements in the About tab
• Visit GitHub for support and documentation

For more help, visit:
https://github.com/yashrajy264/scal-pdf"""
        
        help_text.configure(state=tk.NORMAL)
        help_text.insert(tk.END, help_content)
        help_text.configure(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        
    def run(self):
        """Run the launcher."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main entry point."""
    # Ensure we're running with a GUI
    if not os.environ.get('DISPLAY') and platform.system() == 'Linux':
        print("Error: No display available. Please run in a graphical environment.")
        sys.exit(1)
    
    try:
        app = ScalPDFLauncher()
        app.run()
    except Exception as e:
        # Show error in a simple dialog if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("ScalPDF Launcher Error", f"Failed to start launcher:\n{e}")
        except:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
