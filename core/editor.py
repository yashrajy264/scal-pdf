"""
ScalPDF Editor Module
Handles PDF editing operations: merge, split, reorder, delete pages
"""

import pikepdf
import fitz  # PyMuPDF
from typing import List, Optional, Tuple, Dict, Any, Union
from pathlib import Path
import tempfile
import shutil


class PDFEditor:
    """Handles PDF editing operations using pikepdf and PyMuPDF."""
    
    def __init__(self):
        """Initialize the PDF editor."""
        pass
    
    def merge_pdfs(self, input_files: List[Path], output_path: Path, 
                  page_ranges: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Merge multiple PDF files into one.
        
        Args:
            input_files: List of PDF file paths to merge
            output_path: Path to save merged PDF
            page_ranges: Optional list of page ranges for each file (e.g., ["1-3", "all", "2,4,6"])
            
        Returns:
            Dictionary with merge statistics
        """
        if not input_files:
            raise ValueError("No input files provided")
        
        total_pages = 0
        merged_pages = 0
        
        try:
            # Create output PDF
            with pikepdf.open() as output_pdf:
                
                for i, input_file in enumerate(input_files):
                    if not input_file.exists():
                        raise FileNotFoundError(f"Input file not found: {input_file}")
                    
                    with pikepdf.open(input_file) as input_pdf:
                        total_pages += len(input_pdf.pages)
                        
                        # Determine which pages to include
                        if page_ranges and i < len(page_ranges):
                            pages_to_include = self._parse_page_range(
                                page_ranges[i], len(input_pdf.pages)
                            )
                        else:
                            pages_to_include = list(range(len(input_pdf.pages)))
                        
                        # Add selected pages
                        for page_idx in pages_to_include:
                            if 0 <= page_idx < len(input_pdf.pages):
                                output_pdf.pages.append(input_pdf.pages[page_idx])
                                merged_pages += 1
                
                # Save merged PDF
                output_pdf.save(output_path)
        
        except Exception as e:
            raise RuntimeError(f"Merge failed: {str(e)}")
        
        return {
            'input_files': len(input_files),
            'total_pages': total_pages,
            'merged_pages': merged_pages,
            'output_size': output_path.stat().st_size,
            'success': True
        }
    
    def split_pdf(self, input_path: Path, output_dir: Path, 
                 split_method: str = "pages", split_value: Union[int, str] = 1) -> Dict[str, Any]:
        """
        Split a PDF file.
        
        Args:
            input_path: Path to input PDF
            output_dir: Directory to save split files
            split_method: "pages" (every N pages), "range" (specific range), or "each" (each page)
            split_value: Pages per file (for "pages"), page range (for "range"), or ignored (for "each")
            
        Returns:
            Dictionary with split statistics
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_files = []
        
        try:
            with pikepdf.open(input_path) as input_pdf:
                total_pages = len(input_pdf.pages)
                
                if split_method == "each":
                    # Split into individual pages
                    for i in range(total_pages):
                        output_file = output_dir / f"{input_path.stem}_page_{i+1:03d}.pdf"
                        
                        with pikepdf.open() as output_pdf:
                            output_pdf.pages.append(input_pdf.pages[i])
                            output_pdf.save(output_file)
                        
                        output_files.append(output_file)
                
                elif split_method == "pages":
                    # Split every N pages
                    pages_per_file = int(split_value)
                    file_num = 1
                    
                    for start_page in range(0, total_pages, pages_per_file):
                        end_page = min(start_page + pages_per_file, total_pages)
                        output_file = output_dir / f"{input_path.stem}_part_{file_num:03d}.pdf"
                        
                        with pikepdf.open() as output_pdf:
                            for page_idx in range(start_page, end_page):
                                output_pdf.pages.append(input_pdf.pages[page_idx])
                            output_pdf.save(output_file)
                        
                        output_files.append(output_file)
                        file_num += 1
                
                elif split_method == "range":
                    # Split by specific page range
                    page_indices = self._parse_page_range(str(split_value), total_pages)
                    output_file = output_dir / f"{input_path.stem}_pages_{split_value}.pdf"
                    
                    with pikepdf.open() as output_pdf:
                        for page_idx in page_indices:
                            if 0 <= page_idx < total_pages:
                                output_pdf.pages.append(input_pdf.pages[page_idx])
                        output_pdf.save(output_file)
                    
                    output_files.append(output_file)
                
                else:
                    raise ValueError(f"Unknown split method: {split_method}")
        
        except Exception as e:
            raise RuntimeError(f"Split failed: {str(e)}")
        
        return {
            'input_pages': total_pages,
            'output_files': len(output_files),
            'files_created': [str(f) for f in output_files],
            'success': True
        }
    
    def reorder_pages(self, input_path: Path, output_path: Path, 
                     new_order: List[int]) -> Dict[str, Any]:
        """
        Reorder pages in a PDF.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save reordered PDF
            new_order: List of page indices in new order (0-based)
            
        Returns:
            Dictionary with reorder statistics
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            with pikepdf.open(input_path) as input_pdf:
                total_pages = len(input_pdf.pages)
                
                # Validate new order
                if len(new_order) != total_pages:
                    raise ValueError(f"New order must contain {total_pages} pages, got {len(new_order)}")
                
                if set(new_order) != set(range(total_pages)):
                    raise ValueError("New order must contain all page indices exactly once")
                
                # Create new PDF with reordered pages
                with pikepdf.open() as output_pdf:
                    for page_idx in new_order:
                        output_pdf.pages.append(input_pdf.pages[page_idx])
                    
                    output_pdf.save(output_path)
        
        except Exception as e:
            raise RuntimeError(f"Reorder failed: {str(e)}")
        
        return {
            'total_pages': len(new_order),
            'reordered': True,
            'output_size': output_path.stat().st_size,
            'success': True
        }
    
    def delete_pages(self, input_path: Path, output_path: Path, 
                    pages_to_delete: List[int]) -> Dict[str, Any]:
        """
        Delete specific pages from a PDF.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save modified PDF
            pages_to_delete: List of page indices to delete (0-based)
            
        Returns:
            Dictionary with deletion statistics
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            with pikepdf.open(input_path) as input_pdf:
                total_pages = len(input_pdf.pages)
                
                # Validate page indices
                invalid_pages = [p for p in pages_to_delete if p < 0 or p >= total_pages]
                if invalid_pages:
                    raise ValueError(f"Invalid page indices: {invalid_pages}")
                
                # Create new PDF without deleted pages
                pages_to_keep = [i for i in range(total_pages) if i not in pages_to_delete]
                
                with pikepdf.open() as output_pdf:
                    for page_idx in pages_to_keep:
                        output_pdf.pages.append(input_pdf.pages[page_idx])
                    
                    output_pdf.save(output_path)
        
        except Exception as e:
            raise RuntimeError(f"Delete pages failed: {str(e)}")
        
        return {
            'original_pages': total_pages,
            'deleted_pages': len(pages_to_delete),
            'remaining_pages': total_pages - len(pages_to_delete),
            'output_size': output_path.stat().st_size,
            'success': True
        }
    
    def extract_pages(self, input_path: Path, output_path: Path, 
                     page_range: str) -> Dict[str, Any]:
        """
        Extract specific pages to a new PDF.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save extracted pages
            page_range: Page range string (e.g., "1-5", "1,3,5", "2-4,7-9")
            
        Returns:
            Dictionary with extraction statistics
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            with pikepdf.open(input_path) as input_pdf:
                total_pages = len(input_pdf.pages)
                
                # Parse page range
                pages_to_extract = self._parse_page_range(page_range, total_pages)
                
                # Create new PDF with extracted pages
                with pikepdf.open() as output_pdf:
                    for page_idx in pages_to_extract:
                        if 0 <= page_idx < total_pages:
                            output_pdf.pages.append(input_pdf.pages[page_idx])
                    
                    output_pdf.save(output_path)
        
        except Exception as e:
            raise RuntimeError(f"Extract pages failed: {str(e)}")
        
        return {
            'original_pages': total_pages,
            'extracted_pages': len(pages_to_extract),
            'page_range': page_range,
            'output_size': output_path.stat().st_size,
            'success': True
        }
    
    def rotate_pages(self, input_path: Path, output_path: Path, 
                    rotation: int, page_range: Optional[str] = None) -> Dict[str, Any]:
        """
        Rotate pages in a PDF.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save rotated PDF
            rotation: Rotation angle (90, 180, 270 degrees)
            page_range: Page range to rotate (default: all pages)
            
        Returns:
            Dictionary with rotation statistics
        """
        if rotation not in [90, 180, 270]:
            raise ValueError("Rotation must be 90, 180, or 270 degrees")
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            with pikepdf.open(input_path) as input_pdf:
                total_pages = len(input_pdf.pages)
                
                # Determine which pages to rotate
                if page_range:
                    pages_to_rotate = self._parse_page_range(page_range, total_pages)
                else:
                    pages_to_rotate = list(range(total_pages))
                
                # Rotate specified pages
                for page_idx in pages_to_rotate:
                    if 0 <= page_idx < total_pages:
                        page = input_pdf.pages[page_idx]
                        # Rotate page
                        current_rotation = page.get('/Rotate', 0)
                        new_rotation = (current_rotation + rotation) % 360
                        page['/Rotate'] = new_rotation
                
                # Save rotated PDF
                input_pdf.save(output_path)
        
        except Exception as e:
            raise RuntimeError(f"Rotate pages failed: {str(e)}")
        
        return {
            'total_pages': total_pages,
            'rotated_pages': len(pages_to_rotate),
            'rotation_degrees': rotation,
            'page_range': page_range or 'all',
            'success': True
        }
    
    def _parse_page_range(self, page_range: str, total_pages: int) -> List[int]:
        """
        Parse a page range string into a list of page indices.
        
        Args:
            page_range: Page range string (e.g., "1-5", "1,3,5", "2-4,7-9")
            total_pages: Total number of pages in document
            
        Returns:
            List of 0-based page indices
        """
        if page_range.lower() == "all":
            return list(range(total_pages))
        
        pages = []
        
        # Split by commas
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Range (e.g., "1-5")
                try:
                    start, end = part.split('-', 1)
                    start_idx = int(start) - 1  # Convert to 0-based
                    end_idx = int(end) - 1      # Convert to 0-based
                    
                    # Validate range
                    start_idx = max(0, min(start_idx, total_pages - 1))
                    end_idx = max(0, min(end_idx, total_pages - 1))
                    
                    if start_idx <= end_idx:
                        pages.extend(range(start_idx, end_idx + 1))
                except ValueError:
                    continue  # Skip invalid ranges
            else:
                # Single page
                try:
                    page_idx = int(part) - 1  # Convert to 0-based
                    if 0 <= page_idx < total_pages:
                        pages.append(page_idx)
                except ValueError:
                    continue  # Skip invalid page numbers
        
        # Remove duplicates and sort
        return sorted(list(set(pages)))
    
    def get_pdf_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        if not file_path.exists():
            return {'error': 'File not found'}
        
        try:
            with pikepdf.open(file_path) as pdf:
                info = {
                    'page_count': len(pdf.pages),
                    'file_size': file_path.stat().st_size,
                    'encrypted': pdf.is_encrypted,
                    'linearized': pdf.is_linearized,
                    'pdf_version': str(pdf.pdf_version),
                    'pages_info': []
                }
                
                # Get information for each page
                for i, page in enumerate(pdf.pages):
                    try:
                        # Get page size
                        mediabox = page.get('/MediaBox')
                        if mediabox:
                            width = float(mediabox[2] - mediabox[0])
                            height = float(mediabox[3] - mediabox[1])
                        else:
                            width = height = 0
                        
                        # Get rotation
                        rotation = page.get('/Rotate', 0)
                        
                        page_info = {
                            'page_number': i + 1,
                            'width': width,
                            'height': height,
                            'rotation': rotation
                        }
                        
                        info['pages_info'].append(page_info)
                    
                    except Exception:
                        # Skip problematic pages
                        info['pages_info'].append({
                            'page_number': i + 1,
                            'error': 'Could not read page info'
                        })
                
                return info
        
        except Exception as e:
            return {'error': str(e)}
    
    def validate_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with validation results
        """
        if not file_path.exists():
            return {'valid': False, 'error': 'File not found'}
        
        try:
            with pikepdf.open(file_path) as pdf:
                # Basic validation
                page_count = len(pdf.pages)
                
                # Try to access each page
                accessible_pages = 0
                for page in pdf.pages:
                    try:
                        # Try to access page properties
                        _ = page.get('/MediaBox')
                        accessible_pages += 1
                    except:
                        pass
                
                return {
                    'valid': True,
                    'page_count': page_count,
                    'accessible_pages': accessible_pages,
                    'encrypted': pdf.is_encrypted,
                    'corrupted_pages': page_count - accessible_pages
                }
        
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
