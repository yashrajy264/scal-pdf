"""
Tests for ScalPDF editor module
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from core.editor import PDFEditor


class TestPDFEditor:
    """Test cases for PDF editing operations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.editor = PDFEditor()
    
    def test_parse_page_range_single_pages(self):
        """Test parsing single page numbers."""
        result = self.editor._parse_page_range("1,3,5", 10)
        assert result == [0, 2, 4]  # Convert to 0-based
    
    def test_parse_page_range_ranges(self):
        """Test parsing page ranges."""
        result = self.editor._parse_page_range("1-3,7-9", 10)
        assert result == [0, 1, 2, 6, 7, 8]  # Convert to 0-based
    
    def test_parse_page_range_mixed(self):
        """Test parsing mixed ranges and single pages."""
        result = self.editor._parse_page_range("1,3-5,8", 10)
        assert result == [0, 2, 3, 4, 7]  # Convert to 0-based
    
    def test_parse_page_range_all(self):
        """Test parsing 'all' keyword."""
        result = self.editor._parse_page_range("all", 5)
        assert result == [0, 1, 2, 3, 4]
    
    def test_parse_page_range_out_of_bounds(self):
        """Test parsing with out-of-bounds pages."""
        result = self.editor._parse_page_range("1-3,15-20", 10)
        assert result == [0, 1, 2, 9]  # Only valid pages
    
    def test_parse_page_range_invalid_format(self):
        """Test parsing with invalid format."""
        result = self.editor._parse_page_range("1,abc,3-xyz", 10)
        assert result == [0]  # Only valid pages
    
    def test_parse_page_range_empty(self):
        """Test parsing empty range."""
        result = self.editor._parse_page_range("", 10)
        assert result == []
    
    def test_parse_page_range_duplicates(self):
        """Test parsing with duplicate pages."""
        result = self.editor._parse_page_range("1,2,1-3,2", 10)
        assert result == [0, 1, 2]  # Duplicates removed and sorted
    
    @patch('pikepdf.open')
    def test_merge_pdfs_basic(self, mock_pikepdf_open):
        """Test basic PDF merging."""
        # Mock pikepdf objects
        mock_input_pdf = Mock()
        mock_input_pdf.pages = [Mock(), Mock(), Mock()]  # 3 pages
        
        mock_output_pdf = Mock()
        mock_output_pdf.pages = Mock()
        
        # Configure mock context managers
        mock_pikepdf_open.side_effect = [
            mock_output_pdf,  # Output PDF
            mock_input_pdf,   # Input PDF
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            input_file.touch()  # Create empty file
            
            output_file = temp_path / "output.pdf"
            
            result = self.editor.merge_pdfs([input_file], output_file)
            
            assert result['input_files'] == 1
            assert result['success'] is True
    
    @patch('pikepdf.open')
    def test_split_pdf_each_page(self, mock_pikepdf_open):
        """Test splitting PDF into individual pages."""
        # Mock pikepdf objects
        mock_page1 = Mock()
        mock_page2 = Mock()
        mock_input_pdf = Mock()
        mock_input_pdf.pages = [mock_page1, mock_page2]
        
        mock_output_pdf = Mock()
        mock_output_pdf.pages = Mock()
        
        mock_pikepdf_open.side_effect = [
            mock_input_pdf,    # Input PDF
            mock_output_pdf,   # Output PDF 1
            mock_output_pdf,   # Output PDF 2
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            input_file.touch()
            
            result = self.editor.split_pdf(input_file, temp_path, "each", 1)
            
            assert result['input_pages'] == 2
            assert result['output_files'] == 2
            assert result['success'] is True
    
    @patch('pikepdf.open')
    def test_delete_pages(self, mock_pikepdf_open):
        """Test deleting pages from PDF."""
        # Mock pikepdf objects
        mock_pages = [Mock(), Mock(), Mock(), Mock()]  # 4 pages
        mock_input_pdf = Mock()
        mock_input_pdf.pages = mock_pages
        
        mock_output_pdf = Mock()
        mock_output_pdf.pages = Mock()
        
        mock_pikepdf_open.side_effect = [
            mock_input_pdf,   # Input PDF
            mock_output_pdf,  # Output PDF
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            input_file.touch()
            
            output_file = temp_path / "output.pdf"
            
            # Delete pages 1 and 3 (0-based: 0 and 2)
            result = self.editor.delete_pages(input_file, output_file, [0, 2])
            
            assert result['original_pages'] == 4
            assert result['deleted_pages'] == 2
            assert result['remaining_pages'] == 2
            assert result['success'] is True
    
    @patch('pikepdf.open')
    def test_reorder_pages(self, mock_pikepdf_open):
        """Test reordering pages in PDF."""
        # Mock pikepdf objects
        mock_pages = [Mock(), Mock(), Mock()]  # 3 pages
        mock_input_pdf = Mock()
        mock_input_pdf.pages = mock_pages
        
        mock_output_pdf = Mock()
        mock_output_pdf.pages = Mock()
        
        mock_pikepdf_open.side_effect = [
            mock_input_pdf,   # Input PDF
            mock_output_pdf,  # Output PDF
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            input_file.touch()
            
            output_file = temp_path / "output.pdf"
            
            # Reorder: 3rd, 1st, 2nd page (0-based: 2, 0, 1)
            new_order = [2, 0, 1]
            result = self.editor.reorder_pages(input_file, output_file, new_order)
            
            assert result['total_pages'] == 3
            assert result['reordered'] is True
            assert result['success'] is True
    
    def test_reorder_pages_invalid_order(self):
        """Test reordering with invalid page order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "nonexistent.pdf"
            output_file = temp_path / "output.pdf"
            
            with pytest.raises(FileNotFoundError):
                self.editor.reorder_pages(input_file, output_file, [0, 1])
    
    @patch('pikepdf.open')
    def test_rotate_pages(self, mock_pikepdf_open):
        """Test rotating pages in PDF."""
        # Mock pikepdf objects
        mock_page = Mock()
        mock_page.get.return_value = 0  # Current rotation
        mock_input_pdf = Mock()
        mock_input_pdf.pages = [mock_page]
        
        mock_pikepdf_open.return_value = mock_input_pdf
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            input_file.touch()
            
            output_file = temp_path / "output.pdf"
            
            result = self.editor.rotate_pages(input_file, output_file, 90)
            
            assert result['total_pages'] == 1
            assert result['rotated_pages'] == 1
            assert result['rotation_degrees'] == 90
            assert result['success'] is True
    
    def test_rotate_pages_invalid_angle(self):
        """Test rotating with invalid angle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "input.pdf"
            output_file = temp_path / "output.pdf"
            
            with pytest.raises(ValueError, match="Rotation must be"):
                self.editor.rotate_pages(input_file, output_file, 45)
    
    @patch('pikepdf.open')
    def test_get_pdf_info(self, mock_pikepdf_open):
        """Test getting PDF information."""
        # Mock pikepdf objects
        mock_page = Mock()
        mock_page.get.side_effect = lambda key, default=None: {
            '/MediaBox': [0, 0, 612, 792],  # US Letter size
            '/Rotate': 0
        }.get(key, default)
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page, mock_page]  # 2 pages
        mock_pdf.is_encrypted = False
        mock_pdf.is_linearized = True
        mock_pdf.pdf_version = "1.4"
        
        mock_pikepdf_open.return_value = mock_pdf
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"dummy pdf content")
            
            info = self.editor.get_pdf_info(input_file)
            
            assert info['page_count'] == 2
            assert info['encrypted'] is False
            assert info['linearized'] is True
            assert info['pdf_version'] == "1.4"
            assert len(info['pages_info']) == 2
            
            # Check page info
            page_info = info['pages_info'][0]
            assert page_info['page_number'] == 1
            assert page_info['width'] == 612.0
            assert page_info['height'] == 792.0
            assert page_info['rotation'] == 0
    
    def test_get_pdf_info_nonexistent_file(self):
        """Test getting info for nonexistent file."""
        nonexistent_file = Path("nonexistent.pdf")
        info = self.editor.get_pdf_info(nonexistent_file)
        
        assert 'error' in info
        assert info['error'] == 'File not found'
    
    @patch('pikepdf.open')
    def test_validate_pdf(self, mock_pikepdf_open):
        """Test PDF validation."""
        # Mock valid PDF
        mock_page = Mock()
        mock_page.get.return_value = [0, 0, 612, 792]
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page, mock_page]
        mock_pdf.is_encrypted = False
        
        mock_pikepdf_open.return_value = mock_pdf
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "test.pdf"
            input_file.touch()
            
            result = self.editor.validate_pdf(input_file)
            
            assert result['valid'] is True
            assert result['page_count'] == 2
            assert result['accessible_pages'] == 2
            assert result['corrupted_pages'] == 0
    
    def test_validate_pdf_nonexistent_file(self):
        """Test validating nonexistent file."""
        nonexistent_file = Path("nonexistent.pdf")
        result = self.editor.validate_pdf(nonexistent_file)
        
        assert result['valid'] is False
        assert 'error' in result
