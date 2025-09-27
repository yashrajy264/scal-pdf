"""
ScalPDF Thumbnails Panel
Panel for displaying page thumbnails and navigation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush

from typing import List


class ThumbnailItem(QWidget):
    """Custom widget for thumbnail items."""
    
    clicked = Signal(int)  # page number
    
    def __init__(self, page_num: int, pixmap: QPixmap):
        """Initialize thumbnail item."""
        super().__init__()
        
        self.page_num = page_num
        self.pixmap = pixmap
        self.is_selected = False
        
        self.setFixedSize(150, 200)
        self.setStyleSheet("""
            ThumbnailItem {
                border: 2px solid transparent;
                background-color: white;
                margin: 2px;
            }
            ThumbnailItem:hover {
                border: 2px solid #0078d4;
            }
        """)
    
    def paintEvent(self, event):
        """Custom paint event."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        if self.is_selected:
            painter.fillRect(self.rect(), QBrush(Qt.lightGray))
            painter.setPen(QPen(Qt.blue, 3))
        else:
            painter.fillRect(self.rect(), QBrush(Qt.white))
            painter.setPen(QPen(Qt.gray, 1))
        
        painter.drawRect(self.rect())
        
        # Draw thumbnail
        if self.pixmap:
            # Scale pixmap to fit while maintaining aspect ratio
            scaled_pixmap = self.pixmap.scaled(
                self.width() - 10, self.height() - 30,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            
            # Center the pixmap
            x = (self.width() - scaled_pixmap.width()) // 2
            y = 5
            painter.drawPixmap(x, y, scaled_pixmap)
        
        # Draw page number
        painter.setPen(Qt.black)
        painter.drawText(
            0, self.height() - 20, self.width(), 20,
            Qt.AlignCenter, f"Page {self.page_num + 1}"
        )
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.page_num)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self.is_selected = selected
        self.update()


class ThumbnailsPanel(QWidget):
    """Panel for displaying PDF page thumbnails."""
    
    # Signals
    page_selected = Signal(int)  # page number
    
    def __init__(self):
        """Initialize the thumbnails panel."""
        super().__init__()
        
        self.thumbnail_items: List[ThumbnailItem] = []
        self.current_selection = -1
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel("Pages")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Scroll area for thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for thumbnails
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(5)
        
        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_thumbnails)
        controls_layout.addWidget(self.btn_refresh)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
    
    def set_thumbnails(self, thumbnails: List[QPixmap]):
        """Set the thumbnails to display."""
        # Clear existing thumbnails
        self.clear_thumbnails()
        
        # Add new thumbnails
        for i, pixmap in enumerate(thumbnails):
            item = ThumbnailItem(i, pixmap)
            item.clicked.connect(self.on_thumbnail_clicked)
            
            self.container_layout.addWidget(item)
            self.thumbnail_items.append(item)
        
        # Add stretch at the end
        self.container_layout.addStretch()
        
        # Select first page if available
        if self.thumbnail_items:
            self.select_page(0)
    
    def clear_thumbnails(self):
        """Clear all thumbnails."""
        # Remove all thumbnail items
        for item in self.thumbnail_items:
            item.deleteLater()
        
        self.thumbnail_items.clear()
        self.current_selection = -1
        
        # Clear layout
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def select_page(self, page_num: int):
        """Select a specific page."""
        if 0 <= page_num < len(self.thumbnail_items):
            # Deselect previous selection
            if 0 <= self.current_selection < len(self.thumbnail_items):
                self.thumbnail_items[self.current_selection].set_selected(False)
            
            # Select new page
            self.current_selection = page_num
            self.thumbnail_items[page_num].set_selected(True)
            
            # Scroll to selected item
            self.scroll_to_item(page_num)
    
    def scroll_to_item(self, page_num: int):
        """Scroll to make the specified item visible."""
        if 0 <= page_num < len(self.thumbnail_items):
            item = self.thumbnail_items[page_num]
            
            # Calculate the position to scroll to
            item_y = item.y()
            item_height = item.height()
            
            scroll_bar = self.scroll_area.verticalScrollBar()
            viewport_height = self.scroll_area.viewport().height()
            
            # Scroll to center the item in the viewport
            target_position = item_y - (viewport_height - item_height) // 2
            target_position = max(0, min(target_position, scroll_bar.maximum()))
            
            scroll_bar.setValue(target_position)
    
    def on_thumbnail_clicked(self, page_num: int):
        """Handle thumbnail click."""
        self.select_page(page_num)
        self.page_selected.emit(page_num)
    
    def refresh_thumbnails(self):
        """Refresh thumbnails (placeholder for future implementation)."""
        # TODO: Regenerate thumbnails from current document
        pass
    
    def get_selected_page(self) -> int:
        """Get the currently selected page number."""
        return self.current_selection
    
    def set_page_count(self, count: int):
        """Set the total page count (for display purposes)."""
        # Update title to show page count
        title_text = f"Pages ({count})" if count > 0 else "Pages"
        
        # Find and update title label
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and isinstance(item.widget(), QLabel):
                widget = item.widget()
                if widget.text().startswith("Pages"):
                    widget.setText(title_text)
                    break
