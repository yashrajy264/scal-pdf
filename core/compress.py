"""
ScalPDF Compression Module
Handles PDF compression with different quality presets
"""

import pikepdf
from PIL import Image
import io
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum


class CompressionPreset(Enum):
    """Compression quality presets."""
    MAX_QUALITY = "max_quality"
    BALANCED = "balanced"
    MAX_COMPRESSION = "max_compression"


class PDFCompressor:
    """Handles PDF compression using pikepdf and Pillow."""
    
    def __init__(self):
        """Initialize the compressor with preset configurations."""
        self.presets = {
            CompressionPreset.MAX_QUALITY: {
                'image_quality': 95,
                'image_dpi': 300,
                'downsample_threshold': 450,  # Only downsample if > 450 DPI
                'jpeg_quality': 95,
                'remove_unused': True,
                'linearize': True,
                'compress_streams': True
            },
            CompressionPreset.BALANCED: {
                'image_quality': 85,
                'image_dpi': 200,
                'downsample_threshold': 250,
                'jpeg_quality': 85,
                'remove_unused': True,
                'linearize': True,
                'compress_streams': True
            },
            CompressionPreset.MAX_COMPRESSION: {
                'image_quality': 70,
                'image_dpi': 150,
                'downsample_threshold': 200,
                'jpeg_quality': 70,
                'remove_unused': True,
                'linearize': True,
                'compress_streams': True
            }
        }
    
    def compress_pdf(self, input_path: Path, output_path: Path, 
                    preset: CompressionPreset = CompressionPreset.BALANCED,
                    custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compress a PDF file.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save compressed PDF
            preset: Compression preset to use
            custom_settings: Override preset settings
            
        Returns:
            Dictionary with compression statistics
        """
        # Get compression settings
        settings = self.presets[preset].copy()
        if custom_settings:
            settings.update(custom_settings)
        
        # Get original file size
        original_size = input_path.stat().st_size
        
        try:
            # Open PDF with pikepdf
            with pikepdf.open(input_path) as pdf:
                
                # Remove unused objects if enabled
                if settings.get('remove_unused', True):
                    pdf.remove_unreferenced_resources()
                
                # Process images
                images_processed = 0
                images_compressed = 0
                
                for page in pdf.pages:
                    images_processed += self._process_page_images(page, settings)
                    images_compressed += 1
                
                # Save with compression options
                save_kwargs = {
                    'linearize': settings.get('linearize', True),
                    'compress_streams': settings.get('compress_streams', True),
                    'stream_decode_level': pikepdf.StreamDecodeLevel.generalized
                }
                
                pdf.save(output_path, **save_kwargs)
        
        except Exception as e:
            raise RuntimeError(f"Compression failed: {str(e)}")
        
        # Calculate compression statistics
        compressed_size = output_path.stat().st_size
        compression_ratio = (original_size - compressed_size) / original_size * 100
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'size_reduction': original_size - compressed_size,
            'compression_ratio': compression_ratio,
            'images_processed': images_processed,
            'preset_used': preset.value,
            'settings': settings
        }
    
    def _process_page_images(self, page: pikepdf.Page, settings: Dict[str, Any]) -> int:
        """
        Process and compress images on a page.
        
        Args:
            page: pikepdf Page object
            settings: Compression settings
            
        Returns:
            Number of images processed
        """
        images_processed = 0
        
        try:
            # Get page resources
            if '/Resources' not in page:
                return 0
            
            resources = page.Resources
            if '/XObject' not in resources:
                return 0
            
            xobjects = resources.XObject
            
            # Process each XObject (potential image)
            for name, xobj in xobjects.items():
                if self._is_image_xobject(xobj):
                    try:
                        self._compress_image_xobject(xobj, settings)
                        images_processed += 1
                    except Exception:
                        # Skip problematic images
                        continue
        
        except Exception:
            # Skip problematic pages
            pass
        
        return images_processed
    
    def _is_image_xobject(self, xobj) -> bool:
        """
        Check if XObject is an image.
        
        Args:
            xobj: XObject to check
            
        Returns:
            True if XObject is an image
        """
        try:
            return (hasattr(xobj, 'Subtype') and 
                   xobj.Subtype == '/Image')
        except:
            return False
    
    def _compress_image_xobject(self, xobj, settings: Dict[str, Any]) -> None:
        """
        Compress an image XObject.
        
        Args:
            xobj: Image XObject to compress
            settings: Compression settings
        """
        try:
            # Get image properties
            width = int(xobj.Width)
            height = int(xobj.Height)
            
            # Skip very small images
            if width < 50 or height < 50:
                return
            
            # Calculate current DPI (assuming 72 DPI base)
            current_dpi = max(width, height) / 8.5 * 72  # Rough estimate
            
            # Check if downsampling is needed
            target_dpi = settings.get('image_dpi', 200)
            downsample_threshold = settings.get('downsample_threshold', 250)
            
            if current_dpi <= downsample_threshold:
                return  # No need to downsample
            
            # Extract image data
            if hasattr(xobj, 'read_bytes'):
                image_data = xobj.read_bytes()
            else:
                return  # Can't extract image data
            
            # Open with Pillow
            try:
                image = Image.open(io.BytesIO(image_data))
            except:
                return  # Can't open image
            
            # Calculate new size for target DPI
            scale_factor = target_dpi / current_dpi
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Resize image
            if scale_factor < 1.0:
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Compress image
            output_buffer = io.BytesIO()
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save as JPEG with quality setting
            jpeg_quality = settings.get('jpeg_quality', 85)
            image.save(output_buffer, format='JPEG', quality=jpeg_quality, optimize=True)
            
            # Replace image data in PDF
            compressed_data = output_buffer.getvalue()
            
            # Update XObject with compressed data
            xobj.write(compressed_data, filter=pikepdf.Name.DCTDecode)
            xobj.Width = new_width
            xobj.Height = new_height
            xobj.ColorSpace = pikepdf.Name.DeviceRGB
            xobj.BitsPerComponent = 8
            
        except Exception:
            # Skip problematic images
            pass
    
    def get_pdf_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Get information about a PDF file for compression analysis.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            with pikepdf.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                # Count images
                total_images = 0
                large_images = 0
                
                for page in pdf.pages:
                    page_images = self._count_page_images(page)
                    total_images += page_images['total']
                    large_images += page_images['large']
                
                # Get file size
                file_size = file_path.stat().st_size
                
                return {
                    'file_size': file_size,
                    'page_count': page_count,
                    'total_images': total_images,
                    'large_images': large_images,
                    'estimated_compression': self._estimate_compression_ratio(
                        file_size, total_images, large_images
                    )
                }
        
        except Exception as e:
            return {
                'error': str(e),
                'file_size': file_path.stat().st_size if file_path.exists() else 0
            }
    
    def _count_page_images(self, page: pikepdf.Page) -> Dict[str, int]:
        """
        Count images on a page.
        
        Args:
            page: pikepdf Page object
            
        Returns:
            Dictionary with image counts
        """
        total = 0
        large = 0
        
        try:
            if '/Resources' in page and '/XObject' in page.Resources:
                xobjects = page.Resources.XObject
                
                for xobj in xobjects.values():
                    if self._is_image_xobject(xobj):
                        total += 1
                        
                        # Check if image is large
                        try:
                            width = int(xobj.Width)
                            height = int(xobj.Height)
                            if width > 1000 or height > 1000:
                                large += 1
                        except:
                            pass
        
        except Exception:
            pass
        
        return {'total': total, 'large': large}
    
    def _estimate_compression_ratio(self, file_size: int, total_images: int, large_images: int) -> Dict[str, float]:
        """
        Estimate potential compression ratios for different presets.
        
        Args:
            file_size: Original file size in bytes
            total_images: Total number of images
            large_images: Number of large images
            
        Returns:
            Dictionary with estimated compression ratios
        """
        # Base compression from PDF optimization
        base_compression = 0.1  # 10%
        
        # Additional compression from image processing
        image_factor = min(0.5, (large_images / max(1, total_images)) * 0.7)
        
        return {
            CompressionPreset.MAX_QUALITY.value: base_compression + image_factor * 0.3,
            CompressionPreset.BALANCED.value: base_compression + image_factor * 0.5,
            CompressionPreset.MAX_COMPRESSION.value: base_compression + image_factor * 0.7
        }
    
    def optimize_pdf(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """
        Optimize PDF without aggressive compression (remove unused objects, linearize).
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save optimized PDF
            
        Returns:
            Dictionary with optimization statistics
        """
        original_size = input_path.stat().st_size
        
        try:
            with pikepdf.open(input_path) as pdf:
                # Remove unused objects
                pdf.remove_unreferenced_resources()
                
                # Save with optimization
                pdf.save(output_path, 
                        linearize=True,
                        compress_streams=True)
        
        except Exception as e:
            raise RuntimeError(f"Optimization failed: {str(e)}")
        
        optimized_size = output_path.stat().st_size
        size_reduction = original_size - optimized_size
        
        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'size_reduction': size_reduction,
            'reduction_percentage': (size_reduction / original_size * 100) if original_size > 0 else 0
        }
