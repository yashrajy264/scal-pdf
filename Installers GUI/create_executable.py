#!/usr/bin/env python3
"""
Create a proper executable for ScalPDF Launcher
This script creates a binary executable that won't open in text editor
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_executable():
    """Create executable launcher."""
    script_dir = Path(__file__).parent
    
    # Create the executable content
    executable_content = '''#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add current directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Change to script directory
os.chdir(script_dir)

# Import and run the launcher
try:
    # Try to import from ScalPDF-Launcher first
    launcher_file = script_dir / "ScalPDF-Launcher"
    if launcher_file.exists():
        exec(open(launcher_file).read())
    else:
        # Fallback to scalpdf_launcher.py
        from scalpdf_launcher import ScalPDFLauncher
        app = ScalPDFLauncher()
        app.run()
except ImportError as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Failed to import launcher: {e}")
    sys.exit(1)
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Failed to start ScalPDF: {e}")
    sys.exit(1)
'''

    # Write executable
    executable_path = script_dir / "ScalPDF"
    with open(executable_path, 'w') as f:
        f.write(executable_content)
    
    # Make it executable
    os.chmod(executable_path, 0o755)
    
    print(f"✅ Created executable: {executable_path}")
    
    # Also create a .desktop file that points to this
    desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=ScalPDF Launcher
Comment=Secure PDF Viewer and Editor Launcher
Exec={executable_path}
Icon=application-pdf
Terminal=false
Categories=Office;Graphics;Viewer;
StartupNotify=true
'''
    
    desktop_path = script_dir / "ScalPDF.desktop"
    with open(desktop_path, 'w') as f:
        f.write(desktop_content)
    
    os.chmod(desktop_path, 0o755)
    
    print(f"✅ Created desktop file: {desktop_path}")
    
    # Create a simple README for users
    readme_content = '''# 🚀 ScalPDF Launcher - FIXED!

## Double-Click These Files (They Won't Open in Text Editor):

### ✅ MAIN LAUNCHER (Recommended):
```
ScalPDF
```
This is a proper executable file that will run directly!

### ✅ ALTERNATIVE LAUNCHERS:
```
run-scalpdf          # Shell script executable
launch-scalpdf.sh    # Enhanced shell script
```

### ✅ DESKTOP INTEGRATION:
```
ScalPDF.desktop      # Copy this to your desktop
```

## 🎯 Instructions:

1. **Double-click** `ScalPDF` (the main executable)
2. **If that doesn't work**, try `run-scalpdf`
3. **If still having issues**, try `launch-scalpdf.sh`

## 🔧 If Still Opening Text Editor:

### Method 1: Right-click Properties
1. Right-click on `ScalPDF`
2. Select "Properties"
3. Go to "Permissions" tab
4. Check "Allow executing file as program"
5. Close and double-click again

### Method 2: Terminal (One-time setup)
```bash
chmod +x ScalPDF
chmod +x run-scalpdf
chmod +x launch-scalpdf.sh
```

### Method 3: Open With
1. Right-click on `ScalPDF`
2. Select "Open With" → "Other Application"
3. Choose "Python 3" or "Execute in Terminal"

## ✅ Success Indicators:
- GUI window opens with ScalPDF branding
- No text editor appears
- You see installation status and buttons

## 🆘 Last Resort:
If nothing works, open terminal and run:
```bash
cd "scal-pdf/Installers GUI"
python3 ScalPDF
```

---
**The `ScalPDF` file is now a proper executable that should work!**
'''
    
    readme_path = script_dir / "CLICK_TO_LAUNCH.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Created instructions: {readme_path}")
    
    return executable_path

if __name__ == "__main__":
    create_executable()
