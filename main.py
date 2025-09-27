#!/usr/bin/env python3
"""
ScalPDF - Secure, Cross-platform, Offline PDF Management Tool
Main GUI entry point
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow


def main():
    """Main entry point for ScalPDF GUI application."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("ScalPDF")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ScalPDF")
    
    # Set application icon if available
    icon_path = project_root / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Show first-run privacy notice
    window.show_privacy_notice()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
