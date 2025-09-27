"""
Tests for ScalPDF CLI interface
"""

import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import Mock, patch

from cli.cli import cli, format_file_size


class TestCLI:
    """Test cases for CLI interface."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "ScalPDF" in result.output
        assert "Secure, Cross-platform, Offline PDF Management Tool" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    def test_compress_help(self):
        """Test compress command help."""
        result = self.runner.invoke(cli, ['compress', '--help'])
        assert result.exit_code == 0
        assert "Compress a PDF file" in result.output
    
    @patch('core.compress.PDFCompressor')
    def test_compress_command(self, mock_compressor_class):
        """Test compress command execution."""
        # Mock compressor
        mock_compressor = Mock()
        mock_compressor.compress_pdf.return_value = {
            'original_size': 1000000,
            'compressed_size': 500000,
            'size_reduction': 500000,
            'compression_ratio': 50.0,
            'images_processed': 5
        }
        mock_compressor_class.return_value = mock_compressor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"dummy pdf content")
            
            result = self.runner.invoke(cli, [
                'compress', str(input_file),
                '-o', str(temp_path / "compressed.pdf"),
                '--preset', 'balanced',
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert "Compression completed successfully" in result.output
            assert "50.0%" in result.output
    
    def test_compress_nonexistent_file(self):
        """Test compress command with nonexistent file."""
        result = self.runner.invoke(cli, [
            'compress', 'nonexistent.pdf'
        ])
        
        assert result.exit_code == 2  # Click error code for bad parameter
        assert "does not exist" in result.output
    
    @patch('core.crypto.PDFCrypto')
    def test_encrypt_command(self, mock_crypto_class):
        """Test encrypt command execution."""
        # Mock crypto
        mock_crypto = Mock()
        mock_crypto_class.return_value = mock_crypto
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"dummy pdf content")
            
            result = self.runner.invoke(cli, [
                'encrypt', str(input_file),
                '-o', str(temp_path / "encrypted.scalpdf"),
                '--password', 'test_password',
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert "Encryption completed successfully" in result.output
            mock_crypto.encrypt_file.assert_called_once()
    
    @patch('core.crypto.PDFCrypto')
    def test_decrypt_command(self, mock_crypto_class):
        """Test decrypt command execution."""
        # Mock crypto
        mock_crypto = Mock()
        mock_crypto_class.return_value = mock_crypto
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "encrypted.scalpdf"
            input_file.write_bytes(b"encrypted content")
            
            result = self.runner.invoke(cli, [
                'decrypt', str(input_file),
                '-o', str(temp_path / "decrypted.pdf"),
                '--password', 'test_password',
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert "Decryption completed successfully" in result.output
            mock_crypto.decrypt_file.assert_called_once()
    
    @patch('core.editor.PDFEditor')
    def test_merge_command(self, mock_editor_class):
        """Test merge command execution."""
        # Mock editor
        mock_editor = Mock()
        mock_editor.merge_pdfs.return_value = {
            'input_files': 2,
            'total_pages': 10,
            'merged_pages': 10,
            'success': True
        }
        mock_editor_class.return_value = mock_editor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input files
            input1 = temp_path / "test1.pdf"
            input1.write_bytes(b"pdf1 content")
            
            input2 = temp_path / "test2.pdf"
            input2.write_bytes(b"pdf2 content")
            
            output_file = temp_path / "merged.pdf"
            
            result = self.runner.invoke(cli, [
                'merge', str(input1), str(input2),
                '-o', str(output_file),
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert "Merge completed successfully" in result.output
            mock_editor.merge_pdfs.assert_called_once()
    
    def test_merge_missing_output(self):
        """Test merge command without output file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input1 = temp_path / "test1.pdf"
            input1.write_bytes(b"pdf1 content")
            
            result = self.runner.invoke(cli, [
                'merge', str(input1)
            ])
            
            assert result.exit_code == 2  # Missing required option
    
    @patch('core.editor.PDFEditor')
    def test_split_command(self, mock_editor_class):
        """Test split command execution."""
        # Mock editor
        mock_editor = Mock()
        mock_editor.split_pdf.return_value = {
            'input_pages': 10,
            'output_files': 10,
            'files_created': ['page_001.pdf', 'page_002.pdf'],
            'success': True
        }
        mock_editor_class.return_value = mock_editor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"multi-page pdf content")
            
            result = self.runner.invoke(cli, [
                'split', str(input_file),
                '-o', str(temp_path),
                '--method', 'each',
                '--verbose'
            ])
            
            assert result.exit_code == 0
            assert "Split completed successfully" in result.output
            mock_editor.split_pdf.assert_called_once()
    
    @patch('core.editor.PDFEditor')
    def test_info_command(self, mock_editor_class):
        """Test info command execution."""
        # Mock editor
        mock_editor = Mock()
        mock_editor.get_pdf_info.return_value = {
            'page_count': 5,
            'file_size': 1024000,
            'pdf_version': '1.4',
            'encrypted': False,
            'linearized': True,
            'pages_info': [
                {'page_number': 1, 'width': 612, 'height': 792, 'rotation': 0},
                {'page_number': 2, 'width': 612, 'height': 792, 'rotation': 90}
            ]
        }
        mock_editor_class.return_value = mock_editor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test input file
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"pdf content")
            
            result = self.runner.invoke(cli, [
                'info', str(input_file), '--all'
            ])
            
            assert result.exit_code == 0
            assert "PDF Information" in result.output
            assert "Pages: 5" in result.output
            assert "1.0 MB" in result.output  # Formatted file size
            mock_editor.get_pdf_info.assert_called_once()
    
    def test_format_file_size(self):
        """Test file size formatting function."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(512) == "512.0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1073741824) == "1.0 GB"
    
    def test_invalid_preset(self):
        """Test compress command with invalid preset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"pdf content")
            
            result = self.runner.invoke(cli, [
                'compress', str(input_file),
                '--preset', 'invalid-preset'
            ])
            
            assert result.exit_code == 2  # Click error for invalid choice
    
    def test_split_invalid_method(self):
        """Test split command with invalid method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(b"pdf content")
            
            result = self.runner.invoke(cli, [
                'split', str(input_file),
                '-o', str(temp_path),
                '--method', 'invalid-method'
            ])
            
            assert result.exit_code == 2  # Click error for invalid choice
    
    @patch('core.editor.PDFEditor')
    def test_info_command_error(self, mock_editor_class):
        """Test info command with file error."""
        # Mock editor to return error
        mock_editor = Mock()
        mock_editor.get_pdf_info.return_value = {
            'error': 'Cannot read PDF file'
        }
        mock_editor_class.return_value = mock_editor
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            input_file = temp_path / "corrupt.pdf"
            input_file.write_bytes(b"not a pdf")
            
            result = self.runner.invoke(cli, [
                'info', str(input_file)
            ])
            
            assert result.exit_code == 1
            assert "Error reading file" in result.output
