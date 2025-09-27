#!/usr/bin/env python3
"""
ScalPDF GUI Installer
User-friendly graphical installer for normal consumers
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

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    print("Error: tkinter not available. Please install tkinter.")
    sys.exit(1)


class ScalPDFInstaller:
    """GUI installer for ScalPDF."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Installation state
        self.install_path = self.get_default_install_path()
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu = tk.BooleanVar(value=True)
        self.add_to_path = tk.BooleanVar(value=True)
        self.installing = False
        
        # Setup UI
        self.setup_ui()
        
        # Center window
        self.center_window()
    
    def get_default_install_path(self):
        """Get default installation path based on platform."""
        system = platform.system().lower()
        if system == "windows":
            return Path(os.environ.get("LOCALAPPDATA", "")) / "ScalPDF"
        elif system == "linux":
            return Path.home() / ".local" / "share" / "scalpdf"
        else:
            return Path.home() / "ScalPDF"
    
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"600x500+{x}+{y}")
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Logo/Icon (text-based)
        logo_label = ttk.Label(header_frame, text="📄", font=("Arial", 48))
        logo_label.grid(row=0, column=0, padx=(0, 20))
        
        # Title and description
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, text="ScalPDF Installer", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        desc_label = ttk.Label(title_frame, 
                              text="Secure, Cross-platform, Offline PDF Management Tool",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, sticky=tk.W)
        
        version_label = ttk.Label(title_frame, text="Version 1.0.0", 
                                 font=("Arial", 9), foreground="gray")
        version_label.grid(row=2, column=0, sticky=tk.W)
        
        # Installation options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        options_frame.columnconfigure(1, weight=1)
        
        # Install path
        ttk.Label(options_frame, text="Install Location:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(options_frame)
        path_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        self.path_var = tk.StringVar(value=str(self.install_path))
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_install_path)
        browse_btn.grid(row=0, column=1)
        
        # Checkboxes for options
        ttk.Checkbutton(options_frame, text="Create desktop shortcut", 
                       variable=self.create_desktop_shortcut).grid(row=1, column=0, columnspan=2, 
                                                                  sticky=tk.W, pady=2)
        
        system = platform.system().lower()
        if system == "windows":
            menu_text = "Add to Start Menu"
        else:
            menu_text = "Add to Application Menu"
        
        ttk.Checkbutton(options_frame, text=menu_text, 
                       variable=self.create_start_menu).grid(row=2, column=0, columnspan=2, 
                                                            sticky=tk.W, pady=2)
        
        ttk.Checkbutton(options_frame, text="Add to system PATH (for CLI access)", 
                       variable=self.add_to_path).grid(row=3, column=0, columnspan=2, 
                                                      sticky=tk.W, pady=2)
        
        # Features info
        features_frame = ttk.LabelFrame(main_frame, text="Features", padding="10")
        features_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        features_text = """• View and annotate PDFs with highlights, notes, and comments
• Merge, split, and reorder PDF pages
• Compress PDFs with quality presets
• Encrypt/decrypt PDFs with AES-256-GCM encryption
• Command-line tools for batch operations
• Completely offline - no internet connection required
• Privacy-first design with no data collection"""
        
        features_label = ttk.Label(features_frame, text=features_text, justify=tk.LEFT)
        features_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress frame (initially hidden)
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready to install...")
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log area (initially hidden)
        self.log_frame = ttk.LabelFrame(main_frame, text="Installation Log", padding="5")
        self.log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.rowconfigure(0, weight=1)
        
        self.log_text = ScrolledText(self.log_frame, height=8, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initially hide progress and log
        self.progress_frame.grid_remove()
        self.log_frame.grid_remove()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.install_btn = ttk.Button(button_frame, text="Install ScalPDF", 
                                     command=self.start_installation, style="Accent.TButton")
        self.install_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_installation)
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # Configure accent button style
        self.style.configure("Accent.TButton", foreground="white")
        try:
            self.style.configure("Accent.TButton", background="#0078d4")
        except:
            pass  # Some themes don't support background color
    
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
        main_frame.rowconfigure(4, weight=1)  # Make log frame expandable
        
        # Update UI state
        self.installing = True
        self.install_btn.config(text="Installing...", state=tk.DISABLED)
        self.cancel_btn.config(text="Close", state=tk.DISABLED)
        
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
            self.update_progress("Creating Python environment...")
            self.log_message("🐍 Creating Python virtual environment...")
            
            venv_path = install_path / "venv"
            self.create_virtual_environment(venv_path)
            
            # Install dependencies
            self.update_progress("Installing Python packages...")
            self.log_message("📦 Installing Python dependencies...")
            
            self.install_dependencies(venv_path, install_path)
            
            # Create shortcuts
            if self.create_desktop_shortcut.get():
                self.update_progress("Creating desktop shortcut...")
                self.log_message("🖥️ Creating desktop shortcut...")
                self.create_desktop_shortcut_file(install_path)
            
            if self.create_start_menu.get():
                self.update_progress("Creating menu entries...")
                self.log_message("📱 Creating application menu entries...")
                self.create_menu_entries(install_path)
            
            # Add to PATH
            if self.add_to_path.get():
                self.update_progress("Adding to system PATH...")
                self.log_message("🛤️ Adding to system PATH...")
                self.add_to_system_path(install_path)
            
            # Create uninstaller
            self.update_progress("Creating uninstaller...")
            self.log_message("🗑️ Creating uninstaller...")
            self.create_uninstaller(install_path)
            
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
            system = platform.system().lower()
            if system == "windows":
                python_exe = venv_path / "Scripts" / "python.exe"
                pip_exe = venv_path / "Scripts" / "pip.exe"
            else:
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
    
    def create_desktop_shortcut_file(self, install_path):
        """Create desktop shortcut."""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                self.create_windows_shortcut(install_path)
            else:
                self.create_linux_shortcut(install_path)
                
            self.log_message("✅ Desktop shortcut created")
        except Exception as e:
            self.log_message(f"⚠️ Desktop shortcut failed: {e}")
    
    def create_windows_shortcut(self, install_path):
        """Create Windows shortcut."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(Path(desktop) / "ScalPDF.lnk"))
            shortcut.Targetpath = str(install_path / "venv" / "Scripts" / "python.exe")
            shortcut.Arguments = str(install_path / "main.py")
            shortcut.WorkingDirectory = str(install_path)
            shortcut.IconLocation = str(install_path / "assets" / "icon.ico")
            shortcut.save()
        except ImportError:
            # Fallback: create batch file
            desktop = Path.home() / "Desktop"
            batch_file = desktop / "ScalPDF.bat"
            
            batch_content = f'''@echo off
cd /d "{install_path}"
call "venv\\Scripts\\activate.bat"
python main.py %*
'''
            batch_file.write_text(batch_content)
    
    def create_linux_shortcut(self, install_path):
        """Create Linux desktop shortcut."""
        desktop_dir = Path.home() / "Desktop"
        desktop_dir.mkdir(exist_ok=True)
        
        desktop_file = desktop_dir / "ScalPDF.desktop"
        
        desktop_content = f"""[Desktop Entry]
Type=Application
Name=ScalPDF
Comment=Secure PDF Management Tool
Exec={install_path}/venv/bin/python {install_path}/main.py
Icon={install_path}/assets/icon.png
Categories=Office;Graphics;
StartupNotify=true
StartupWMClass=ScalPDF
"""
        
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)
    
    def create_menu_entries(self, install_path):
        """Create application menu entries."""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                self.create_windows_menu_entries(install_path)
            else:
                self.create_linux_menu_entries(install_path)
                
            self.log_message("✅ Menu entries created")
        except Exception as e:
            self.log_message(f"⚠️ Menu entries failed: {e}")
    
    def create_windows_menu_entries(self, install_path):
        """Create Windows Start Menu entries."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            start_menu = winshell.start_menu()
            shell = Dispatch('WScript.Shell')
            
            # GUI shortcut
            shortcut = shell.CreateShortCut(str(Path(start_menu) / "ScalPDF.lnk"))
            shortcut.Targetpath = str(install_path / "venv" / "Scripts" / "python.exe")
            shortcut.Arguments = str(install_path / "main.py")
            shortcut.WorkingDirectory = str(install_path)
            shortcut.IconLocation = str(install_path / "assets" / "icon.ico")
            shortcut.save()
            
        except ImportError:
            self.log_message("⚠️ Start Menu creation requires pywin32")
    
    def create_linux_menu_entries(self, install_path):
        """Create Linux application menu entries."""
        apps_dir = Path.home() / ".local" / "share" / "applications"
        apps_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_file = apps_dir / "scalpdf.desktop"
        
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
    
    def add_to_system_path(self, install_path):
        """Add installation to system PATH."""
        try:
            # Create launcher scripts
            system = platform.system().lower()
            
            if system == "windows":
                # Create batch launchers in install directory
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
                
                # Add to user PATH
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        current_path, _ = winreg.QueryValueEx(key, "PATH")
                    except FileNotFoundError:
                        current_path = ""
                    
                    if str(install_path) not in current_path:
                        new_path = f"{current_path};{install_path}" if current_path else str(install_path)
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                
            else:
                # Create launcher scripts in ~/.local/bin
                bin_dir = Path.home() / ".local" / "bin"
                bin_dir.mkdir(parents=True, exist_ok=True)
                
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
            
            self.log_message("✅ Added to system PATH")
        except Exception as e:
            self.log_message(f"⚠️ PATH addition failed: {e}")
    
    def create_uninstaller(self, install_path):
        """Create uninstaller."""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                uninstaller = install_path / "Uninstall.bat"
                uninstaller_content = f'''@echo off
echo Uninstalling ScalPDF...
echo.

REM Remove installation directory
if exist "{install_path}" (
    rmdir /s /q "{install_path}"
    echo ✅ Application files removed
)

REM Remove shortcuts
del "%USERPROFILE%\\Desktop\\ScalPDF.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ScalPDF.lnk" 2>nul
echo ✅ Shortcuts removed

echo.
echo ScalPDF has been uninstalled.
pause
'''
            else:
                uninstaller = install_path / "uninstall.sh"
                uninstaller_content = f'''#!/bin/bash
echo "Uninstalling ScalPDF..."

# Remove installation directory
rm -rf "{install_path}"
echo "✅ Application files removed"

# Remove launchers
rm -f "$HOME/.local/bin/scalpdf"
rm -f "$HOME/.local/bin/scalpdf-cli"
echo "✅ Launchers removed"

# Remove desktop entries
rm -f "$HOME/.local/share/applications/scalpdf.desktop"
rm -f "$HOME/Desktop/ScalPDF.desktop"
echo "✅ Desktop entries removed"

echo "ScalPDF has been uninstalled."
'''
                uninstaller.chmod(0o755)
            
            uninstaller.write_text(uninstaller_content)
            self.log_message("✅ Uninstaller created")
        except Exception as e:
            self.log_message(f"⚠️ Uninstaller creation failed: {e}")
    
    def test_installation(self, install_path):
        """Test the installation."""
        try:
            system = platform.system().lower()
            if system == "windows":
                python_exe = install_path / "venv" / "Scripts" / "python.exe"
            else:
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
        
        if self.create_start_menu.get():
            system = platform.system().lower()
            if system == "windows":
                self.log_message("• Find ScalPDF in the Start Menu")
            else:
                self.log_message("• Find ScalPDF in your application menu")
        
        if self.add_to_path.get():
            self.log_message("• Run 'scalpdf' from command line (after restart)")
        
        self.install_btn.config(text="Installation Complete", state=tk.DISABLED)
        self.cancel_btn.config(text="Close", state=tk.NORMAL)
        
        # Show success message
        messagebox.showinfo(
            "Installation Complete",
            "ScalPDF has been installed successfully!\n\n"
            "You can now use ScalPDF to manage your PDF files securely."
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
    # Check if tkinter is available
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter is not available.")
        print("Please install tkinter:")
        print("  Ubuntu/Debian: sudo apt install python3-tk")
        print("  Fedora: sudo dnf install tkinter")
        print("  Windows: tkinter should be included with Python")
        return 1
    
    # Create and run installer
    installer = ScalPDFInstaller()
    installer.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
