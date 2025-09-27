"""
ScalPDF Command Line Interface
Provides CLI commands for PDF operations
"""

import click
import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.crypto import PDFCrypto
from core.compress import PDFCompressor, CompressionPreset
from core.editor import PDFEditor
from core.annotations import PDFAnnotations


def validate_file_exists(ctx, param, value):
    """Validate that input file exists."""
    if value is None:
        return value
    
    path = Path(value)
    if not path.exists():
        raise click.BadParameter(f"File does not exist: {value}")
    
    return path


def validate_output_dir(ctx, param, value):
    """Validate output directory."""
    if value is None:
        return value
    
    path = Path(value)
    if not path.parent.exists():
        raise click.BadParameter(f"Output directory does not exist: {path.parent}")
    
    return path


@click.group()
@click.version_option(version="1.0.0", prog_name="ScalPDF")
def cli():
    """
    ScalPDF - Secure, Cross-platform, Offline PDF Management Tool
    
    A privacy-first PDF management tool that works completely offline.
    Manage, edit, compress, and secure your PDF documents.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), callback=validate_file_exists)
@click.option('-o', '--output', 'output_file', type=click.Path(), callback=validate_output_dir,
              help='Output file path')
@click.option('--preset', type=click.Choice(['max-quality', 'balanced', 'max-compression']),
              default='balanced', help='Compression preset (default: balanced)')
@click.option('--quality', type=click.IntRange(50, 100), default=None,
              help='Image quality (50-100, overrides preset)')
@click.option('--dpi', type=click.IntRange(72, 600), default=None,
              help='Target DPI (overrides preset)')
@click.option('--no-linearize', is_flag=True, help='Disable PDF linearization')
@click.option('--no-cleanup', is_flag=True, help='Disable unused object removal')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
def compress(input_file: Path, output_file: Optional[Path], preset: str, 
            quality: Optional[int], dpi: Optional[int], no_linearize: bool,
            no_cleanup: bool, verbose: bool):
    """
    Compress a PDF file.
    
    Examples:
    
        scalpdf compress document.pdf -o compressed.pdf
        
        scalpdf compress large.pdf --preset max-compression
        
        scalpdf compress image-heavy.pdf --quality 70 --dpi 150
    """
    try:
        # Set default output file
        if not output_file:
            output_file = input_file.with_stem(f"{input_file.stem}_compressed")
        
        # Map preset names
        preset_map = {
            'max-quality': CompressionPreset.MAX_QUALITY,
            'balanced': CompressionPreset.BALANCED,
            'max-compression': CompressionPreset.MAX_COMPRESSION
        }
        
        compression_preset = preset_map[preset]
        
        # Create custom settings if specified
        custom_settings = {}
        if quality is not None:
            custom_settings['image_quality'] = quality
            custom_settings['jpeg_quality'] = quality
        
        if dpi is not None:
            custom_settings['image_dpi'] = dpi
        
        if no_linearize:
            custom_settings['linearize'] = False
        
        if no_cleanup:
            custom_settings['remove_unused'] = False
        
        if verbose:
            click.echo(f"Compressing: {input_file}")
            click.echo(f"Output: {output_file}")
            click.echo(f"Preset: {preset}")
            if custom_settings:
                click.echo(f"Custom settings: {custom_settings}")
        
        # Compress PDF
        compressor = PDFCompressor()
        
        with click.progressbar(length=100, label='Compressing PDF') as bar:
            # Simulate progress (in real implementation, this would be more granular)
            bar.update(20)
            
            result = compressor.compress_pdf(
                input_file, output_file, compression_preset, custom_settings
            )
            
            bar.update(80)
        
        # Display results
        original_size = result['original_size']
        compressed_size = result['compressed_size']
        reduction = result['size_reduction']
        ratio = result['compression_ratio']
        
        click.echo(f"\n✅ Compression completed successfully!")
        click.echo(f"Original size: {format_file_size(original_size)}")
        click.echo(f"Compressed size: {format_file_size(compressed_size)}")
        click.echo(f"Size reduction: {format_file_size(reduction)} ({ratio:.1f}%)")
        click.echo(f"Images processed: {result['images_processed']}")
        
    except Exception as e:
        click.echo(f"❌ Compression failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), callback=validate_file_exists)
@click.option('-o', '--output', 'output_file', type=click.Path(), callback=validate_output_dir,
              help='Output file path')
@click.option('-p', '--password', prompt=True, hide_input=True,
              help='Encryption password')
@click.option('--no-copy', is_flag=True, help='Prevent copying text')
@click.option('--no-print', is_flag=True, help='Prevent printing')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
def encrypt(input_file: Path, output_file: Optional[Path], password: str,
           no_copy: bool, no_print: bool, verbose: bool):
    """
    Encrypt a PDF file with AES-256-GCM.
    
    Examples:
    
        scalpdf encrypt document.pdf -o encrypted.scalpdf
        
        scalpdf encrypt sensitive.pdf --no-copy --no-print
    """
    try:
        # Set default output file
        if not output_file:
            output_file = input_file.with_suffix('.scalpdf')
        
        if verbose:
            click.echo(f"Encrypting: {input_file}")
            click.echo(f"Output: {output_file}")
            click.echo(f"Security options: copy={not no_copy}, print={not no_print}")
        
        # Encrypt PDF
        crypto = PDFCrypto()
        
        with click.progressbar(length=100, label='Encrypting PDF') as bar:
            bar.update(30)
            
            crypto.encrypt_file(input_file, output_file, password)
            
            bar.update(70)
        
        click.echo(f"\n✅ Encryption completed successfully!")
        click.echo(f"Encrypted file: {output_file}")
        click.echo("⚠️  Keep your password safe - it cannot be recovered!")
        
    except Exception as e:
        click.echo(f"❌ Encryption failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), callback=validate_file_exists)
@click.option('-o', '--output', 'output_file', type=click.Path(), callback=validate_output_dir,
              help='Output file path')
@click.option('-p', '--password', prompt=True, hide_input=True,
              help='Decryption password')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
def decrypt(input_file: Path, output_file: Optional[Path], password: str, verbose: bool):
    """
    Decrypt a ScalPDF encrypted file.
    
    Examples:
    
        scalpdf decrypt encrypted.scalpdf -o decrypted.pdf
    """
    try:
        # Set default output file
        if not output_file:
            if input_file.suffix == '.scalpdf':
                output_file = input_file.with_suffix('.pdf')
            else:
                output_file = input_file.with_stem(f"{input_file.stem}_decrypted")
        
        if verbose:
            click.echo(f"Decrypting: {input_file}")
            click.echo(f"Output: {output_file}")
        
        # Decrypt PDF
        crypto = PDFCrypto()
        
        with click.progressbar(length=100, label='Decrypting PDF') as bar:
            bar.update(30)
            
            crypto.decrypt_file(input_file, output_file, password)
            
            bar.update(70)
        
        click.echo(f"\n✅ Decryption completed successfully!")
        click.echo(f"Decrypted file: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Decryption failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('-o', '--output', 'output_file', type=click.Path(), callback=validate_output_dir,
              required=True, help='Output file path')
@click.option('--pages', multiple=True, help='Page ranges for each file (e.g., "1-3", "all")')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
def merge(input_files: List[str], output_file: Path, pages: List[str], verbose: bool):
    """
    Merge multiple PDF files into one.
    
    Examples:
    
        scalpdf merge file1.pdf file2.pdf file3.pdf -o merged.pdf
        
        scalpdf merge doc1.pdf doc2.pdf -o combined.pdf --pages "1-3" --pages "all"
    """
    try:
        input_paths = [Path(f) for f in input_files]
        
        if verbose:
            click.echo(f"Merging {len(input_paths)} files:")
            for i, path in enumerate(input_paths):
                page_range = pages[i] if i < len(pages) else "all"
                click.echo(f"  {path} (pages: {page_range})")
            click.echo(f"Output: {output_file}")
        
        # Convert pages list to match input files
        page_ranges = list(pages) if pages else None
        
        # Merge PDFs
        editor = PDFEditor()
        
        with click.progressbar(length=100, label='Merging PDFs') as bar:
            bar.update(20)
            
            result = editor.merge_pdfs(input_paths, output_file, page_ranges)
            
            bar.update(80)
        
        click.echo(f"\n✅ Merge completed successfully!")
        click.echo(f"Input files: {result['input_files']}")
        click.echo(f"Total pages processed: {result['total_pages']}")
        click.echo(f"Pages in merged file: {result['merged_pages']}")
        click.echo(f"Output file: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Merge failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), callback=validate_file_exists)
@click.option('-o', '--output-dir', type=click.Path(exists=True), required=True,
              help='Output directory for split files')
@click.option('--pages', type=int, default=1, help='Pages per file (default: 1)')
@click.option('--range', 'page_range', help='Specific page range (e.g., "1-5,10,15-20")')
@click.option('--method', type=click.Choice(['pages', 'range', 'each']), default='each',
              help='Split method (default: each)')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
def split(input_file: Path, output_dir: Path, pages: int, page_range: Optional[str],
         method: str, verbose: bool):
    """
    Split a PDF file.
    
    Examples:
    
        scalpdf split document.pdf -o ./split_files/
        
        scalpdf split large.pdf -o ./parts/ --method pages --pages 5
        
        scalpdf split doc.pdf -o ./extract/ --method range --range "1-3,10-15"
    """
    try:
        if verbose:
            click.echo(f"Splitting: {input_file}")
            click.echo(f"Output directory: {output_dir}")
            click.echo(f"Method: {method}")
            if method == 'pages':
                click.echo(f"Pages per file: {pages}")
            elif method == 'range':
                click.echo(f"Page range: {page_range}")
        
        # Determine split value based on method
        if method == 'pages':
            split_value = pages
        elif method == 'range':
            if not page_range:
                raise click.BadParameter("Page range required for range method")
            split_value = page_range
        else:  # method == 'each'
            split_value = 1
        
        # Split PDF
        editor = PDFEditor()
        
        with click.progressbar(length=100, label='Splitting PDF') as bar:
            bar.update(20)
            
            result = editor.split_pdf(input_file, output_dir, method, split_value)
            
            bar.update(80)
        
        click.echo(f"\n✅ Split completed successfully!")
        click.echo(f"Original pages: {result['input_pages']}")
        click.echo(f"Output files created: {result['output_files']}")
        
        if verbose:
            click.echo("Created files:")
            for file_path in result['files_created']:
                click.echo(f"  {file_path}")
        
    except Exception as e:
        click.echo(f"❌ Split failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True), callback=validate_file_exists)
@click.option('--pages', is_flag=True, help='Show page information')
@click.option('--metadata', is_flag=True, help='Show document metadata')
@click.option('--security', is_flag=True, help='Show security information')
@click.option('--all', 'show_all', is_flag=True, help='Show all information')
def info(input_file: Path, pages: bool, metadata: bool, security: bool, show_all: bool):
    """
    Display information about a PDF file.
    
    Examples:
    
        scalpdf info document.pdf --all
        
        scalpdf info file.pdf --pages --metadata
    """
    try:
        # If no specific options, show basic info
        if not any([pages, metadata, security, show_all]):
            show_all = True
        
        editor = PDFEditor()
        info_data = editor.get_pdf_info(input_file)
        
        if 'error' in info_data:
            click.echo(f"❌ Error reading file: {info_data['error']}", err=True)
            sys.exit(1)
        
        click.echo(f"📄 PDF Information: {input_file.name}")
        click.echo("=" * 50)
        
        # Basic information
        click.echo(f"File size: {format_file_size(info_data['file_size'])}")
        click.echo(f"Pages: {info_data['page_count']}")
        click.echo(f"PDF version: {info_data.get('pdf_version', 'Unknown')}")
        
        if show_all or security:
            click.echo(f"Encrypted: {'Yes' if info_data['encrypted'] else 'No'}")
            click.echo(f"Linearized: {'Yes' if info_data['linearized'] else 'No'}")
        
        if (show_all or pages) and 'pages_info' in info_data:
            click.echo("\n📋 Page Information:")
            for page_info in info_data['pages_info'][:10]:  # Show first 10 pages
                if 'error' in page_info:
                    click.echo(f"  Page {page_info['page_number']}: Error - {page_info['error']}")
                else:
                    width = page_info.get('width', 0)
                    height = page_info.get('height', 0)
                    rotation = page_info.get('rotation', 0)
                    click.echo(f"  Page {page_info['page_number']}: {width:.0f}x{height:.0f} pts, rotation: {rotation}°")
            
            if len(info_data['pages_info']) > 10:
                click.echo(f"  ... and {len(info_data['pages_info']) - 10} more pages")
        
        # Compression analysis
        if show_all:
            compressor = PDFCompressor()
            comp_info = compressor.get_pdf_info(input_file)
            
            if 'error' not in comp_info:
                click.echo(f"\n🗜️  Compression Analysis:")
                click.echo(f"Total images: {comp_info['total_images']}")
                click.echo(f"Large images: {comp_info['large_images']}")
                
                estimates = comp_info.get('estimated_compression', {})
                if estimates:
                    click.echo("Estimated compression potential:")
                    for preset, ratio in estimates.items():
                        click.echo(f"  {preset}: {ratio*100:.1f}% reduction")
        
    except Exception as e:
        click.echo(f"❌ Failed to read file info: {str(e)}", err=True)
        sys.exit(1)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


if __name__ == '__main__':
    cli()
