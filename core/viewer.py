"""
ScalPDF Viewer Module
Handles PDF viewing and rendering using PyMuPDF
"""

import fitz  # PyMuPDF
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QImage
import io


class PDFViewer(QObject):
    """PDF viewer using PyMuPDF for rendering and page operations."""
    
    # Signals for GUI updates
    document_loaded = Signal(str)  # filename
    page_changed = Signal(int)     # page number
    zoom_changed = Signal(float)   # zoom level
    error_occurred = Signal(str)   # error message
    
    def __init__(self):
        """Initialize the PDF viewer."""
        super().__init__()
        self.document: Optional[fitz.Document] = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.rotation = 0
        self.file_path: Optional[Path] = None
        
        # View modes
        self.VIEW_SINGLE = "single"
        self.VIEW_CONTINUOUS = "continuous"
        self.VIEW_TWO_PAGE = "two_page"
        self.view_mode = self.VIEW_SINGLE
    
    def open_document(self, file_path: Path) -> bool:
        """
        Open a PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Close existing document
            self.close_document()
            
            # Open new document
            self.document = fitz.open(str(file_path))
            self.file_path = file_path
            self.current_page = 0
            self.zoom_level = 1.0
            self.rotation = 0
            
            self.document_loaded.emit(file_path.name)
            self.page_changed.emit(0)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to open PDF: {str(e)}")
            return False
    
    def close_document(self) -> None:
        """Close the current document."""
        if self.document:
            self.document.close()
            self.document = None
            self.file_path = None
            self.current_page = 0
    
    def get_page_count(self) -> int:
        """Get the total number of pages."""
        return len(self.document) if self.document else 0
    
    def get_current_page(self) -> int:
        """Get the current page number (0-based)."""
        return self.current_page
    
    def set_page(self, page_num: int) -> bool:
        """
        Set the current page.
        
        Args:
            page_num: Page number (0-based)
            
        Returns:
            True if successful
        """
        if not self.document or page_num < 0 or page_num >= len(self.document):
            return False
        
        self.current_page = page_num
        self.page_changed.emit(page_num)
        return True
    
    def next_page(self) -> bool:
        """Go to next page."""
        return self.set_page(self.current_page + 1)
    
    def previous_page(self) -> bool:
        """Go to previous page."""
        return self.set_page(self.current_page - 1)
    
    def set_zoom(self, zoom_level: float) -> None:
        """
        Set zoom level.
        
        Args:
            zoom_level: Zoom level (1.0 = 100%)
        """
        self.zoom_level = max(0.1, min(10.0, zoom_level))
        self.zoom_changed.emit(self.zoom_level)
    
    def zoom_in(self) -> None:
        """Zoom in by 25%."""
        self.set_zoom(self.zoom_level * 1.25)
    
    def zoom_out(self) -> None:
        """Zoom out by 25%."""
        self.set_zoom(self.zoom_level * 0.8)
    
    def zoom_fit_width(self, widget_width: int) -> None:
        """
        Zoom to fit page width.
        
        Args:
            widget_width: Width of the display widget
        """
        if not self.document:
            return
        
        page = self.document[self.current_page]
        page_rect = page.rect
        zoom = widget_width / page_rect.width * 0.95  # 5% margin
        self.set_zoom(zoom)
    
    def zoom_fit_page(self, widget_width: int, widget_height: int) -> None:
        """
        Zoom to fit entire page.
        
        Args:
            widget_width: Width of the display widget
            widget_height: Height of the display widget
        """
        if not self.document:
            return
        
        page = self.document[self.current_page]
        page_rect = page.rect
        
        zoom_w = widget_width / page_rect.width * 0.95
        zoom_h = widget_height / page_rect.height * 0.95
        zoom = min(zoom_w, zoom_h)
        
        self.set_zoom(zoom)
    
    def rotate_page(self, degrees: int) -> None:
        """
        Rotate the current page.
        
        Args:
            degrees: Rotation in degrees (90, 180, 270)
        """
        self.rotation = (self.rotation + degrees) % 360
    
    def render_page(self, page_num: Optional[int] = None, 
                   zoom: Optional[float] = None) -> Optional[QPixmap]:
        """
        Render a page as QPixmap.
        
        Args:
            page_num: Page number to render (default: current page)
            zoom: Zoom level (default: current zoom)
            
        Returns:
            QPixmap of the rendered page or None if error
        """
        if not self.document:
            return None
        
        page_num = page_num if page_num is not None else self.current_page
        zoom = zoom if zoom is not None else self.zoom_level
        
        if page_num < 0 or page_num >= len(self.document):
            return None
        
        try:
            page = self.document[page_num]
            
            # Create transformation matrix
            mat = fitz.Matrix(zoom, zoom)
            if self.rotation:
                mat = mat * fitz.Matrix(self.rotation)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to QImage then QPixmap
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            
            return QPixmap.fromImage(qimg)
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to render page {page_num + 1}: {str(e)}")
            return None
    
    def get_page_thumbnails(self, max_size: int = 150) -> List[QPixmap]:
        """
        Generate thumbnails for all pages.
        
        Args:
            max_size: Maximum thumbnail size in pixels
            
        Returns:
            List of thumbnail QPixmaps
        """
        thumbnails = []
        
        if not self.document:
            return thumbnails
        
        for page_num in range(len(self.document)):
            try:
                page = self.document[page_num]
                
                # Calculate zoom to fit thumbnail size
                rect = page.rect
                zoom = min(max_size / rect.width, max_size / rect.height)
                
                # Render thumbnail
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Convert to QPixmap
                img_data = pix.tobytes("ppm")
                qimg = QImage.fromData(img_data)
                thumbnails.append(QPixmap.fromImage(qimg))
                
            except Exception:
                # Add empty pixmap for failed thumbnails
                thumbnails.append(QPixmap(max_size, max_size))
        
        return thumbnails
    
    def search_text(self, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search for text in the document.
        
        Args:
            query: Text to search for
            case_sensitive: Whether search is case sensitive
            
        Returns:
            List of search results with page number and bounding boxes
        """
        results = []
        
        if not self.document or not query.strip():
            return results
        
        flags = 0 if case_sensitive else fitz.TEXT_DEHYPHENATE
        
        for page_num in range(len(self.document)):
            page = self.document[page_num]
            text_instances = page.search_for(query, flags=flags)
            
            for rect in text_instances:
                results.append({
                    'page': page_num,
                    'bbox': (rect.x0, rect.y0, rect.x1, rect.y1),
                    'text': query
                })
        
        return results
    
    def get_page_text(self, page_num: Optional[int] = None) -> str:
        """
        Extract text from a page.
        
        Args:
            page_num: Page number (default: current page)
            
        Returns:
            Extracted text
        """
        if not self.document:
            return ""
        
        page_num = page_num if page_num is not None else self.current_page
        
        if page_num < 0 or page_num >= len(self.document):
            return ""
        
        try:
            page = self.document[page_num]
            return page.get_text()
        except Exception:
            return ""
    
    def get_document_info(self) -> Dict[str, Any]:
        """
        Get document metadata.
        
        Returns:
            Dictionary with document information
        """
        if not self.document:
            return {}
        
        try:
            metadata = self.document.metadata
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(self.document),
                'encrypted': self.document.needs_pass,
                'file_size': self.file_path.stat().st_size if self.file_path else 0
            }
        except Exception:
            return {'page_count': len(self.document) if self.document else 0}
    
    def get_page_size(self, page_num: Optional[int] = None) -> Tuple[float, float]:
        """
        Get page dimensions.
        
        Args:
            page_num: Page number (default: current page)
            
        Returns:
            Tuple of (width, height) in points
        """
        if not self.document:
            return (0.0, 0.0)
        
        page_num = page_num if page_num is not None else self.current_page
        
        if page_num < 0 or page_num >= len(self.document):
            return (0.0, 0.0)
        
        try:
            page = self.document[page_num]
            rect = page.rect
            return (rect.width, rect.height)
        except Exception:
            return (0.0, 0.0)
