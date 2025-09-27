"""
ScalPDF Main Window
Main GUI window with toolbar, panels, and PDF viewer
"""

import sys
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QStatusBar, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QTabWidget, QLabel, QProgressBar, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, pyqtSignal
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPixmap

# Import core modules
from core.viewer import PDFViewer
from core.crypto import PDFCrypto
from core.compress import PDFCompressor, CompressionPreset
from core.editor import PDFEditor
from core.annotations import PDFAnnotations

# Import UI components
from ui.pdf_viewer_widget import PDFViewerWidget
from ui.thumbnails_panel import ThumbnailsPanel
from ui.annotations_panel import AnnotationsPanel
from ui.dialogs import (
    EncryptionDialog, CompressionDialog, MergeDialog, SplitDialog,
    PrivacyNoticeDialog, AboutDialog
)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize core components
        self.pdf_viewer = PDFViewer()
        self.pdf_crypto = PDFCrypto()
        self.pdf_compressor = PDFCompressor()
        self.pdf_editor = PDFEditor()
        self.pdf_annotations = PDFAnnotations()
        
        # UI state
        self.current_file: Optional[Path] = None
        self.recent_files: List[Path] = []
        self.is_dark_theme = False
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        
        # Load settings
        self.load_settings()
        
        # Set window properties
        self.setWindowTitle("ScalPDF - Secure PDF Management")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for panels
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create left panel (thumbnails)
        self.thumbnails_panel = ThumbnailsPanel()
        self.thumbnails_panel.setMaximumWidth(250)
        self.main_splitter.addWidget(self.thumbnails_panel)
        
        # Create center area (tabbed PDF viewers)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.main_splitter.addWidget(self.tab_widget)
        
        # Create right panel (annotations)
        self.annotations_panel = AnnotationsPanel()
        self.annotations_panel.setMaximumWidth(300)
        self.main_splitter.addWidget(self.annotations_panel)
        
        # Set splitter proportions
        self.main_splitter.setSizes([200, 800, 250])
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
    
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # File operations
        self.action_open = QAction("Open", self)
        self.action_open.setShortcut(QKeySequence.Open)
        self.action_open.triggered.connect(self.open_file)
        toolbar.addAction(self.action_open)
        
        self.action_save = QAction("Save", self)
        self.action_save.setShortcut(QKeySequence.Save)
        self.action_save.triggered.connect(self.save_file)
        self.action_save.setEnabled(False)
        toolbar.addAction(self.action_save)
        
        self.action_save_as = QAction("Save As", self)
        self.action_save_as.setShortcut(QKeySequence.SaveAs)
        self.action_save_as.triggered.connect(self.save_file_as)
        self.action_save_as.setEnabled(False)
        toolbar.addAction(self.action_save_as)
        
        toolbar.addSeparator()
        
        # PDF operations
        self.action_merge = QAction("Merge", self)
        self.action_merge.triggered.connect(self.merge_pdfs)
        toolbar.addAction(self.action_merge)
        
        self.action_split = QAction("Split", self)
        self.action_split.triggered.connect(self.split_pdf)
        self.action_split.setEnabled(False)
        toolbar.addAction(self.action_split)
        
        self.action_compress = QAction("Compress", self)
        self.action_compress.triggered.connect(self.compress_pdf)
        self.action_compress.setEnabled(False)
        toolbar.addAction(self.action_compress)
        
        toolbar.addSeparator()
        
        # Security operations
        self.action_encrypt = QAction("Encrypt", self)
        self.action_encrypt.triggered.connect(self.encrypt_pdf)
        self.action_encrypt.setEnabled(False)
        toolbar.addAction(self.action_encrypt)
        
        self.action_decrypt = QAction("Decrypt", self)
        self.action_decrypt.triggered.connect(self.decrypt_pdf)
        toolbar.addAction(self.action_decrypt)
        
        toolbar.addSeparator()
        
        # View operations
        self.action_zoom_in = QAction("Zoom In", self)
        self.action_zoom_in.setShortcut(QKeySequence.ZoomIn)
        self.action_zoom_in.triggered.connect(self.zoom_in)
        self.action_zoom_in.setEnabled(False)
        toolbar.addAction(self.action_zoom_in)
        
        self.action_zoom_out = QAction("Zoom Out", self)
        self.action_zoom_out.setShortcut(QKeySequence.ZoomOut)
        self.action_zoom_out.triggered.connect(self.zoom_out)
        self.action_zoom_out.setEnabled(False)
        toolbar.addAction(self.action_zoom_out)
        
        self.action_fit_width = QAction("Fit Width", self)
        self.action_fit_width.triggered.connect(self.fit_width)
        self.action_fit_width.setEnabled(False)
        toolbar.addAction(self.action_fit_width)
        
        self.action_fit_page = QAction("Fit Page", self)
        self.action_fit_page.triggered.connect(self.fit_page)
        self.action_fit_page.setEnabled(False)
        toolbar.addAction(self.action_fit_page)
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.action_open)
        file_menu.addSeparator()
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        # Exit action
        action_exit = QAction("Exit", self)
        action_exit.setShortcut(QKeySequence.Quit)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction(self.action_merge)
        edit_menu.addAction(self.action_split)
        edit_menu.addAction(self.action_compress)
        
        # Security menu
        security_menu = menubar.addMenu("Security")
        security_menu.addAction(self.action_encrypt)
        security_menu.addAction(self.action_decrypt)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.action_zoom_in)
        view_menu.addAction(self.action_zoom_out)
        view_menu.addAction(self.action_fit_width)
        view_menu.addAction(self.action_fit_page)
        view_menu.addSeparator()
        
        # Theme toggle
        action_toggle_theme = QAction("Toggle Dark/Light Theme", self)
        action_toggle_theme.triggered.connect(self.toggle_theme)
        view_menu.addAction(action_toggle_theme)
        
        # Panels submenu
        panels_menu = view_menu.addMenu("Panels")
        
        action_toggle_thumbnails = QAction("Show/Hide Thumbnails", self)
        action_toggle_thumbnails.triggered.connect(self.toggle_thumbnails_panel)
        panels_menu.addAction(action_toggle_thumbnails)
        
        action_toggle_annotations = QAction("Show/Hide Annotations", self)
        action_toggle_annotations.triggered.connect(self.toggle_annotations_panel)
        panels_menu.addAction(action_toggle_annotations)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        action_privacy = QAction("Privacy Notice", self)
        action_privacy.triggered.connect(self.show_privacy_notice)
        help_menu.addAction(action_privacy)
        
        action_about = QAction("About ScalPDF", self)
        action_about.triggered.connect(self.show_about)
        help_menu.addAction(action_about)
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        self.status_bar.addPermanentWidget(QLabel("|"))
        
        self.page_label = QLabel("No document")
        self.status_bar.addPermanentWidget(self.page_label)
        
        self.status_bar.addPermanentWidget(QLabel("|"))
        
        self.zoom_label = QLabel("100%")
        self.status_bar.addPermanentWidget(self.zoom_label)
        
        self.status_bar.addPermanentWidget(QLabel("|"))
        
        self.security_label = QLabel("🔓 Unencrypted")
        self.status_bar.addPermanentWidget(self.security_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_connections(self):
        """Setup signal connections."""
        # PDF viewer signals
        self.pdf_viewer.document_loaded.connect(self.on_document_loaded)
        self.pdf_viewer.page_changed.connect(self.on_page_changed)
        self.pdf_viewer.zoom_changed.connect(self.on_zoom_changed)
        self.pdf_viewer.error_occurred.connect(self.show_error)
        
        # Tab widget signals
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Thumbnails panel signals
        self.thumbnails_panel.page_selected.connect(self.goto_page)
        
        # Annotations panel signals
        self.annotations_panel.annotation_added.connect(self.on_annotation_added)
        self.annotations_panel.annotation_deleted.connect(self.on_annotation_deleted)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Additional shortcuts not in toolbar
        pass
    
    def load_settings(self):
        """Load application settings."""
        # TODO: Implement settings loading
        pass
    
    def save_settings(self):
        """Save application settings."""
        # TODO: Implement settings saving
        pass
    
    def open_file(self):
        """Open a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF File",
            "",
            "PDF Files (*.pdf);;Encrypted PDF Files (*.scalpdf);;All Files (*)"
        )
        
        if file_path:
            self.load_document(Path(file_path))
    
    def load_document(self, file_path: Path):
        """Load a document into the viewer."""
        try:
            # Check if file is encrypted by ScalPDF
            if self.pdf_crypto.is_encrypted_file(file_path):
                # Handle encrypted file
                self.decrypt_and_load(file_path)
                return
            
            # Create new tab for the document
            viewer_widget = PDFViewerWidget(self.pdf_viewer)
            
            # Load document
            if self.pdf_viewer.open_document(file_path):
                # Add tab
                tab_name = file_path.name
                tab_index = self.tab_widget.addTab(viewer_widget, tab_name)
                self.tab_widget.setCurrentIndex(tab_index)
                
                # Update UI state
                self.current_file = file_path
                self.add_to_recent_files(file_path)
                self.update_ui_state()
                
                # Load thumbnails
                self.load_thumbnails()
                
                self.status_label.setText(f"Loaded: {file_path.name}")
            
        except Exception as e:
            self.show_error(f"Failed to open file: {str(e)}")
    
    def decrypt_and_load(self, file_path: Path):
        """Decrypt and load an encrypted PDF."""
        dialog = EncryptionDialog(self, mode="decrypt")
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            
            try:
                # Create temporary file for decrypted content
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_path = Path(temp_file.name)
                
                # Decrypt file
                self.pdf_crypto.decrypt_file(file_path, temp_path, password)
                
                # Load decrypted file
                self.load_document(temp_path)
                
                # Mark as encrypted in UI
                self.security_label.setText("🔒 Encrypted")
                
            except Exception as e:
                self.show_error(f"Decryption failed: {str(e)}")
    
    def save_file(self):
        """Save the current document."""
        if self.current_file and self.pdf_viewer.document:
            try:
                self.pdf_viewer.document.save(str(self.current_file))
                self.status_label.setText(f"Saved: {self.current_file.name}")
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def save_file_as(self):
        """Save the current document with a new name."""
        if not self.pdf_viewer.document:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                self.pdf_viewer.document.save(file_path)
                self.current_file = Path(file_path)
                self.status_label.setText(f"Saved as: {self.current_file.name}")
                
                # Update tab title
                current_tab = self.tab_widget.currentIndex()
                if current_tab >= 0:
                    self.tab_widget.setTabText(current_tab, self.current_file.name)
                
            except Exception as e:
                self.show_error(f"Failed to save file: {str(e)}")
    
    def merge_pdfs(self):
        """Open merge dialog."""
        dialog = MergeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # TODO: Implement merge operation
            pass
    
    def split_pdf(self):
        """Open split dialog."""
        if not self.current_file:
            return
        
        dialog = SplitDialog(self, self.current_file)
        if dialog.exec() == QDialog.Accepted:
            # TODO: Implement split operation
            pass
    
    def compress_pdf(self):
        """Open compression dialog."""
        if not self.current_file:
            return
        
        dialog = CompressionDialog(self, self.current_file)
        if dialog.exec() == QDialog.Accepted:
            # TODO: Implement compression operation
            pass
    
    def encrypt_pdf(self):
        """Encrypt the current PDF."""
        if not self.current_file:
            return
        
        dialog = EncryptionDialog(self, mode="encrypt")
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            
            # Get output file path
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Encrypted PDF",
                str(self.current_file.with_suffix('.scalpdf')),
                "Encrypted PDF Files (*.scalpdf);;All Files (*)"
            )
            
            if output_path:
                try:
                    self.pdf_crypto.encrypt_file(self.current_file, Path(output_path), password)
                    self.status_label.setText(f"Encrypted and saved: {Path(output_path).name}")
                except Exception as e:
                    self.show_error(f"Encryption failed: {str(e)}")
    
    def decrypt_pdf(self):
        """Decrypt a PDF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Encrypted PDF",
            "",
            "Encrypted PDF Files (*.scalpdf);;All Files (*)"
        )
        
        if file_path:
            self.decrypt_and_load(Path(file_path))
    
    def zoom_in(self):
        """Zoom in the current document."""
        if self.pdf_viewer.document:
            self.pdf_viewer.zoom_in()
    
    def zoom_out(self):
        """Zoom out the current document."""
        if self.pdf_viewer.document:
            self.pdf_viewer.zoom_out()
    
    def fit_width(self):
        """Fit document to width."""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, PDFViewerWidget):
            width = current_widget.width()
            self.pdf_viewer.zoom_fit_width(width)
    
    def fit_page(self):
        """Fit entire page."""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, PDFViewerWidget):
            width = current_widget.width()
            height = current_widget.height()
            self.pdf_viewer.zoom_fit_page(width, height)
    
    def goto_page(self, page_num: int):
        """Go to specific page."""
        self.pdf_viewer.set_page(page_num)
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.is_dark_theme = not self.is_dark_theme
        # TODO: Implement theme switching
        self.status_label.setText(f"Switched to {'dark' if self.is_dark_theme else 'light'} theme")
    
    def toggle_thumbnails_panel(self):
        """Toggle thumbnails panel visibility."""
        self.thumbnails_panel.setVisible(not self.thumbnails_panel.isVisible())
    
    def toggle_annotations_panel(self):
        """Toggle annotations panel visibility."""
        self.annotations_panel.setVisible(not self.annotations_panel.isVisible())
    
    def show_privacy_notice(self):
        """Show privacy notice dialog."""
        dialog = PrivacyNoticeDialog(self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_error(self, message: str):
        """Show error message."""
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText(f"Error: {message}")
    
    def show_info(self, message: str):
        """Show info message."""
        QMessageBox.information(self, "Information", message)
        self.status_label.setText(message)
    
    def on_document_loaded(self, filename: str):
        """Handle document loaded signal."""
        self.update_ui_state()
        self.load_thumbnails()
    
    def on_page_changed(self, page_num: int):
        """Handle page changed signal."""
        if self.pdf_viewer.document:
            total_pages = self.pdf_viewer.get_page_count()
            self.page_label.setText(f"Page {page_num + 1} of {total_pages}")
            
            # Update thumbnails selection
            self.thumbnails_panel.select_page(page_num)
    
    def on_zoom_changed(self, zoom_level: float):
        """Handle zoom changed signal."""
        self.zoom_label.setText(f"{int(zoom_level * 100)}%")
    
    def on_tab_changed(self, index: int):
        """Handle tab changed signal."""
        # TODO: Switch to different document
        pass
    
    def close_tab(self, index: int):
        """Close a tab."""
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        
        if widget:
            widget.deleteLater()
        
        # Update UI state if no tabs left
        if self.tab_widget.count() == 0:
            self.current_file = None
            self.pdf_viewer.close_document()
            self.update_ui_state()
    
    def on_annotation_added(self, annotation_data: dict):
        """Handle annotation added signal."""
        # TODO: Add annotation to document
        pass
    
    def on_annotation_deleted(self, annotation_id: str):
        """Handle annotation deleted signal."""
        # TODO: Remove annotation from document
        pass
    
    def load_thumbnails(self):
        """Load thumbnails for current document."""
        if self.pdf_viewer.document:
            thumbnails = self.pdf_viewer.get_page_thumbnails()
            self.thumbnails_panel.set_thumbnails(thumbnails)
    
    def update_ui_state(self):
        """Update UI state based on current document."""
        has_document = self.pdf_viewer.document is not None
        
        # Enable/disable actions
        self.action_save.setEnabled(has_document)
        self.action_save_as.setEnabled(has_document)
        self.action_split.setEnabled(has_document)
        self.action_compress.setEnabled(has_document)
        self.action_encrypt.setEnabled(has_document)
        self.action_zoom_in.setEnabled(has_document)
        self.action_zoom_out.setEnabled(has_document)
        self.action_fit_width.setEnabled(has_document)
        self.action_fit_page.setEnabled(has_document)
        
        # Update status
        if has_document:
            page_count = self.pdf_viewer.get_page_count()
            current_page = self.pdf_viewer.get_current_page()
            self.page_label.setText(f"Page {current_page + 1} of {page_count}")
            
            # Check if document is encrypted
            doc_info = self.pdf_viewer.get_document_info()
            if doc_info.get('encrypted', False):
                self.security_label.setText("🔒 Encrypted")
            else:
                self.security_label.setText("🔓 Unencrypted")
        else:
            self.page_label.setText("No document")
            self.security_label.setText("🔓 Unencrypted")
    
    def add_to_recent_files(self, file_path: Path):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # Keep only last 10 files
        self.recent_files = self.recent_files[:10]
        
        self.update_recent_menu()
    
    def update_recent_menu(self):
        """Update recent files menu."""
        self.recent_menu.clear()
        
        for file_path in self.recent_files:
            if file_path.exists():
                action = QAction(file_path.name, self)
                action.setData(str(file_path))
                action.triggered.connect(lambda checked, path=file_path: self.load_document(path))
                self.recent_menu.addAction(action)
        
        if not self.recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings
        self.save_settings()
        
        # Close all documents
        self.pdf_viewer.close_document()
        
        event.accept()
