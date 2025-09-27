#!/usr/bin/env python3
"""
ScalPDF Portable Application
Ready-to-use ScalPDF application that runs directly without installation.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import subprocess
import threading
import tempfile
import shutil

# Add the parent directory to Python path to import ScalPDF modules
sys.path.insert(0, str(Path(__file__).parent.parent))

class ScalPDFPortable:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF - Secure PDF Viewer & Editor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Center window
        self.center_window()
        
        # Variables
        self.current_pdf = None
        self.pdf_pages = []
        self.current_page = 0
        self.zoom_level = 1.0
        
        # Create GUI
        self.create_gui()
        
        # Check dependencies
        self.check_dependencies()
        
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_gui(self):
        """Create the main GUI."""
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="ScalPDF - Secure PDF Viewer & Editor", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Portable • Offline • Privacy-First")
        subtitle_label.pack()
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar_frame, text="📂 Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="💾 Save", command=self.save_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🔀 Merge PDFs", command=self.merge_pdfs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="✂️ Split PDF", command=self.split_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🗜️ Compress", command=self.compress_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="🔒 Encrypt", command=self.encrypt_pdf).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="❓ Help", command=self.show_help).pack(side=tk.RIGHT)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File list and thumbnails
        left_panel = ttk.LabelFrame(content_frame, text="Files & Pages", padding="5")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.file_listbox = tk.Listbox(left_panel, width=25)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Center panel - PDF viewer
        center_panel = ttk.LabelFrame(content_frame, text="PDF Viewer", padding="5")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # PDF display area
        self.pdf_canvas = tk.Canvas(center_panel, bg='white', width=500, height=400)
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Viewer controls
        viewer_controls = ttk.Frame(center_panel)
        viewer_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(viewer_controls, text="◀", command=self.prev_page).pack(side=tk.LEFT)
        self.page_label = ttk.Label(viewer_controls, text="No PDF loaded")
        self.page_label.pack(side=tk.LEFT, padx=10)
        ttk.Button(viewer_controls, text="▶", command=self.next_page).pack(side=tk.LEFT)
        
        ttk.Button(viewer_controls, text="🔍-", command=self.zoom_out).pack(side=tk.RIGHT)
        ttk.Button(viewer_controls, text="🔍+", command=self.zoom_in).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Right panel - Tools and info
        right_panel = ttk.LabelFrame(content_frame, text="Tools & Info", padding="5")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Notebook for different tool tabs
        notebook = ttk.Notebook(right_panel)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Info tab
        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Info")
        
        self.info_text = scrolledtext.ScrolledText(info_tab, width=30, height=10, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Tools tab
        tools_tab = ttk.Frame(notebook)
        notebook.add(tools_tab, text="Tools")
        
        ttk.Button(tools_tab, text="📝 Add Annotation", command=self.add_annotation).pack(fill=tk.X, pady=2)
        ttk.Button(tools_tab, text="🖍️ Highlight", command=self.highlight_text).pack(fill=tk.X, pady=2)
        ttk.Button(tools_tab, text="📎 Extract Pages", command=self.extract_pages).pack(fill=tk.X, pady=2)
        ttk.Button(tools_tab, text="🔄 Rotate Pages", command=self.rotate_pages).pack(fill=tk.X, pady=2)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready - ScalPDF Portable v1.0", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Initial info
        self.update_info("ScalPDF Portable Application\n\n✅ Ready to use\n✅ No installation required\n✅ Completely offline\n✅ Privacy-first design\n\nOpen a PDF file to get started!")
        
    def check_dependencies(self):
        """Check if required dependencies are available."""
        missing_deps = []
        
        try:
            import fitz  # PyMuPDF
        except ImportError:
            missing_deps.append("PyMuPDF")
            
        try:
            import pikepdf
        except ImportError:
            missing_deps.append("pikepdf")
            
        try:
            from PIL import Image
        except ImportError:
            missing_deps.append("Pillow")
            
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            missing_deps.append("cryptography")
            
        if missing_deps:
            self.update_info(f"⚠️ Missing dependencies:\n{', '.join(missing_deps)}\n\nSome features may not work.\n\nTo install:\npip install {' '.join(missing_deps)}")
            messagebox.showwarning("Dependencies", f"Missing: {', '.join(missing_deps)}\n\nSome features may not work properly.\n\nInstall with: pip install {' '.join(missing_deps)}")
        else:
            self.update_info("✅ All dependencies available\n✅ Full functionality ready")
            
    def update_info(self, text):
        """Update the info panel."""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        
    def update_status(self, text):
        """Update status bar."""
        self.status_bar.config(text=text)
        self.root.update_idletasks()
        
    def open_pdf(self):
        """Open a PDF file."""
        file_path = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("Loading PDF...")
                
                # Try to import PyMuPDF
                try:
                    import fitz
                    
                    # Open PDF
                    doc = fitz.open(file_path)
                    self.current_pdf = doc
                    self.current_page = 0
                    
                    # Update file list
                    self.file_listbox.delete(0, tk.END)
                    self.file_listbox.insert(0, Path(file_path).name)
                    
                    # Update info
                    info = f"📄 {Path(file_path).name}\n\n"
                    info += f"📊 Pages: {len(doc)}\n"
                    info += f"📏 Size: {Path(file_path).stat().st_size / (1024*1024):.1f} MB\n"
                    info += f"🔒 Encrypted: {'Yes' if doc.needs_pass else 'No'}\n"
                    info += f"📝 Title: {doc.metadata.get('title', 'N/A')}\n"
                    info += f"👤 Author: {doc.metadata.get('author', 'N/A')}\n"
                    
                    self.update_info(info)
                    self.display_page()
                    self.update_status(f"Loaded: {Path(file_path).name} ({len(doc)} pages)")
                    
                except ImportError:
                    messagebox.showerror("Error", "PyMuPDF not installed.\n\nInstall with: pip install PyMuPDF")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF:\n{e}")
                self.update_status("Error loading PDF")
                
    def display_page(self):
        """Display current page on canvas."""
        if not self.current_pdf:
            return
            
        try:
            import fitz
            
            page = self.current_pdf[self.current_page]
            
            # Get page as image
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Clear canvas
            self.pdf_canvas.delete("all")
            
            # Create PhotoImage from data
            from tkinter import PhotoImage
            import io
            
            # Convert to PIL Image then to PhotoImage
            try:
                from PIL import Image, ImageTk
                pil_image = Image.open(io.BytesIO(img_data))
                photo = ImageTk.PhotoImage(pil_image)
                
                # Display on canvas
                self.pdf_canvas.create_image(10, 10, anchor=tk.NW, image=photo)
                self.pdf_canvas.image = photo  # Keep a reference
                
                # Update canvas scroll region
                self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))
                
            except ImportError:
                # Fallback without PIL
                self.pdf_canvas.create_text(250, 200, text="PDF Preview\n(Install Pillow for full display)", 
                                          font=('Arial', 16), anchor=tk.CENTER)
            
            # Update page label
            self.page_label.config(text=f"Page {self.current_page + 1} of {len(self.current_pdf)}")
            
        except Exception as e:
            self.pdf_canvas.create_text(250, 200, text=f"Error displaying page:\n{e}", 
                                      font=('Arial', 12), anchor=tk.CENTER)
            
    def prev_page(self):
        """Go to previous page."""
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            
    def next_page(self):
        """Go to next page."""
        if self.current_pdf and self.current_page < len(self.current_pdf) - 1:
            self.current_page += 1
            self.display_page()
            
    def zoom_in(self):
        """Zoom in."""
        self.zoom_level *= 1.2
        self.display_page()
        
    def zoom_out(self):
        """Zoom out."""
        self.zoom_level /= 1.2
        self.display_page()
        
    def save_pdf(self):
        """Save current PDF."""
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.current_pdf.save(file_path)
                messagebox.showinfo("Success", f"PDF saved to:\n{file_path}")
                self.update_status(f"Saved: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF:\n{e}")
                
    def merge_pdfs(self):
        """Merge multiple PDFs."""
        files = filedialog.askopenfilenames(
            title="Select PDFs to merge",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if len(files) < 2:
            messagebox.showwarning("Warning", "Select at least 2 PDF files to merge")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                import fitz
                
                merged_doc = fitz.open()
                
                for file_path in files:
                    doc = fitz.open(file_path)
                    merged_doc.insert_pdf(doc)
                    doc.close()
                
                merged_doc.save(output_file)
                merged_doc.close()
                
                messagebox.showinfo("Success", f"Merged {len(files)} PDFs into:\n{output_file}")
                self.update_status(f"Merged {len(files)} PDFs")
                
            except ImportError:
                messagebox.showerror("Error", "PyMuPDF not installed")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge PDFs:\n{e}")
                
    def split_pdf(self):
        """Split current PDF."""
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        # Simple dialog for page range
        dialog = tk.Toplevel(self.root)
        dialog.title("Split PDF")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter page range to extract:").pack(pady=10)
        ttk.Label(dialog, text="(e.g., 1-5 or 3,7,9)").pack()
        
        range_var = tk.StringVar(value="1-3")
        entry = ttk.Entry(dialog, textvariable=range_var, width=20)
        entry.pack(pady=10)
        
        def do_split():
            try:
                page_range = range_var.get()
                
                # Parse page range
                pages = []
                if '-' in page_range:
                    start, end = map(int, page_range.split('-'))
                    pages = list(range(start-1, end))  # Convert to 0-based
                else:
                    pages = [int(p.strip())-1 for p in page_range.split(',')]
                
                # Ask for output file
                output_file = filedialog.asksaveasfilename(
                    title="Save split PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")]
                )
                
                if output_file:
                    import fitz
                    
                    new_doc = fitz.open()
                    for page_num in pages:
                        if 0 <= page_num < len(self.current_pdf):
                            new_doc.insert_pdf(self.current_pdf, from_page=page_num, to_page=page_num)
                    
                    new_doc.save(output_file)
                    new_doc.close()
                    
                    dialog.destroy()
                    messagebox.showinfo("Success", f"Extracted {len(pages)} pages to:\n{output_file}")
                    self.update_status(f"Split PDF: {len(pages)} pages extracted")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to split PDF:\n{e}")
        
        ttk.Button(dialog, text="Split", command=do_split).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
        
    def compress_pdf(self):
        """Compress current PDF."""
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save compressed PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                # Simple compression by saving with deflate
                self.current_pdf.save(output_file, deflate=True, clean=True)
                
                # Compare sizes
                original_size = Path(self.current_pdf.name).stat().st_size if self.current_pdf.name else 0
                compressed_size = Path(output_file).stat().st_size
                
                if original_size > 0:
                    reduction = (1 - compressed_size / original_size) * 100
                    messagebox.showinfo("Success", f"PDF compressed!\n\nOriginal: {original_size/1024/1024:.1f} MB\nCompressed: {compressed_size/1024/1024:.1f} MB\nReduction: {reduction:.1f}%")
                else:
                    messagebox.showinfo("Success", f"PDF compressed and saved to:\n{output_file}")
                    
                self.update_status("PDF compressed")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to compress PDF:\n{e}")
                
    def encrypt_pdf(self):
        """Encrypt current PDF."""
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        # Simple password dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Encrypt PDF")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter password:").pack(pady=10)
        
        password_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=password_var, show="*", width=20)
        entry.pack(pady=10)
        
        def do_encrypt():
            password = password_var.get()
            if not password:
                messagebox.showwarning("Warning", "Please enter a password")
                return
                
            output_file = filedialog.asksaveasfilename(
                title="Save encrypted PDF",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            
            if output_file:
                try:
                    # Encrypt and save
                    self.current_pdf.save(output_file, encryption=fitz.PDF_ENCRYPT_AES_256, 
                                        user_pw=password, owner_pw=password)
                    
                    dialog.destroy()
                    messagebox.showinfo("Success", f"PDF encrypted and saved to:\n{output_file}")
                    self.update_status("PDF encrypted")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to encrypt PDF:\n{e}")
        
        ttk.Button(dialog, text="Encrypt", command=do_encrypt).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()
        
    def add_annotation(self):
        """Add annotation to current page."""
        messagebox.showinfo("Feature", "Annotation feature coming soon!\n\nThis will allow you to add notes, highlights, and comments to PDF pages.")
        
    def highlight_text(self):
        """Highlight text on current page."""
        messagebox.showinfo("Feature", "Text highlighting feature coming soon!\n\nThis will allow you to highlight and markup text in PDFs.")
        
    def extract_pages(self):
        """Extract specific pages."""
        self.split_pdf()  # Reuse split functionality
        
    def rotate_pages(self):
        """Rotate pages."""
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        try:
            page = self.current_pdf[self.current_page]
            page.set_rotation(page.rotation + 90)
            self.display_page()
            self.update_status("Page rotated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate page:\n{e}")
            
    def show_help(self):
        """Show help dialog."""
        help_text = """ScalPDF Portable - Help

🚀 QUICK START:
• Click "Open PDF" to load a PDF file
• Use navigation buttons to browse pages
• Use zoom buttons to adjust view size

📝 FEATURES:
• PDF Viewing: Multi-page viewing with zoom and navigation
• PDF Merging: Combine multiple PDFs into one
• PDF Splitting: Extract specific pages or ranges
• PDF Compression: Reduce file size
• PDF Encryption: Password-protect documents
• Annotations: Add notes and highlights (coming soon)

🛡️ SECURITY:
• Completely offline operation
• No data collection or telemetry
• Files processed locally only
• AES-256 encryption support

🔧 REQUIREMENTS:
• Python 3.7+
• PyMuPDF (for PDF processing)
• Pillow (for image display)
• tkinter (usually included with Python)

📦 INSTALLATION:
This is a portable application - no installation required!
Just run this file directly.

For full functionality, install dependencies:
pip install PyMuPDF Pillow pikepdf cryptography

🆘 SUPPORT:
Visit: https://github.com/yashrajy264/scal-pdf
"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("ScalPDF Help")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, help_text)
        text_widget.configure(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        
    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Main entry point."""
    print("🚀 Starting ScalPDF Portable...")
    print("=" * 50)
    print("ScalPDF - Secure PDF Viewer & Editor")
    print("Portable Application - No Installation Required")
    print("=" * 50)
    
    try:
        app = ScalPDFPortable()
        app.run()
    except Exception as e:
        print(f"❌ Error starting ScalPDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
