#!/usr/bin/env python3
"""
ScalPDF GUI Installer Launcher
Smart launcher that detects platform and runs the best installer
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


class InstallerLauncher:
    """Smart installer launcher with platform detection."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Detect platform and available installers
        self.platform = self.detect_platform()
        self.available_installers = self.detect_installers()
        
        self.setup_ui()
        self.center_window()
    
    def detect_platform(self):
        """Detect current platform."""
        system = platform.system().lower()
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        else:
            return "unknown"
    
    def detect_installers(self):
        """Detect available installer scripts."""
        installer_dir = Path(__file__).parent
        installers = {}
        
        # Check for available installers
        installer_files = {
            "gui": installer_dir / "gui_installer.py",
            "windows": installer_dir / "windows_installer.py",
            "linux": installer_dir / "linux_installer.py"
        }
        
        for name, path in installer_files.items():
            if path.exists():
                installers[name] = path
        
        return installers
    
    def center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
    
    def setup_ui(self):
        """Setup user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        header_frame.columnconfigure(1, weight=1)
        
        # Logo
        logo_label = ttk.Label(header_frame, text="📄", font=("Arial", 48))
        logo_label.grid(row=0, column=0, padx=(0, 20), rowspan=2)
        
        # Title
        title_label = ttk.Label(header_frame, text="ScalPDF Installer", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=1, sticky=tk.W)
        
        subtitle_label = ttk.Label(header_frame, text="Choose your installation method", 
                                  font=("Arial", 11))
        subtitle_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Platform info
        platform_frame = ttk.LabelFrame(main_frame, text="System Information", padding="15")
        platform_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        platform_info = f"Platform: {self.get_platform_name()}"
        ttk.Label(platform_frame, text=platform_info, font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        
        python_version = f"Python: {sys.version.split()[0]}"
        ttk.Label(platform_frame, text=python_version, font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Installer options
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="15")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        options_frame.columnconfigure(0, weight=1)
        
        # Recommended installer
        recommended_installer = self.get_recommended_installer()
        if recommended_installer:
            rec_frame = ttk.Frame(options_frame)
            rec_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
            rec_frame.columnconfigure(1, weight=1)
            
            ttk.Label(rec_frame, text="🌟", font=("Arial", 16)).grid(row=0, column=0, padx=(0, 10))
            
            rec_info_frame = ttk.Frame(rec_frame)
            rec_info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
            rec_info_frame.columnconfigure(0, weight=1)
            
            ttk.Label(rec_info_frame, text="Recommended for your system:", 
                     font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
            
            rec_desc = self.get_installer_description(recommended_installer)
            ttk.Label(rec_info_frame, text=rec_desc, 
                     font=("Arial", 9), foreground="gray").grid(row=1, column=0, sticky=tk.W)
            
            self.recommended_btn = ttk.Button(rec_frame, text="Install (Recommended)", 
                                            command=lambda: self.run_installer(recommended_installer),
                                            style="Accent.TButton")
            self.recommended_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Other options
        other_frame = ttk.Frame(options_frame)
        other_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        other_frame.columnconfigure(1, weight=1)
        
        ttk.Label(other_frame, text="Other options:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        row = 1
        for installer_type, path in self.available_installers.items():
            if installer_type != recommended_installer:
                btn_frame = ttk.Frame(other_frame)
                btn_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=2)
                btn_frame.columnconfigure(1, weight=1)
                
                btn_text = self.get_installer_button_text(installer_type)
                btn = ttk.Button(btn_frame, text=btn_text, 
                               command=lambda t=installer_type: self.run_installer(t))
                btn.grid(row=0, column=0, sticky=tk.W)
                
                desc = self.get_installer_description(installer_type)
                ttk.Label(btn_frame, text=desc, font=("Arial", 8), 
                         foreground="gray").grid(row=0, column=1, sticky=tk.W, padx=(15, 0))
                
                row += 1
        
        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="About ScalPDF", padding="15")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        info_text = """ScalPDF is a secure, cross-platform PDF management tool that works completely offline.

Features:
• View and annotate PDFs with highlights and notes
• Merge, split, and reorder PDF pages  
• Compress PDFs with quality presets
• Encrypt/decrypt with AES-256-GCM encryption
• Command-line tools for batch operations
• Privacy-first design with no data collection"""
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                 font=("Arial", 9)).grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        help_btn = ttk.Button(button_frame, text="Help", command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        
        exit_btn = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        exit_btn.pack(side=tk.RIGHT)
        
        # Configure accent button style
        style = ttk.Style()
        try:
            style.configure("Accent.TButton", font=("Arial", 9, "bold"))
        except:
            pass
    
    def get_platform_name(self):
        """Get friendly platform name."""
        names = {
            "windows": "Microsoft Windows",
            "linux": "Linux",
            "macos": "macOS",
            "unknown": "Unknown"
        }
        return names.get(self.platform, "Unknown")
    
    def get_recommended_installer(self):
        """Get recommended installer for current platform."""
        if self.platform == "windows" and "windows" in self.available_installers:
            return "windows"
        elif self.platform == "linux" and "linux" in self.available_installers:
            return "linux"
        elif "gui" in self.available_installers:
            return "gui"
        else:
            return list(self.available_installers.keys())[0] if self.available_installers else None
    
    def get_installer_button_text(self, installer_type):
        """Get button text for installer type."""
        texts = {
            "gui": "Universal Installer",
            "windows": "Windows Installer",
            "linux": "Linux Installer"
        }
        return texts.get(installer_type, f"{installer_type.title()} Installer")
    
    def get_installer_description(self, installer_type):
        """Get description for installer type."""
        descriptions = {
            "gui": "Cross-platform installer with basic options",
            "windows": "Advanced Windows installer with native features",
            "linux": "Linux installer with distribution-specific support"
        }
        return descriptions.get(installer_type, "Platform-specific installer")
    
    def run_installer(self, installer_type):
        """Run the selected installer."""
        if installer_type not in self.available_installers:
            messagebox.showerror("Error", f"Installer '{installer_type}' not found!")
            return
        
        installer_path = self.available_installers[installer_type]
        
        try:
            # Hide launcher window
            self.root.withdraw()
            
            # Run installer
            if self.platform == "windows":
                # On Windows, use pythonw to avoid console window
                subprocess.run([sys.executable, str(installer_path)], check=True)
            else:
                subprocess.run([sys.executable, str(installer_path)], check=True)
            
            # Close launcher after installer completes
            self.root.quit()
            
        except subprocess.CalledProcessError as e:
            # Show launcher again if installer failed
            self.root.deiconify()
            messagebox.showerror("Installer Error", 
                               f"Installer failed with exit code {e.returncode}")
        except FileNotFoundError:
            self.root.deiconify()
            messagebox.showerror("Error", "Python interpreter not found!")
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Failed to run installer: {str(e)}")
    
    def show_help(self):
        """Show help dialog."""
        help_text = f"""ScalPDF Installer Help

Platform Detected: {self.get_platform_name()}
Available Installers: {len(self.available_installers)}

Installer Types:

• Universal Installer (gui_installer.py)
  - Works on all platforms
  - Simple, clean interface
  - Basic installation options
  - Good for most users

• Windows Installer (windows_installer.py)
  - Windows-specific features
  - Start Menu integration
  - File associations
  - Registry entries
  - Professional Windows look

• Linux Installer (linux_installer.py)
  - Distribution detection
  - Package manager integration
  - Desktop environment support
  - System dependency installation

System Requirements:
• Python 3.11 or higher
• tkinter (GUI toolkit)
• Internet connection (for dependencies)
• 150 MB free disk space

For support: https://github.com/yashrajy264/scal-pdf"""
        
        messagebox.showinfo("Help", help_text)
    
    def run(self):
        """Run the launcher."""
        # Check if any installers are available
        if not self.available_installers:
            messagebox.showerror("Error", 
                               "No installer scripts found!\n\n"
                               "Please make sure you have the installer files in the same directory.")
            return
        
        # Check Python version
        if sys.version_info < (3, 11):
            result = messagebox.askyesno("Python Version Warning",
                                       f"Python 3.11+ is recommended, but you have {sys.version.split()[0]}.\n\n"
                                       "Installation may fail. Continue anyway?")
            if not result:
                return
        
        self.root.mainloop()


def main():
    """Main function."""
    # Check if tkinter is available
    try:
        import tkinter
    except ImportError:
        print("Error: tkinter is not available.")
        print("Please install tkinter:")
        print("  Windows: tkinter should be included with Python")
        print("  Ubuntu/Debian: sudo apt install python3-tk")
        print("  Fedora: sudo dnf install tkinter")
        print("  Arch: sudo pacman -S tk")
        return 1
    
    # Create and run launcher
    launcher = InstallerLauncher()
    launcher.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
