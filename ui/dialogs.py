"""
ScalPDF Dialogs
Various dialog windows for the application
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox,
    QProgressBar, QFileDialog, QListWidget, QGroupBox,
    QFormLayout, QSlider, QMessageBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QThread, pyqtSignal
from PySide6.QtGui import QPixmap, QFont

from pathlib import Path
from typing import List, Optional, Dict, Any

from core.crypto import PDFCrypto
from core.compress import CompressionPreset


class EncryptionDialog(QDialog):
    """Dialog for PDF encryption/decryption."""
    
    def __init__(self, parent=None, mode="encrypt"):
        """Initialize encryption dialog."""
        super().__init__(parent)
        
        self.mode = mode  # "encrypt" or "decrypt"
        self.crypto = PDFCrypto()
        
        self.setWindowTitle(f"PDF {mode.title()}")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = f"{'Encrypt' if self.mode == 'encrypt' else 'Decrypt'} PDF"
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Password input
        password_group = QGroupBox("Password")
        password_layout = QFormLayout(password_group)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.textChanged.connect(self.on_password_changed)
        password_layout.addRow("Password:", self.password_edit)
        
        if self.mode == "encrypt":
            self.confirm_password_edit = QLineEdit()
            self.confirm_password_edit.setEchoMode(QLineEdit.Password)
            self.confirm_password_edit.textChanged.connect(self.on_password_changed)
            password_layout.addRow("Confirm:", self.confirm_password_edit)
            
            # Show password checkbox
            self.show_password_check = QCheckBox("Show password")
            self.show_password_check.toggled.connect(self.toggle_password_visibility)
            password_layout.addRow("", self.show_password_check)
            
            # Password strength indicator
            self.strength_label = QLabel("Password strength: Weak")
            self.strength_label.setStyleSheet("color: red;")
            password_layout.addRow("", self.strength_label)
            
            # Generate password button
            self.generate_btn = QPushButton("Generate Strong Password")
            self.generate_btn.clicked.connect(self.generate_password)
            password_layout.addRow("", self.generate_btn)
        
        layout.addWidget(password_group)
        
        if self.mode == "encrypt":
            # Security options
            security_group = QGroupBox("Security Options")
            security_layout = QFormLayout(security_group)
            
            self.prevent_copy_check = QCheckBox("Prevent copying text")
            security_layout.addRow("", self.prevent_copy_check)
            
            self.prevent_print_check = QCheckBox("Prevent printing")
            security_layout.addRow("", self.prevent_print_check)
            
            layout.addWidget(security_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        action_text = "Encrypt" if self.mode == "encrypt" else "Decrypt"
        self.action_btn = QPushButton(action_text)
        self.action_btn.clicked.connect(self.accept)
        self.action_btn.setEnabled(False)
        button_layout.addWidget(self.action_btn)
        
        layout.addLayout(button_layout)
    
    def on_password_changed(self):
        """Handle password change."""
        password = self.password_edit.text()
        
        if self.mode == "encrypt":
            confirm_password = self.confirm_password_edit.text()
            passwords_match = password == confirm_password
            
            # Check password strength
            if password:
                strength_score, strength_desc = self.crypto.check_password_strength(password)
                self.strength_label.setText(f"Password strength: {strength_desc}")
                
                if strength_score >= 80:
                    self.strength_label.setStyleSheet("color: green;")
                elif strength_score >= 60:
                    self.strength_label.setStyleSheet("color: orange;")
                else:
                    self.strength_label.setStyleSheet("color: red;")
            else:
                self.strength_label.setText("Password strength: Weak")
                self.strength_label.setStyleSheet("color: red;")
            
            # Enable button only if passwords match and are strong enough
            self.action_btn.setEnabled(
                len(password) >= 8 and passwords_match and strength_score >= 40
            )
        else:
            # For decryption, just need a password
            self.action_btn.setEnabled(len(password) > 0)
    
    def toggle_password_visibility(self, show: bool):
        """Toggle password visibility."""
        mode = QLineEdit.Normal if show else QLineEdit.Password
        self.password_edit.setEchoMode(mode)
        if hasattr(self, 'confirm_password_edit'):
            self.confirm_password_edit.setEchoMode(mode)
    
    def generate_password(self):
        """Generate a strong password."""
        password = self.crypto.generate_strong_password(16)
        self.password_edit.setText(password)
        if hasattr(self, 'confirm_password_edit'):
            self.confirm_password_edit.setText(password)
    
    def get_password(self) -> str:
        """Get the entered password."""
        return self.password_edit.text()
    
    def get_security_options(self) -> Dict[str, bool]:
        """Get security options (for encryption)."""
        if self.mode == "encrypt":
            return {
                'prevent_copy': self.prevent_copy_check.isChecked(),
                'prevent_print': self.prevent_print_check.isChecked()
            }
        return {}


class CompressionDialog(QDialog):
    """Dialog for PDF compression."""
    
    def __init__(self, parent=None, input_file: Optional[Path] = None):
        """Initialize compression dialog."""
        super().__init__(parent)
        
        self.input_file = input_file
        
        self.setWindowTitle("Compress PDF")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        
        if input_file:
            self.analyze_file()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("PDF Compression")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # File info
        if self.input_file:
            info_group = QGroupBox("File Information")
            info_layout = QFormLayout(info_group)
            
            self.file_name_label = QLabel(self.input_file.name)
            info_layout.addRow("File:", self.file_name_label)
            
            self.file_size_label = QLabel("Analyzing...")
            info_layout.addRow("Size:", self.file_size_label)
            
            self.pages_label = QLabel("Analyzing...")
            info_layout.addRow("Pages:", self.pages_label)
            
            self.images_label = QLabel("Analyzing...")
            info_layout.addRow("Images:", self.images_label)
            
            layout.addWidget(info_group)
        
        # Compression presets
        preset_group = QGroupBox("Compression Preset")
        preset_layout = QVBoxLayout(preset_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Maximum Quality", CompressionPreset.MAX_QUALITY)
        self.preset_combo.addItem("Balanced", CompressionPreset.BALANCED)
        self.preset_combo.addItem("Maximum Compression", CompressionPreset.MAX_COMPRESSION)
        self.preset_combo.setCurrentIndex(1)  # Balanced by default
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        
        # Preset description
        self.preset_description = QLabel()
        self.preset_description.setWordWrap(True)
        self.preset_description.setStyleSheet("color: #666; font-size: 11px; margin: 5px;")
        preset_layout.addWidget(self.preset_description)
        
        layout.addWidget(preset_group)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        # Image quality
        self.image_quality_slider = QSlider(Qt.Horizontal)
        self.image_quality_slider.setRange(50, 100)
        self.image_quality_slider.setValue(85)
        self.image_quality_slider.valueChanged.connect(self.update_quality_label)
        
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(self.image_quality_slider)
        self.quality_label = QLabel("85%")
        quality_layout.addWidget(self.quality_label)
        
        advanced_layout.addRow("Image Quality:", quality_layout)
        
        # Image DPI
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setRange(72, 600)
        self.dpi_spinbox.setValue(200)
        self.dpi_spinbox.setSuffix(" DPI")
        advanced_layout.addRow("Target DPI:", self.dpi_spinbox)
        
        # Options
        self.remove_unused_check = QCheckBox("Remove unused objects")
        self.remove_unused_check.setChecked(True)
        advanced_layout.addRow("", self.remove_unused_check)
        
        self.linearize_check = QCheckBox("Linearize PDF (fast web view)")
        self.linearize_check.setChecked(True)
        advanced_layout.addRow("", self.linearize_check)
        
        layout.addWidget(advanced_group)
        
        # Estimated compression
        self.estimation_label = QLabel("Estimated size reduction: Calculating...")
        self.estimation_label.setStyleSheet("font-weight: bold; color: #0078d4; margin: 10px;")
        layout.addWidget(self.estimation_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.compress_btn = QPushButton("Compress")
        self.compress_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.compress_btn)
        
        layout.addLayout(button_layout)
        
        # Update preset description
        self.on_preset_changed()
    
    def analyze_file(self):
        """Analyze the input file."""
        # TODO: Implement file analysis in a separate thread
        pass
    
    def on_preset_changed(self):
        """Handle preset change."""
        preset = self.preset_combo.currentData()
        
        descriptions = {
            CompressionPreset.MAX_QUALITY: "Minimal compression, preserves maximum quality. Best for archival or professional use.",
            CompressionPreset.BALANCED: "Good balance between file size and quality. Recommended for most use cases.",
            CompressionPreset.MAX_COMPRESSION: "Maximum compression, smaller file size. May reduce image quality."
        }
        
        self.preset_description.setText(descriptions.get(preset, ""))
        
        # Update advanced options based on preset
        if preset == CompressionPreset.MAX_QUALITY:
            self.image_quality_slider.setValue(95)
            self.dpi_spinbox.setValue(300)
        elif preset == CompressionPreset.BALANCED:
            self.image_quality_slider.setValue(85)
            self.dpi_spinbox.setValue(200)
        elif preset == CompressionPreset.MAX_COMPRESSION:
            self.image_quality_slider.setValue(70)
            self.dpi_spinbox.setValue(150)
    
    def update_quality_label(self, value: int):
        """Update quality label."""
        self.quality_label.setText(f"{value}%")
    
    def get_compression_settings(self) -> Dict[str, Any]:
        """Get compression settings."""
        return {
            'preset': self.preset_combo.currentData(),
            'image_quality': self.image_quality_slider.value(),
            'image_dpi': self.dpi_spinbox.value(),
            'remove_unused': self.remove_unused_check.isChecked(),
            'linearize': self.linearize_check.isChecked()
        }


class MergeDialog(QDialog):
    """Dialog for merging PDF files."""
    
    def __init__(self, parent=None):
        """Initialize merge dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Merge PDF Files")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Merge PDF Files")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # File list
        files_group = QGroupBox("Files to Merge")
        files_layout = QVBoxLayout(files_group)
        
        # File list controls
        list_controls = QHBoxLayout()
        
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self.add_files)
        list_controls.addWidget(self.add_files_btn)
        
        self.remove_file_btn = QPushButton("Remove")
        self.remove_file_btn.clicked.connect(self.remove_file)
        self.remove_file_btn.setEnabled(False)
        list_controls.addWidget(self.remove_file_btn)
        
        list_controls.addStretch()
        
        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.move_up)
        self.move_up_btn.setEnabled(False)
        list_controls.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("Move Down")
        self.move_down_btn.clicked.connect(self.move_down)
        self.move_down_btn.setEnabled(False)
        list_controls.addWidget(self.move_down_btn)
        
        files_layout.addLayout(list_controls)
        
        # File list
        self.files_list = QListWidget()
        self.files_list.itemSelectionChanged.connect(self.on_selection_changed)
        files_layout.addWidget(self.files_list)
        
        layout.addWidget(files_group)
        
        # Output options
        output_group = QGroupBox("Output")
        output_layout = QFormLayout(output_group)
        
        # Output file
        output_file_layout = QHBoxLayout()
        self.output_file_edit = QLineEdit()
        output_file_layout.addWidget(self.output_file_edit)
        
        self.browse_output_btn = QPushButton("Browse")
        self.browse_output_btn.clicked.connect(self.browse_output)
        output_file_layout.addWidget(self.browse_output_btn)
        
        output_layout.addRow("Output File:", output_file_layout)
        
        layout.addWidget(output_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.merge_btn = QPushButton("Merge")
        self.merge_btn.clicked.connect(self.accept)
        self.merge_btn.setEnabled(False)
        button_layout.addWidget(self.merge_btn)
        
        layout.addLayout(button_layout)
    
    def add_files(self):
        """Add PDF files to merge."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        
        for file_path in files:
            self.files_list.addItem(file_path)
        
        self.update_ui_state()
    
    def remove_file(self):
        """Remove selected file."""
        current_row = self.files_list.currentRow()
        if current_row >= 0:
            self.files_list.takeItem(current_row)
        
        self.update_ui_state()
    
    def move_up(self):
        """Move selected file up."""
        current_row = self.files_list.currentRow()
        if current_row > 0:
            item = self.files_list.takeItem(current_row)
            self.files_list.insertItem(current_row - 1, item)
            self.files_list.setCurrentRow(current_row - 1)
    
    def move_down(self):
        """Move selected file down."""
        current_row = self.files_list.currentRow()
        if current_row < self.files_list.count() - 1:
            item = self.files_list.takeItem(current_row)
            self.files_list.insertItem(current_row + 1, item)
            self.files_list.setCurrentRow(current_row + 1)
    
    def browse_output(self):
        """Browse for output file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.output_file_edit.setText(file_path)
        
        self.update_ui_state()
    
    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = self.files_list.currentRow() >= 0
        self.remove_file_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and self.files_list.currentRow() > 0)
        self.move_down_btn.setEnabled(has_selection and self.files_list.currentRow() < self.files_list.count() - 1)
    
    def update_ui_state(self):
        """Update UI state."""
        has_files = self.files_list.count() >= 2
        has_output = bool(self.output_file_edit.text().strip())
        
        self.merge_btn.setEnabled(has_files and has_output)
    
    def get_file_list(self) -> List[str]:
        """Get list of files to merge."""
        files = []
        for i in range(self.files_list.count()):
            files.append(self.files_list.item(i).text())
        return files
    
    def get_output_file(self) -> str:
        """Get output file path."""
        return self.output_file_edit.text().strip()


class SplitDialog(QDialog):
    """Dialog for splitting PDF files."""
    
    def __init__(self, parent=None, input_file: Optional[Path] = None):
        """Initialize split dialog."""
        super().__init__(parent)
        
        self.input_file = input_file
        
        self.setWindowTitle("Split PDF")
        self.setModal(True)
        self.resize(400, 350)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Split PDF")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # File info
        if self.input_file:
            info_label = QLabel(f"File: {self.input_file.name}")
            info_label.setStyleSheet("margin: 5px;")
            layout.addWidget(info_label)
        
        # Split options
        options_group = QGroupBox("Split Options")
        options_layout = QVBoxLayout(options_group)
        
        # Split by pages
        self.split_pages_radio = QRadioButton("Split every N pages")
        self.split_pages_radio.setChecked(True)
        options_layout.addWidget(self.split_pages_radio)
        
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("    Pages per file:"))
        self.pages_spinbox = QSpinBox()
        self.pages_spinbox.setRange(1, 1000)
        self.pages_spinbox.setValue(1)
        pages_layout.addWidget(self.pages_spinbox)
        pages_layout.addStretch()
        options_layout.addLayout(pages_layout)
        
        # Split by range
        self.split_range_radio = QRadioButton("Extract page range")
        options_layout.addWidget(self.split_range_radio)
        
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("    Page range:"))
        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText("e.g., 1-5, 10, 15-20")
        range_layout.addWidget(self.range_edit)
        options_layout.addLayout(range_layout)
        
        # Split each page
        self.split_each_radio = QRadioButton("Split into individual pages")
        options_layout.addWidget(self.split_each_radio)
        
        layout.addWidget(options_group)
        
        # Output directory
        output_group = QGroupBox("Output")
        output_layout = QFormLayout(output_group)
        
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        if self.input_file:
            self.output_dir_edit.setText(str(self.input_file.parent))
        output_dir_layout.addWidget(self.output_dir_edit)
        
        self.browse_dir_btn = QPushButton("Browse")
        self.browse_dir_btn.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.browse_dir_btn)
        
        output_layout.addRow("Output Directory:", output_dir_layout)
        
        layout.addWidget(output_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.split_btn = QPushButton("Split")
        self.split_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.split_btn)
        
        layout.addLayout(button_layout)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_edit.setText(dir_path)
    
    def get_split_settings(self) -> Dict[str, Any]:
        """Get split settings."""
        if self.split_pages_radio.isChecked():
            return {
                'method': 'pages',
                'value': self.pages_spinbox.value(),
                'output_dir': self.output_dir_edit.text()
            }
        elif self.split_range_radio.isChecked():
            return {
                'method': 'range',
                'value': self.range_edit.text(),
                'output_dir': self.output_dir_edit.text()
            }
        else:  # split_each_radio
            return {
                'method': 'each',
                'value': None,
                'output_dir': self.output_dir_edit.text()
            }


class PrivacyNoticeDialog(QDialog):
    """Dialog showing privacy notice."""
    
    def __init__(self, parent=None):
        """Initialize privacy notice dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Privacy Notice")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("ScalPDF Privacy Guarantee")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Privacy text
        privacy_text = """
<h3>🔒 Your Privacy is Our Priority</h3>

<p><strong>ScalPDF is completely offline and privacy-first:</strong></p>

<ul>
<li>✅ <strong>No Internet Connection:</strong> ScalPDF never connects to the internet</li>
<li>✅ <strong>No Telemetry:</strong> We don't collect any usage data or analytics</li>
<li>✅ <strong>No Cloud Storage:</strong> All files remain on your device</li>
<li>✅ <strong>No Account Required:</strong> No sign-ups, logins, or personal information</li>
<li>✅ <strong>Local Processing:</strong> All PDF operations happen on your computer</li>
<li>✅ <strong>Secure Encryption:</strong> AES-256-GCM with Argon2id key derivation</li>
</ul>

<h3>🛡️ What This Means for You</h3>

<p>Your documents are <strong>completely private</strong>. We cannot see, access, or collect your files in any way. ScalPDF works entirely offline, ensuring your sensitive documents never leave your device.</p>

<p>This is our commitment to you: <strong>Your data stays yours, always.</strong></p>

<h3>🔐 Security Features</h3>

<ul>
<li>Military-grade AES-256-GCM encryption</li>
<li>Secure password-based key derivation</li>
<li>Memory protection for sensitive data</li>
<li>No plaintext password storage</li>
</ul>
        """
        
        text_edit = QTextEdit()
        text_edit.setHtml(privacy_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Checkbox for "Don't show again"
        self.dont_show_check = QCheckBox("Don't show this notice again")
        layout.addWidget(self.dont_show_check)
        
        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("I Understand")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def dont_show_again(self) -> bool:
        """Check if user selected don't show again."""
        return self.dont_show_check.isChecked()


class AboutDialog(QDialog):
    """About dialog."""
    
    def __init__(self, parent=None):
        """Initialize about dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("About ScalPDF")
        self.setModal(True)
        self.resize(400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Logo/Icon (placeholder)
        logo_label = QLabel("📄")
        logo_label.setStyleSheet("font-size: 48px;")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # App name and version
        name_label = QLabel("ScalPDF")
        name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setStyleSheet("font-size: 14px; color: #666;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description = """
<p align="center"><strong>Secure, Cross-platform, Offline PDF Management</strong></p>

<p>ScalPDF is a privacy-first PDF management tool that works completely offline. 
Manage, edit, compress, and secure your PDF documents without compromising your privacy.</p>

<p><strong>Key Features:</strong></p>
<ul>
<li>View and annotate PDFs</li>
<li>Merge, split, and reorder pages</li>
<li>Compress PDFs with quality presets</li>
<li>AES-256-GCM encryption</li>
<li>Completely offline operation</li>
</ul>

<p align="center">Built with Python, PySide6, PyMuPDF, and pikepdf</p>
        """
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setOpenExternalLinks(True)
        layout.addWidget(desc_label)
        
        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
