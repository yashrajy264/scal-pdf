"""
ScalPDF Annotations Module
Handles PDF annotations: highlights, underlines, sticky notes, comments
"""

import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import uuid


class AnnotationType(Enum):
    """Types of annotations supported."""
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    SQUIGGLY = "squiggly"
    NOTE = "note"
    TEXT = "text"
    FREETEXT = "freetext"


class PDFAnnotations:
    """Handles PDF annotations using PyMuPDF."""
    
    def __init__(self):
        """Initialize the annotations handler."""
        self.default_colors = {
            AnnotationType.HIGHLIGHT: (1.0, 1.0, 0.0),      # Yellow
            AnnotationType.UNDERLINE: (0.0, 0.0, 1.0),      # Blue
            AnnotationType.STRIKEOUT: (1.0, 0.0, 0.0),      # Red
            AnnotationType.SQUIGGLY: (1.0, 0.5, 0.0),       # Orange
            AnnotationType.NOTE: (1.0, 1.0, 0.0),           # Yellow
            AnnotationType.TEXT: (0.0, 0.0, 0.0),           # Black
            AnnotationType.FREETEXT: (0.0, 0.0, 0.0)        # Black
        }
    
    def add_highlight(self, doc: fitz.Document, page_num: int, 
                     quad_points: List[Tuple[float, float, float, float]], 
                     color: Optional[Tuple[float, float, float]] = None,
                     opacity: float = 0.5, author: str = "", 
                     content: str = "") -> str:
        """
        Add a highlight annotation.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based)
            quad_points: List of (x0, y0, x1, y1) rectangles to highlight
            color: RGB color tuple (default: yellow)
            opacity: Opacity (0.0 to 1.0)
            author: Author name
            content: Annotation content/comment
            
        Returns:
            Annotation ID
        """
        if page_num < 0 or page_num >= len(doc):
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = doc[page_num]
        color = color or self.default_colors[AnnotationType.HIGHLIGHT]
        
        # Create highlight annotation
        annot_id = str(uuid.uuid4())
        
        for x0, y0, x1, y1 in quad_points:
            rect = fitz.Rect(x0, y0, x1, y1)
            
            # Add highlight annotation
            annot = page.add_highlight_annot(rect)
            annot.set_colors(stroke=color)
            annot.set_opacity(opacity)
            
            # Set annotation properties
            info = {
                "title": author,
                "content": content,
                "id": annot_id,
                "creationDate": datetime.now().isoformat(),
                "modDate": datetime.now().isoformat()
            }
            annot.set_info(info)
            annot.update()
        
        return annot_id
    
    def add_underline(self, doc: fitz.Document, page_num: int,
                     quad_points: List[Tuple[float, float, float, float]],
                     color: Optional[Tuple[float, float, float]] = None,
                     author: str = "", content: str = "") -> str:
        """
        Add an underline annotation.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based)
            quad_points: List of (x0, y0, x1, y1) rectangles to underline
            color: RGB color tuple (default: blue)
            author: Author name
            content: Annotation content/comment
            
        Returns:
            Annotation ID
        """
        if page_num < 0 or page_num >= len(doc):
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = doc[page_num]
        color = color or self.default_colors[AnnotationType.UNDERLINE]
        
        annot_id = str(uuid.uuid4())
        
        for x0, y0, x1, y1 in quad_points:
            rect = fitz.Rect(x0, y0, x1, y1)
            
            # Add underline annotation
            annot = page.add_underline_annot(rect)
            annot.set_colors(stroke=color)
            
            # Set annotation properties
            info = {
                "title": author,
                "content": content,
                "id": annot_id,
                "creationDate": datetime.now().isoformat(),
                "modDate": datetime.now().isoformat()
            }
            annot.set_info(info)
            annot.update()
        
        return annot_id
    
    def add_sticky_note(self, doc: fitz.Document, page_num: int,
                       position: Tuple[float, float], content: str,
                       author: str = "", icon: str = "Note") -> str:
        """
        Add a sticky note annotation.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based)
            position: (x, y) position for the note
            content: Note content
            author: Author name
            icon: Icon name (Note, Comment, Key, etc.)
            
        Returns:
            Annotation ID
        """
        if page_num < 0 or page_num >= len(doc):
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = doc[page_num]
        
        # Create small rectangle for the note icon
        x, y = position
        rect = fitz.Rect(x, y, x + 20, y + 20)
        
        # Add text annotation (sticky note)
        annot = page.add_text_annot(fitz.Point(x, y), content)
        annot.set_info(title=author, content=content)
        
        # Set icon
        if hasattr(annot, 'set_name'):
            annot.set_name(icon)
        
        annot_id = str(uuid.uuid4())
        info = annot.info
        info["id"] = annot_id
        info["creationDate"] = datetime.now().isoformat()
        info["modDate"] = datetime.now().isoformat()
        annot.set_info(info)
        annot.update()
        
        return annot_id
    
    def add_freetext(self, doc: fitz.Document, page_num: int,
                    rect: Tuple[float, float, float, float], text: str,
                    font_size: float = 12, color: Optional[Tuple[float, float, float]] = None,
                    author: str = "") -> str:
        """
        Add a free text annotation.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based)
            rect: (x0, y0, x1, y1) rectangle for the text
            text: Text content
            font_size: Font size
            color: Text color (default: black)
            author: Author name
            
        Returns:
            Annotation ID
        """
        if page_num < 0 or page_num >= len(doc):
            raise ValueError(f"Invalid page number: {page_num}")
        
        page = doc[page_num]
        color = color or self.default_colors[AnnotationType.FREETEXT]
        
        # Create freetext annotation
        fitz_rect = fitz.Rect(*rect)
        annot = page.add_freetext_annot(fitz_rect, text, fontsize=font_size)
        annot.set_colors(stroke=color)
        
        annot_id = str(uuid.uuid4())
        info = {
            "title": author,
            "content": text,
            "id": annot_id,
            "creationDate": datetime.now().isoformat(),
            "modDate": datetime.now().isoformat()
        }
        annot.set_info(info)
        annot.update()
        
        return annot_id
    
    def get_annotations(self, doc: fitz.Document, page_num: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all annotations from document or specific page.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based), None for all pages
            
        Returns:
            List of annotation dictionaries
        """
        annotations = []
        
        if page_num is not None:
            if page_num < 0 or page_num >= len(doc):
                return annotations
            pages_to_process = [page_num]
        else:
            pages_to_process = range(len(doc))
        
        for p_num in pages_to_process:
            page = doc[p_num]
            
            for annot in page.annots():
                try:
                    annot_dict = self._annotation_to_dict(annot, p_num)
                    annotations.append(annot_dict)
                except Exception:
                    # Skip problematic annotations
                    continue
        
        return annotations
    
    def _annotation_to_dict(self, annot: fitz.Annot, page_num: int) -> Dict[str, Any]:
        """
        Convert PyMuPDF annotation to dictionary.
        
        Args:
            annot: PyMuPDF annotation
            page_num: Page number
            
        Returns:
            Annotation dictionary
        """
        info = annot.info
        
        # Get annotation type
        annot_type = annot.type[1]  # Remove number prefix
        
        # Get coordinates
        rect = annot.rect
        
        # Get colors
        colors = annot.colors
        stroke_color = colors.get("stroke", (0, 0, 0))
        fill_color = colors.get("fill", None)
        
        return {
            "id": info.get("id", str(uuid.uuid4())),
            "type": annot_type.lower(),
            "page": page_num,
            "rect": [rect.x0, rect.y0, rect.x1, rect.y1],
            "content": info.get("content", ""),
            "author": info.get("title", ""),
            "creation_date": info.get("creationDate", ""),
            "modification_date": info.get("modDate", ""),
            "stroke_color": stroke_color,
            "fill_color": fill_color,
            "opacity": getattr(annot, 'opacity', 1.0)
        }
    
    def delete_annotation(self, doc: fitz.Document, page_num: int, annot_id: str) -> bool:
        """
        Delete an annotation by ID.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based)
            annot_id: Annotation ID
            
        Returns:
            True if annotation was deleted
        """
        if page_num < 0 or page_num >= len(doc):
            return False
        
        page = doc[page_num]
        
        for annot in page.annots():
            info = annot.info
            if info.get("id") == annot_id:
                page.delete_annot(annot)
                return True
        
        return False
    
    def update_annotation(self, doc: fitz.Document, page_num: int, annot_id: str,
                         updates: Dict[str, Any]) -> bool:
        """
        Update an annotation.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based)
            annot_id: Annotation ID
            updates: Dictionary with updates
            
        Returns:
            True if annotation was updated
        """
        if page_num < 0 or page_num >= len(doc):
            return False
        
        page = doc[page_num]
        
        for annot in page.annots():
            info = annot.info
            if info.get("id") == annot_id:
                
                # Update content
                if "content" in updates:
                    info["content"] = updates["content"]
                
                # Update author
                if "author" in updates:
                    info["title"] = updates["author"]
                
                # Update colors
                if "stroke_color" in updates:
                    annot.set_colors(stroke=updates["stroke_color"])
                
                if "fill_color" in updates:
                    annot.set_colors(fill=updates["fill_color"])
                
                # Update opacity
                if "opacity" in updates:
                    annot.set_opacity(updates["opacity"])
                
                # Update modification date
                info["modDate"] = datetime.now().isoformat()
                
                annot.set_info(info)
                annot.update()
                return True
        
        return False
    
    def export_annotations_xfdf(self, doc: fitz.Document, output_path: Path) -> None:
        """
        Export annotations to XFDF format.
        
        Args:
            doc: PyMuPDF document
            output_path: Path to save XFDF file
        """
        annotations = self.get_annotations(doc)
        
        # Create XFDF XML structure
        root = ET.Element("xfdf")
        root.set("xmlns", "http://ns.adobe.com/xfdf/")
        
        annots_elem = ET.SubElement(root, "annots")
        
        for annot in annotations:
            annot_elem = ET.SubElement(annots_elem, annot["type"])
            
            # Set attributes
            annot_elem.set("page", str(annot["page"]))
            annot_elem.set("rect", ",".join(map(str, annot["rect"])))
            
            if annot["content"]:
                annot_elem.set("contents", annot["content"])
            
            if annot["author"]:
                annot_elem.set("title", annot["author"])
            
            if annot["creation_date"]:
                annot_elem.set("creationdate", annot["creation_date"])
            
            if annot["stroke_color"]:
                color_hex = "#{:02x}{:02x}{:02x}".format(
                    int(annot["stroke_color"][0] * 255),
                    int(annot["stroke_color"][1] * 255),
                    int(annot["stroke_color"][2] * 255)
                )
                annot_elem.set("color", color_hex)
        
        # Write XFDF file
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
    
    def import_annotations_xfdf(self, doc: fitz.Document, xfdf_path: Path) -> int:
        """
        Import annotations from XFDF format.
        
        Args:
            doc: PyMuPDF document
            xfdf_path: Path to XFDF file
            
        Returns:
            Number of annotations imported
        """
        if not xfdf_path.exists():
            raise FileNotFoundError(f"XFDF file not found: {xfdf_path}")
        
        try:
            tree = ET.parse(xfdf_path)
            root = tree.getroot()
            
            annots_elem = root.find("annots")
            if annots_elem is None:
                return 0
            
            imported_count = 0
            
            for annot_elem in annots_elem:
                try:
                    # Parse annotation data
                    annot_type = annot_elem.tag
                    page_num = int(annot_elem.get("page", 0))
                    rect_str = annot_elem.get("rect", "")
                    content = annot_elem.get("contents", "")
                    author = annot_elem.get("title", "")
                    
                    if not rect_str:
                        continue
                    
                    # Parse rectangle
                    rect_coords = [float(x) for x in rect_str.split(",")]
                    if len(rect_coords) != 4:
                        continue
                    
                    # Parse color
                    color_str = annot_elem.get("color", "#ffff00")
                    if color_str.startswith("#"):
                        r = int(color_str[1:3], 16) / 255.0
                        g = int(color_str[3:5], 16) / 255.0
                        b = int(color_str[5:7], 16) / 255.0
                        color = (r, g, b)
                    else:
                        color = None
                    
                    # Add annotation based on type
                    if annot_type == "highlight":
                        self.add_highlight(doc, page_num, [tuple(rect_coords)], 
                                         color=color, author=author, content=content)
                        imported_count += 1
                    
                    elif annot_type == "underline":
                        self.add_underline(doc, page_num, [tuple(rect_coords)],
                                         color=color, author=author, content=content)
                        imported_count += 1
                    
                    elif annot_type == "text":
                        self.add_sticky_note(doc, page_num, (rect_coords[0], rect_coords[1]),
                                           content=content, author=author)
                        imported_count += 1
                    
                    elif annot_type == "freetext":
                        self.add_freetext(doc, page_num, tuple(rect_coords), 
                                        text=content, color=color, author=author)
                        imported_count += 1
                
                except Exception:
                    # Skip problematic annotations
                    continue
            
            return imported_count
        
        except Exception as e:
            raise RuntimeError(f"Failed to import XFDF: {str(e)}")
    
    def export_annotations_json(self, doc: fitz.Document, output_path: Path) -> None:
        """
        Export annotations to JSON format.
        
        Args:
            doc: PyMuPDF document
            output_path: Path to save JSON file
        """
        annotations = self.get_annotations(doc)
        
        # Convert to JSON-serializable format
        json_data = {
            "annotations": annotations,
            "export_date": datetime.now().isoformat(),
            "total_count": len(annotations)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    def import_annotations_json(self, doc: fitz.Document, json_path: Path) -> int:
        """
        Import annotations from JSON format.
        
        Args:
            doc: PyMuPDF document
            json_path: Path to JSON file
            
        Returns:
            Number of annotations imported
        """
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            annotations = data.get("annotations", [])
            imported_count = 0
            
            for annot in annotations:
                try:
                    annot_type = annot.get("type", "")
                    page_num = annot.get("page", 0)
                    rect = annot.get("rect", [])
                    content = annot.get("content", "")
                    author = annot.get("author", "")
                    stroke_color = annot.get("stroke_color")
                    
                    if len(rect) != 4:
                        continue
                    
                    # Add annotation based on type
                    if annot_type == "highlight":
                        self.add_highlight(doc, page_num, [tuple(rect)],
                                         color=stroke_color, author=author, content=content)
                        imported_count += 1
                    
                    elif annot_type == "underline":
                        self.add_underline(doc, page_num, [tuple(rect)],
                                         color=stroke_color, author=author, content=content)
                        imported_count += 1
                    
                    elif annot_type == "text":
                        self.add_sticky_note(doc, page_num, (rect[0], rect[1]),
                                           content=content, author=author)
                        imported_count += 1
                    
                    elif annot_type == "freetext":
                        self.add_freetext(doc, page_num, tuple(rect),
                                        text=content, color=stroke_color, author=author)
                        imported_count += 1
                
                except Exception:
                    # Skip problematic annotations
                    continue
            
            return imported_count
        
        except Exception as e:
            raise RuntimeError(f"Failed to import JSON: {str(e)}")
    
    def clear_all_annotations(self, doc: fitz.Document, page_num: Optional[int] = None) -> int:
        """
        Clear all annotations from document or specific page.
        
        Args:
            doc: PyMuPDF document
            page_num: Page number (0-based), None for all pages
            
        Returns:
            Number of annotations deleted
        """
        deleted_count = 0
        
        if page_num is not None:
            if page_num < 0 or page_num >= len(doc):
                return 0
            pages_to_process = [page_num]
        else:
            pages_to_process = range(len(doc))
        
        for p_num in pages_to_process:
            page = doc[p_num]
            
            # Get all annotations on this page
            annotations = list(page.annots())
            
            # Delete each annotation
            for annot in annotations:
                page.delete_annot(annot)
                deleted_count += 1
        
        return deleted_count
