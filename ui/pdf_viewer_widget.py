"""
ScalPDF PDF Viewer Widget
Widget for displaying PDF pages with zoom and navigation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QSlider, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QPainter, QWheelEvent, QMouseEvent

from core.viewer import PDFViewer


class PDFPageWidget(QLabel):
    """Widget for displaying a single PDF page."""
    
    # Signals
    page_clicked = Signal(int, int)  # x, y coordinates
    
    def __init__(self):
        """Initialize the page widget."""
        super().__init__()
        
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.setMinimumSize(200, 300)
        
        # Mouse tracking for annotations
        self.setMouseTracking(True)
        self.mouse_pressed = False
        self.selection_start = None
        self.selection_end = None
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.selection_start = event.pos()
            self.page_clicked.emit(event.x(), event.y())
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if self.mouse_pressed and self.selection_start:
            self.selection_end = event.pos()
            self.update()  # Trigger repaint for selection rectangle
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            # TODO: Handle text selection for annotations
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """Custom paint event to draw selection rectangle."""
        super().paintEvent(event)
        
        if self.selection_start and self.selection_end and self.mouse_pressed:
            painter = QPainter(self)
            painter.setPen(Qt.blue)
            painter.setBrush(Qt.NoBrush)
            
            # Draw selection rectangle
            rect = self.get_selection_rect()
            painter.drawRect(rect)
    
    def get_selection_rect(self):
        """Get the current selection rectangle."""
        if not (self.selection_start and self.selection_end):
            return None
        
        x1, y1 = self.selection_start.x(), self.selection_start.y()
        x2, y2 = self.selection_end.x(), self.selection_end.y()
        
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return (left, top, width, height)


class PDFViewerWidget(QWidget):
    """Main PDF viewer widget with navigation controls."""
    
    # Signals
    page_changed = Signal(int)
    zoom_changed = Signal(float)
    
    def __init__(self, pdf_viewer: PDFViewer):
        """Initialize the viewer widget."""
        super().__init__()
        
        self.pdf_viewer = pdf_viewer
        self.current_pixmap = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create navigation toolbar
        nav_layout = QHBoxLayout()
        
        # Page navigation
        self.btn_first = QPushButton("⏮")
        self.btn_first.setToolTip("First Page")
        self.btn_first.setMaximumWidth(40)
        nav_layout.addWidget(self.btn_first)
        
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setToolTip("Previous Page")
        self.btn_prev.setMaximumWidth(40)
        nav_layout.addWidget(self.btn_prev)
        
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximumWidth(80)
        nav_layout.addWidget(self.page_spinbox)
        
        self.page_total_label = QLabel("of 0")
        nav_layout.addWidget(self.page_total_label)
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setToolTip("Next Page")
        self.btn_next.setMaximumWidth(40)
        nav_layout.addWidget(self.btn_next)
        
        self.btn_last = QPushButton("⏭")
        self.btn_last.setToolTip("Last Page")
        self.btn_last.setMaximumWidth(40)
        nav_layout.addWidget(self.btn_last)
        
        nav_layout.addStretch()
        
        # Zoom controls
        nav_layout.addWidget(QLabel("Zoom:"))
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems([
            "25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%",
            "Fit Width", "Fit Page"
        ])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setMaximumWidth(100)
        nav_layout.addWidget(self.zoom_combo)
        
        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_out.setToolTip("Zoom Out")
        self.btn_zoom_out.setMaximumWidth(30)
        nav_layout.addWidget(self.btn_zoom_out)
        
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setToolTip("Zoom In")
        self.btn_zoom_in.setMaximumWidth(30)
        nav_layout.addWidget(self.btn_zoom_in)
        
        # Rotation controls
        nav_layout.addStretch()
        
        self.btn_rotate_left = QPushButton("↺")
        self.btn_rotate_left.setToolTip("Rotate Left")
        self.btn_rotate_left.setMaximumWidth(40)
        nav_layout.addWidget(self.btn_rotate_left)
        
        self.btn_rotate_right = QPushButton("↻")
        self.btn_rotate_right.setToolTip("Rotate Right")
        self.btn_rotate_right.setMaximumWidth(40)
        nav_layout.addWidget(self.btn_rotate_right)
        
        layout.addLayout(nav_layout)
        
        # Create scroll area for PDF page
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Create page widget
        self.page_widget = PDFPageWidget()
        self.scroll_area.setWidget(self.page_widget)
        
        layout.addWidget(self.scroll_area)
        
        # Initially disable controls
        self.set_controls_enabled(False)
    
    def setup_connections(self):
        """Setup signal connections."""
        # Navigation buttons
        self.btn_first.clicked.connect(self.go_to_first_page)
        self.btn_prev.clicked.connect(self.go_to_previous_page)
        self.btn_next.clicked.connect(self.go_to_next_page)
        self.btn_last.clicked.connect(self.go_to_last_page)
        
        # Page spinbox
        self.page_spinbox.valueChanged.connect(self.on_page_spinbox_changed)
        
        # Zoom controls
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_combo_changed)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        
        # Rotation controls
        self.btn_rotate_left.clicked.connect(self.rotate_left)
        self.btn_rotate_right.clicked.connect(self.rotate_right)
        
        # PDF viewer signals
        self.pdf_viewer.document_loaded.connect(self.on_document_loaded)
        self.pdf_viewer.page_changed.connect(self.on_page_changed)
        self.pdf_viewer.zoom_changed.connect(self.on_zoom_changed)
        
        # Page widget signals
        self.page_widget.page_clicked.connect(self.on_page_clicked)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom with Ctrl+Wheel
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scrolling
            super().wheelEvent(event)
    
    def go_to_first_page(self):
        """Go to first page."""
        self.pdf_viewer.set_page(0)
    
    def go_to_previous_page(self):
        """Go to previous page."""
        self.pdf_viewer.previous_page()
    
    def go_to_next_page(self):
        """Go to next page."""
        self.pdf_viewer.next_page()
    
    def go_to_last_page(self):
        """Go to last page."""
        if self.pdf_viewer.document:
            last_page = self.pdf_viewer.get_page_count() - 1
            self.pdf_viewer.set_page(last_page)
    
    def on_page_spinbox_changed(self, value: int):
        """Handle page spinbox value change."""
        # Convert to 0-based index
        page_index = value - 1
        if page_index != self.pdf_viewer.get_current_page():
            self.pdf_viewer.set_page(page_index)
    
    def on_zoom_combo_changed(self, text: str):
        """Handle zoom combo selection."""
        if text == "Fit Width":
            self.fit_width()
        elif text == "Fit Page":
            self.fit_page()
        elif text.endswith("%"):
            try:
                zoom_percent = int(text[:-1])
                zoom_level = zoom_percent / 100.0
                self.pdf_viewer.set_zoom(zoom_level)
            except ValueError:
                pass
    
    def zoom_in(self):
        """Zoom in."""
        self.pdf_viewer.zoom_in()
    
    def zoom_out(self):
        """Zoom out."""
        self.pdf_viewer.zoom_out()
    
    def fit_width(self):
        """Fit to width."""
        self.pdf_viewer.zoom_fit_width(self.scroll_area.width())
    
    def fit_page(self):
        """Fit entire page."""
        self.pdf_viewer.zoom_fit_page(self.scroll_area.width(), self.scroll_area.height())
    
    def rotate_left(self):
        """Rotate page left (counter-clockwise)."""
        self.pdf_viewer.rotate_page(-90)
        self.refresh_page()
    
    def rotate_right(self):
        """Rotate page right (clockwise)."""
        self.pdf_viewer.rotate_page(90)
        self.refresh_page()
    
    def on_document_loaded(self, filename: str):
        """Handle document loaded."""
        if self.pdf_viewer.document:
            page_count = self.pdf_viewer.get_page_count()
            
            # Update page controls
            self.page_spinbox.setMaximum(page_count)
            self.page_spinbox.setValue(1)
            self.page_total_label.setText(f"of {page_count}")
            
            # Enable controls
            self.set_controls_enabled(True)
            
            # Refresh display
            self.refresh_page()
    
    def on_page_changed(self, page_num: int):
        """Handle page changed."""
        # Update page spinbox (convert to 1-based)
        self.page_spinbox.setValue(page_num + 1)
        
        # Refresh display
        self.refresh_page()
        
        # Emit signal
        self.page_changed.emit(page_num)
    
    def on_zoom_changed(self, zoom_level: float):
        """Handle zoom changed."""
        # Update zoom combo
        zoom_percent = int(zoom_level * 100)
        zoom_text = f"{zoom_percent}%"
        
        # Find and set the zoom level in combo
        index = self.zoom_combo.findText(zoom_text)
        if index >= 0:
            self.zoom_combo.setCurrentIndex(index)
        else:
            # Add custom zoom level
            self.zoom_combo.setEditText(zoom_text)
        
        # Refresh display
        self.refresh_page()
        
        # Emit signal
        self.zoom_changed.emit(zoom_level)
    
    def on_page_clicked(self, x: int, y: int):
        """Handle page click for annotations."""
        # TODO: Handle page clicks for adding annotations
        pass
    
    def refresh_page(self):
        """Refresh the current page display."""
        if self.pdf_viewer.document:
            pixmap = self.pdf_viewer.render_page()
            if pixmap:
                self.current_pixmap = pixmap
                self.page_widget.setPixmap(pixmap)
                
                # Adjust widget size to pixmap
                self.page_widget.resize(pixmap.size())
    
    def set_controls_enabled(self, enabled: bool):
        """Enable/disable navigation controls."""
        controls = [
            self.btn_first, self.btn_prev, self.btn_next, self.btn_last,
            self.page_spinbox, self.zoom_combo, self.btn_zoom_in, self.btn_zoom_out,
            self.btn_rotate_left, self.btn_rotate_right
        ]
        
        for control in controls:
            control.setEnabled(enabled)
    
    def get_current_pixmap(self) -> QPixmap:
        """Get the current page pixmap."""
        return self.current_pixmap
