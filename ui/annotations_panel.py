"""
ScalPDF Annotations Panel
Panel for managing PDF annotations
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QColorDialog,
    QSlider, QSpinBox, QTextEdit, QGroupBox, QButtonGroup,
    QRadioButton, QCheckBox, QToolButton, QMenu
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QColor, QIcon, QPalette

from typing import Dict, Any, List
from core.annotations import AnnotationType


class ColorButton(QPushButton):
    """Button for selecting colors."""
    
    color_changed = Signal(QColor)
    
    def __init__(self, initial_color: QColor = QColor(255, 255, 0)):
        """Initialize color button."""
        super().__init__()
        
        self.current_color = initial_color
        self.setFixedSize(30, 30)
        self.update_color()
        
        self.clicked.connect(self.choose_color)
    
    def update_color(self):
        """Update button appearance with current color."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                border: 2px solid #333;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #0078d4;
            }}
        """)
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Choose Color")
        if color.isValid():
            self.current_color = color
            self.update_color()
            self.color_changed.emit(color)
    
    def get_color(self) -> QColor:
        """Get current color."""
        return self.current_color
    
    def set_color(self, color: QColor):
        """Set current color."""
        self.current_color = color
        self.update_color()


class AnnotationItem(QWidget):
    """Widget for displaying annotation in list."""
    
    # Signals
    edit_requested = Signal(str)    # annotation_id
    delete_requested = Signal(str)  # annotation_id
    
    def __init__(self, annotation_data: Dict[str, Any]):
        """Initialize annotation item."""
        super().__init__()
        
        self.annotation_data = annotation_data
        self.annotation_id = annotation_data.get('id', '')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with type and page
        header_layout = QHBoxLayout()
        
        # Annotation type and page
        type_text = self.annotation_data.get('type', 'unknown').title()
        page_num = self.annotation_data.get('page', 0) + 1
        header_label = QLabel(f"{type_text} - Page {page_num}")
        header_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Action buttons
        self.btn_edit = QPushButton("✏")
        self.btn_edit.setFixedSize(25, 25)
        self.btn_edit.setToolTip("Edit annotation")
        self.btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.annotation_id))
        header_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑")
        self.btn_delete.setFixedSize(25, 25)
        self.btn_delete.setToolTip("Delete annotation")
        self.btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.annotation_id))
        header_layout.addWidget(self.btn_delete)
        
        layout.addLayout(header_layout)
        
        # Content
        content = self.annotation_data.get('content', '')
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(content_label)
        
        # Author and date
        author = self.annotation_data.get('author', '')
        creation_date = self.annotation_data.get('creation_date', '')
        
        if author or creation_date:
            info_text = f"By: {author}" if author else ""
            if creation_date:
                if info_text:
                    info_text += f" | {creation_date[:10]}"  # Just date part
                else:
                    info_text = creation_date[:10]
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: #999; font-size: 10px;")
            layout.addWidget(info_label)
        
        # Style based on annotation type
        self.setStyleSheet("""
            AnnotationItem {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                margin: 2px;
            }
            AnnotationItem:hover {
                background-color: #f0f0f0;
                border: 1px solid #0078d4;
            }
        """)


class AnnotationsPanel(QWidget):
    """Panel for managing PDF annotations."""
    
    # Signals
    annotation_added = Signal(dict)     # annotation_data
    annotation_edited = Signal(str, dict)  # annotation_id, updates
    annotation_deleted = Signal(str)    # annotation_id
    annotation_mode_changed = Signal(str)  # mode
    
    def __init__(self):
        """Initialize the annotations panel."""
        super().__init__()
        
        self.current_mode = "select"
        self.current_color = QColor(255, 255, 0)  # Yellow
        self.current_opacity = 0.5
        self.annotations: List[Dict[str, Any]] = []
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel("Annotations")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Annotation tools
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Mode selection
        mode_layout = QVBoxLayout()
        
        self.mode_group = QButtonGroup()
        
        self.radio_select = QRadioButton("Select")
        self.radio_select.setChecked(True)
        self.mode_group.addButton(self.radio_select, 0)
        mode_layout.addWidget(self.radio_select)
        
        self.radio_highlight = QRadioButton("Highlight")
        self.mode_group.addButton(self.radio_highlight, 1)
        mode_layout.addWidget(self.radio_highlight)
        
        self.radio_underline = QRadioButton("Underline")
        self.mode_group.addButton(self.radio_underline, 2)
        mode_layout.addWidget(self.radio_underline)
        
        self.radio_note = QRadioButton("Sticky Note")
        self.mode_group.addButton(self.radio_note, 3)
        mode_layout.addWidget(self.radio_note)
        
        self.radio_text = QRadioButton("Free Text")
        self.mode_group.addButton(self.radio_text, 4)
        mode_layout.addWidget(self.radio_text)
        
        tools_layout.addLayout(mode_layout)
        
        # Color and opacity
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        
        self.color_button = ColorButton(self.current_color)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        
        tools_layout.addLayout(color_layout)
        
        # Opacity
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(int(self.current_opacity * 100))
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("50%")
        opacity_layout.addWidget(self.opacity_label)
        
        tools_layout.addLayout(opacity_layout)
        
        layout.addWidget(tools_group)
        
        # Author name
        author_layout = QHBoxLayout()
        author_layout.addWidget(QLabel("Author:"))
        
        self.author_edit = QTextEdit()
        self.author_edit.setMaximumHeight(25)
        self.author_edit.setPlainText("User")
        author_layout.addWidget(self.author_edit)
        
        layout.addLayout(author_layout)
        
        # Annotations list
        list_group = QGroupBox("Annotations")
        list_layout = QVBoxLayout(list_group)
        
        # List controls
        list_controls = QHBoxLayout()
        
        self.btn_export = QPushButton("Export")
        self.btn_export.setToolTip("Export annotations")
        list_controls.addWidget(self.btn_export)
        
        self.btn_import = QPushButton("Import")
        self.btn_import.setToolTip("Import annotations")
        list_controls.addWidget(self.btn_import)
        
        list_controls.addStretch()
        
        self.btn_clear_all = QPushButton("Clear All")
        self.btn_clear_all.setToolTip("Clear all annotations")
        list_controls.addWidget(self.btn_clear_all)
        
        list_layout.addLayout(list_controls)
        
        # Annotations list widget
        self.annotations_list = QListWidget()
        self.annotations_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.annotations_list)
        
        layout.addWidget(list_group)
        
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections."""
        # Mode selection
        self.mode_group.buttonClicked.connect(self.on_mode_changed)
        
        # Color and opacity
        self.color_button.color_changed.connect(self.on_color_changed)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        
        # List controls
        self.btn_export.clicked.connect(self.export_annotations)
        self.btn_import.clicked.connect(self.import_annotations)
        self.btn_clear_all.clicked.connect(self.clear_all_annotations)
    
    def on_mode_changed(self, button):
        """Handle annotation mode change."""
        mode_map = {
            0: "select",
            1: "highlight",
            2: "underline",
            3: "note",
            4: "text"
        }
        
        button_id = self.mode_group.id(button)
        self.current_mode = mode_map.get(button_id, "select")
        self.annotation_mode_changed.emit(self.current_mode)
    
    def on_color_changed(self, color: QColor):
        """Handle color change."""
        self.current_color = color
    
    def on_opacity_changed(self, value: int):
        """Handle opacity change."""
        self.current_opacity = value / 100.0
        self.opacity_label.setText(f"{value}%")
    
    def add_annotation(self, annotation_data: Dict[str, Any]):
        """Add an annotation to the list."""
        self.annotations.append(annotation_data)
        self.refresh_annotations_list()
        
        # Emit signal
        self.annotation_added.emit(annotation_data)
    
    def remove_annotation(self, annotation_id: str):
        """Remove an annotation from the list."""
        self.annotations = [a for a in self.annotations if a.get('id') != annotation_id]
        self.refresh_annotations_list()
        
        # Emit signal
        self.annotation_deleted.emit(annotation_id)
    
    def update_annotation(self, annotation_id: str, updates: Dict[str, Any]):
        """Update an annotation."""
        for annotation in self.annotations:
            if annotation.get('id') == annotation_id:
                annotation.update(updates)
                break
        
        self.refresh_annotations_list()
        
        # Emit signal
        self.annotation_edited.emit(annotation_id, updates)
    
    def set_annotations(self, annotations: List[Dict[str, Any]]):
        """Set the annotations list."""
        self.annotations = annotations.copy()
        self.refresh_annotations_list()
    
    def refresh_annotations_list(self):
        """Refresh the annotations list display."""
        self.annotations_list.clear()
        
        for annotation in self.annotations:
            item_widget = AnnotationItem(annotation)
            item_widget.edit_requested.connect(self.edit_annotation)
            item_widget.delete_requested.connect(self.remove_annotation)
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            
            self.annotations_list.addItem(list_item)
            self.annotations_list.setItemWidget(list_item, item_widget)
    
    def edit_annotation(self, annotation_id: str):
        """Edit an annotation."""
        # TODO: Open edit dialog
        pass
    
    def export_annotations(self):
        """Export annotations to file."""
        # TODO: Implement annotation export
        pass
    
    def import_annotations(self):
        """Import annotations from file."""
        # TODO: Implement annotation import
        pass
    
    def clear_all_annotations(self):
        """Clear all annotations."""
        self.annotations.clear()
        self.refresh_annotations_list()
        
        # TODO: Clear annotations from document
    
    def get_current_mode(self) -> str:
        """Get current annotation mode."""
        return self.current_mode
    
    def get_current_color(self) -> QColor:
        """Get current annotation color."""
        return self.current_color
    
    def get_current_opacity(self) -> float:
        """Get current annotation opacity."""
        return self.current_opacity
    
    def get_author_name(self) -> str:
        """Get author name."""
        return self.author_edit.toPlainText().strip() or "User"
    
    def set_mode(self, mode: str):
        """Set annotation mode."""
        mode_map = {
            "select": self.radio_select,
            "highlight": self.radio_highlight,
            "underline": self.radio_underline,
            "note": self.radio_note,
            "text": self.radio_text
        }
        
        radio_button = mode_map.get(mode)
        if radio_button:
            radio_button.setChecked(True)
            self.current_mode = mode
            self.annotation_mode_changed.emit(mode)
