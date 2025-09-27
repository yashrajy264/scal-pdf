#!/usr/bin/env python3
"""
ScalPDF - Complete PDF Viewer and Editor
Main application entry point for binary compilation
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
import json
import base64

# Import PDF processing libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import pikepdf
    HAS_PIKEPDF = True
except ImportError:
    HAS_PIKEPDF = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

class ScalPDFApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF - Secure PDF Viewer & Editor")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Application state
        self.current_pdf = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.pdf_path = None
        
        # Center window
        self.center_window()
        
        # Create GUI
        self.create_gui()
        
        # Show welcome message
        self.show_welcome()
        
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
        
        # Try to set a modern theme
        try:
            style.theme_use('clam')
        except:
            pass
            
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Toolbar.TButton', padding=5)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        self.create_header(main_frame)
        
        # Toolbar
        self.create_toolbar(main_frame)
        
        # Main content area
        self.create_content_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create application header."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo and title
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="🔒 ScalPDF", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Secure PDF Viewer & Editor • Offline • Privacy-First")
        subtitle_label.pack(anchor=tk.W)
        
        # Version info
        version_frame = ttk.Frame(header_frame)
        version_frame.pack(side=tk.RIGHT)
        
        version_label = ttk.Label(version_frame, text="v1.0.0", font=('Arial', 10))
        version_label.pack(anchor=tk.E)
        
        status_text = "✅ Ready" if HAS_PYMUPDF else "⚠️ Limited"
        status_label = ttk.Label(version_frame, text=status_text, font=('Arial', 10))
        status_label.pack(anchor=tk.E)
        
    def create_toolbar(self, parent):
        """Create toolbar with main actions."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        file_frame = ttk.LabelFrame(toolbar_frame, text="File", padding=5)
        file_frame.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(file_frame, text="📂 Open", command=self.open_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="💾 Save", command=self.save_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="📤 Export", command=self.export_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        
        # PDF operations
        pdf_frame = ttk.LabelFrame(toolbar_frame, text="PDF Tools", padding=5)
        pdf_frame.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(pdf_frame, text="🔀 Merge", command=self.merge_pdfs, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(pdf_frame, text="✂️ Split", command=self.split_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(pdf_frame, text="🗜️ Compress", command=self.compress_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        
        # Security operations
        security_frame = ttk.LabelFrame(toolbar_frame, text="Security", padding=5)
        security_frame.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(security_frame, text="🔒 Encrypt", command=self.encrypt_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(security_frame, text="🔓 Decrypt", command=self.decrypt_pdf, style='Toolbar.TButton').pack(side=tk.LEFT, padx=2)
        
        # Help
        help_frame = ttk.Frame(toolbar_frame)
        help_frame.pack(side=tk.RIGHT)
        
        ttk.Button(help_frame, text="❓ Help", command=self.show_help, style='Toolbar.TButton').pack()
        
    def create_content_area(self, parent):
        """Create main content area."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable panels
        paned_window = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File browser and thumbnails
        left_panel = ttk.LabelFrame(paned_window, text="Files & Pages", padding=5)
        paned_window.add(left_panel, weight=1)
        
        # File listbox
        self.file_listbox = tk.Listbox(left_panel, height=8)
        self.file_listbox.pack(fill=tk.X, pady=(0, 5))
        self.file_listbox.bind('<Double-1>', self.on_file_selected)
        
        # Page thumbnails (placeholder)
        thumb_label = ttk.Label(left_panel, text="Page Thumbnails")
        thumb_label.pack()
        
        self.thumb_frame = ttk.Frame(left_panel)
        self.thumb_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center panel - PDF viewer
        center_panel = ttk.LabelFrame(paned_window, text="PDF Viewer", padding=5)
        paned_window.add(center_panel, weight=3)
        
        # PDF display area with scrollbars
        canvas_frame = ttk.Frame(center_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white', width=600, height=500)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Viewer controls
        controls_frame = ttk.Frame(center_panel)
        controls_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Navigation
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text="⏮️", command=self.first_page).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="◀️", command=self.prev_page).pack(side=tk.LEFT, padx=1)
        
        self.page_label = ttk.Label(nav_frame, text="No PDF loaded")
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(nav_frame, text="▶️", command=self.next_page).pack(side=tk.LEFT, padx=1)
        ttk.Button(nav_frame, text="⏭️", command=self.last_page).pack(side=tk.LEFT, padx=1)
        
        # Zoom controls
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.pack(side=tk.RIGHT)
        
        ttk.Button(zoom_frame, text="🔍➖", command=self.zoom_out).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_frame, text="🔍➕", command=self.zoom_in).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_frame, text="📐", command=self.fit_width).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_frame, text="🔄", command=self.rotate_page).pack(side=tk.LEFT, padx=1)
        
        # Right panel - Tools and info
        right_panel = ttk.LabelFrame(paned_window, text="Tools & Information", padding=5)
        paned_window.add(right_panel, weight=1)
        
        # Notebook for different tool tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Document info tab
        info_tab = ttk.Frame(self.notebook)
        self.notebook.add(info_tab, text="Document Info")
        
        self.info_text = scrolledtext.ScrolledText(info_tab, width=30, height=15, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Tools tab
        tools_tab = ttk.Frame(self.notebook)
        self.notebook.add(tools_tab, text="Tools")
        
        # Annotation tools
        ttk.Label(tools_tab, text="Annotations:", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(tools_tab, text="📝 Add Note", command=self.add_annotation).pack(fill=tk.X, pady=1)
        ttk.Button(tools_tab, text="🖍️ Highlight", command=self.highlight_text).pack(fill=tk.X, pady=1)
        ttk.Button(tools_tab, text="📎 Bookmark", command=self.add_bookmark).pack(fill=tk.X, pady=1)
        
        ttk.Separator(tools_tab, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Page tools
        ttk.Label(tools_tab, text="Page Tools:", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(tools_tab, text="📄 Extract Pages", command=self.extract_pages).pack(fill=tk.X, pady=1)
        ttk.Button(tools_tab, text="🔄 Rotate Page", command=self.rotate_page).pack(fill=tk.X, pady=1)
        ttk.Button(tools_tab, text="🗑️ Delete Page", command=self.delete_page).pack(fill=tk.X, pady=1)
        
        # Settings tab
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")
        
        ttk.Label(settings_tab, text="Display:", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.dark_mode = tk.BooleanVar()
        ttk.Checkbutton(settings_tab, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode).pack(anchor=tk.W)
        
        self.show_thumbnails = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_tab, text="Show Thumbnails", variable=self.show_thumbnails).pack(anchor=tk.W)
        
    def create_status_bar(self, parent):
        """Create status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready - ScalPDF v1.0.0", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dependency status
        deps_text = f"PyMuPDF: {'✅' if HAS_PYMUPDF else '❌'} | PIL: {'✅' if HAS_PIL else '❌'} | pikepdf: {'✅' if HAS_PIKEPDF else '❌'} | Crypto: {'✅' if HAS_CRYPTO else '❌'}"
        deps_label = ttk.Label(status_frame, text=deps_text, font=('Arial', 8))
        deps_label.pack(side=tk.RIGHT)
        
    def show_welcome(self):
        """Show welcome message and check dependencies."""
        welcome_text = "🔒 ScalPDF - Secure PDF Viewer & Editor\n\n"
        welcome_text += "✅ Application loaded successfully\n"
        welcome_text += "🛡️ Offline operation - your privacy is protected\n"
        welcome_text += "🔐 AES-256 encryption support\n\n"
        
        if not HAS_PYMUPDF:
            welcome_text += "⚠️ PyMuPDF not available - PDF viewing limited\n"
        if not HAS_PIL:
            welcome_text += "⚠️ PIL not available - image display limited\n"
        if not HAS_PIKEPDF:
            welcome_text += "⚠️ pikepdf not available - some PDF operations limited\n"
        if not HAS_CRYPTO:
            welcome_text += "⚠️ cryptography not available - encryption limited\n"
            
        if HAS_PYMUPDF and HAS_PIL and HAS_PIKEPDF and HAS_CRYPTO:
            welcome_text += "🎉 All features available!\n"
            
        welcome_text += "\n📂 Click 'Open' to load a PDF file and get started!"
        
        self.update_info(welcome_text)
        
    def update_info(self, text):
        """Update the info panel."""
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        
    def update_status(self, text):
        """Update status bar."""
        self.status_label.config(text=text)
        self.root.update_idletasks()
        
    def open_pdf(self):
        """Open a PDF file."""
        if not HAS_PYMUPDF:
            messagebox.showerror("Error", "PyMuPDF is required for PDF viewing.\n\nThis feature is not available in this build.")
            return
            
        file_path = filedialog.askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("Loading PDF...")
                
                # Open PDF with PyMuPDF
                doc = fitz.open(file_path)
                
                if doc.needs_pass:
                    password = self.get_password("PDF Password Required", "Enter password for encrypted PDF:")
                    if password:
                        if not doc.authenticate(password):
                            messagebox.showerror("Error", "Invalid password")
                            doc.close()
                            return
                    else:
                        doc.close()
                        return
                
                self.current_pdf = doc
                self.pdf_path = file_path
                self.current_page = 0
                
                # Update file list
                self.file_listbox.delete(0, tk.END)
                self.file_listbox.insert(0, Path(file_path).name)
                
                # Update document info
                self.update_document_info()
                
                # Display first page
                self.display_page()
                
                self.update_status(f"Loaded: {Path(file_path).name} ({len(doc)} pages)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
                self.update_status("Error loading PDF")
                
    def display_page(self):
        """Display current page on canvas."""
        if not self.current_pdf or not HAS_PYMUPDF:
            return
            
        try:
            page = self.current_pdf[self.current_page]
            
            # Get page as image
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            
            if HAS_PIL:
                # Convert to PIL Image then to PhotoImage
                img_data = pix.tobytes("ppm")
                from io import BytesIO
                pil_image = Image.open(BytesIO(img_data))
                photo = ImageTk.PhotoImage(pil_image)
                
                # Clear canvas and display image
                self.pdf_canvas.delete("all")
                self.pdf_canvas.create_image(10, 10, anchor=tk.NW, image=photo)
                self.pdf_canvas.image = photo  # Keep reference
                
                # Update scroll region
                self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))
            else:
                # Fallback without PIL
                self.pdf_canvas.delete("all")
                self.pdf_canvas.create_text(300, 250, text="PDF Page Preview\n(PIL required for full display)", 
                                          font=('Arial', 16), anchor=tk.CENTER)
            
            # Update page label
            self.page_label.config(text=f"Page {self.current_page + 1} of {len(self.current_pdf)}")
            
        except Exception as e:
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_text(300, 250, text=f"Error displaying page:\n{str(e)}", 
                                      font=('Arial', 12), anchor=tk.CENTER)
            
    def update_document_info(self):
        """Update document information panel."""
        if not self.current_pdf:
            return
            
        try:
            doc = self.current_pdf
            metadata = doc.metadata
            
            info = f"📄 Document Information\n\n"
            info += f"📁 File: {Path(self.pdf_path).name}\n"
            info += f"📊 Pages: {len(doc)}\n"
            info += f"📏 Size: {Path(self.pdf_path).stat().st_size / (1024*1024):.1f} MB\n"
            info += f"🔒 Encrypted: {'Yes' if doc.needs_pass else 'No'}\n"
            info += f"📝 Title: {metadata.get('title', 'N/A')}\n"
            info += f"👤 Author: {metadata.get('author', 'N/A')}\n"
            info += f"📅 Created: {metadata.get('creationDate', 'N/A')}\n"
            info += f"🔧 Producer: {metadata.get('producer', 'N/A')}\n"
            
            # Page info
            if len(doc) > 0:
                page = doc[self.current_page]
                rect = page.rect
                info += f"\n📐 Current Page:\n"
                info += f"   Size: {rect.width:.0f} x {rect.height:.0f} pts\n"
                info += f"   Rotation: {page.rotation}°\n"
            
            self.update_info(info)
            
        except Exception as e:
            self.update_info(f"Error reading document info:\n{str(e)}")
            
    def get_password(self, title, prompt):
        """Get password from user."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text=prompt).pack(pady=10)
        
        password_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=password_var, show="*", width=30)
        entry.pack(pady=5)
        entry.focus()
        
        result = [None]
        
        def ok_clicked():
            result[0] = password_var.get()
            dialog.destroy()
            
        def cancel_clicked():
            dialog.destroy()
            
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: ok_clicked())
        
        dialog.wait_window()
        return result[0]
        
    # Navigation methods
    def first_page(self):
        if self.current_pdf:
            self.current_page = 0
            self.display_page()
            self.update_document_info()
            
    def prev_page(self):
        if self.current_pdf and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            self.update_document_info()
            
    def next_page(self):
        if self.current_pdf and self.current_page < len(self.current_pdf) - 1:
            self.current_page += 1
            self.display_page()
            self.update_document_info()
            
    def last_page(self):
        if self.current_pdf:
            self.current_page = len(self.current_pdf) - 1
            self.display_page()
            self.update_document_info()
            
    def zoom_in(self):
        self.zoom_level *= 1.2
        self.display_page()
        
    def zoom_out(self):
        self.zoom_level /= 1.2
        self.display_page()
        
    def fit_width(self):
        if self.current_pdf and HAS_PYMUPDF:
            page = self.current_pdf[self.current_page]
            canvas_width = self.pdf_canvas.winfo_width()
            page_width = page.rect.width
            if page_width > 0:
                self.zoom_level = (canvas_width - 20) / page_width
                self.display_page()
                
    def rotate_page(self):
        if self.current_pdf and HAS_PYMUPDF:
            try:
                page = self.current_pdf[self.current_page]
                page.set_rotation(page.rotation + 90)
                self.display_page()
                self.update_document_info()
                self.update_status("Page rotated")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rotate page:\n{str(e)}")
                
    # File operations
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
                messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")
                
    def export_pdf(self):
        """Export PDF in different formats."""
        if not self.current_pdf:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
            
        # Simple export as images
        if HAS_PYMUPDF and HAS_PIL:
            folder = filedialog.askdirectory(title="Select folder to export images")
            if folder:
                try:
                    for i, page in enumerate(self.current_pdf):
                        pix = page.get_pixmap()
                        img_path = Path(folder) / f"page_{i+1:03d}.png"
                        pix.save(str(img_path))
                    
                    messagebox.showinfo("Success", f"Exported {len(self.current_pdf)} pages to:\n{folder}")
                    self.update_status(f"Exported {len(self.current_pdf)} pages")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export:\n{str(e)}")
        else:
            messagebox.showinfo("Info", "Export requires PyMuPDF and PIL libraries")
            
    # PDF operations
    def merge_pdfs(self):
        """Merge multiple PDFs."""
        if not HAS_PYMUPDF:
            messagebox.showerror("Error", "PyMuPDF is required for PDF merging")
            return
            
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
                self.update_status("Merging PDFs...")
                
                merged_doc = fitz.open()
                
                for file_path in files:
                    doc = fitz.open(file_path)
                    merged_doc.insert_pdf(doc)
                    doc.close()
                
                merged_doc.save(output_file)
                merged_doc.close()
                
                messagebox.showinfo("Success", f"Merged {len(files)} PDFs into:\n{output_file}")
                self.update_status(f"Merged {len(files)} PDFs")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")
                
    def split_pdf(self):
        """Split current PDF."""
        if not self.current_pdf or not HAS_PYMUPDF:
            messagebox.showwarning("Warning", "No PDF loaded or PyMuPDF not available")
            return
            
        # Get page range from user
        dialog = tk.Toplevel(self.root)
        dialog.title("Split PDF")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(dialog, text="Split PDF", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(dialog, text=f"Current PDF has {len(self.current_pdf)} pages").pack()
        
        ttk.Label(dialog, text="Enter page range to extract:").pack(pady=(10, 5))
        ttk.Label(dialog, text="Examples: 1-5, 3,7,9, 1-3,8-10").pack()
        
        range_var = tk.StringVar(value="1-3")
        entry = ttk.Entry(dialog, textvariable=range_var, width=30)
        entry.pack(pady=10)
        entry.focus()
        
        def do_split():
            try:
                page_range = range_var.get().strip()
                
                # Parse page range
                pages = []
                for part in page_range.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        pages.extend(range(start-1, end))  # Convert to 0-based
                    else:
                        pages.append(int(part)-1)  # Convert to 0-based
                
                # Remove duplicates and sort
                pages = sorted(list(set(pages)))
                
                # Validate page numbers
                valid_pages = [p for p in pages if 0 <= p < len(self.current_pdf)]
                
                if not valid_pages:
                    messagebox.showerror("Error", "No valid page numbers found")
                    return
                
                # Ask for output file
                output_file = filedialog.asksaveasfilename(
                    title="Save split PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")]
                )
                
                if output_file:
                    new_doc = fitz.open()
                    for page_num in valid_pages:
                        new_doc.insert_pdf(self.current_pdf, from_page=page_num, to_page=page_num)
                    
                    new_doc.save(output_file)
                    new_doc.close()
                    
                    dialog.destroy()
                    messagebox.showinfo("Success", f"Extracted {len(valid_pages)} pages to:\n{output_file}")
                    self.update_status(f"Split PDF: {len(valid_pages)} pages extracted")
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid page range format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to split PDF:\n{str(e)}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Split", command=do_split).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: do_split())
        
    def compress_pdf(self):
        """Compress current PDF."""
        if not self.current_pdf or not HAS_PYMUPDF:
            messagebox.showwarning("Warning", "No PDF loaded or PyMuPDF not available")
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save compressed PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                self.update_status("Compressing PDF...")
                
                # Save with compression options
                self.current_pdf.save(output_file, 
                                    garbage=4,  # Remove unused objects
                                    deflate=True,  # Compress streams
                                    clean=True)  # Clean up
                
                # Compare sizes
                if self.pdf_path:
                    original_size = Path(self.pdf_path).stat().st_size
                    compressed_size = Path(output_file).stat().st_size
                    reduction = (1 - compressed_size / original_size) * 100
                    
                    messagebox.showinfo("Success", 
                        f"PDF compressed!\n\n"
                        f"Original: {original_size/1024/1024:.1f} MB\n"
                        f"Compressed: {compressed_size/1024/1024:.1f} MB\n"
                        f"Reduction: {reduction:.1f}%")
                else:
                    messagebox.showinfo("Success", f"PDF compressed and saved to:\n{output_file}")
                    
                self.update_status("PDF compressed successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to compress PDF:\n{str(e)}")
                
    def encrypt_pdf(self):
        """Encrypt current PDF."""
        if not self.current_pdf or not HAS_PYMUPDF:
            messagebox.showwarning("Warning", "No PDF loaded or PyMuPDF not available")
            return
            
        password = self.get_password("Encrypt PDF", "Enter password for encryption:")
        if not password:
            return
            
        output_file = filedialog.asksaveasfilename(
            title="Save encrypted PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if output_file:
            try:
                self.update_status("Encrypting PDF...")
                
                # Encrypt and save
                self.current_pdf.save(output_file, 
                                    encryption=fitz.PDF_ENCRYPT_AES_256,
                                    user_pw=password, 
                                    owner_pw=password)
                
                messagebox.showinfo("Success", f"PDF encrypted and saved to:\n{output_file}")
                self.update_status("PDF encrypted successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to encrypt PDF:\n{str(e)}")
                
    def decrypt_pdf(self):
        """Decrypt current PDF."""
        if not self.current_pdf or not HAS_PYMUPDF:
            messagebox.showwarning("Warning", "No PDF loaded or PyMuPDF not available")
            return
            
        if not self.current_pdf.needs_pass:
            messagebox.showinfo("Info", "This PDF is not encrypted")
            return
            
        password = self.get_password("Decrypt PDF", "Enter password to decrypt:")
        if not password:
            return
            
        try:
            if self.current_pdf.authenticate(password):
                output_file = filedialog.asksaveasfilename(
                    title="Save decrypted PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")]
                )
                
                if output_file:
                    self.current_pdf.save(output_file)
                    messagebox.showinfo("Success", f"PDF decrypted and saved to:\n{output_file}")
                    self.update_status("PDF decrypted successfully")
            else:
                messagebox.showerror("Error", "Invalid password")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt PDF:\n{str(e)}")
            
    # Tool methods (placeholders for future implementation)
    def add_annotation(self):
        messagebox.showinfo("Coming Soon", "Annotation feature will be available in a future update!")
        
    def highlight_text(self):
        messagebox.showinfo("Coming Soon", "Text highlighting feature will be available in a future update!")
        
    def add_bookmark(self):
        messagebox.showinfo("Coming Soon", "Bookmark feature will be available in a future update!")
        
    def extract_pages(self):
        self.split_pdf()  # Reuse split functionality
        
    def delete_page(self):
        if not self.current_pdf or not HAS_PYMUPDF:
            messagebox.showwarning("Warning", "No PDF loaded or PyMuPDF not available")
            return
            
        if len(self.current_pdf) <= 1:
            messagebox.showwarning("Warning", "Cannot delete the only page in the document")
            return
            
        if messagebox.askyesno("Confirm", f"Delete page {self.current_page + 1}?"):
            try:
                self.current_pdf.delete_page(self.current_page)
                
                # Adjust current page if necessary
                if self.current_page >= len(self.current_pdf):
                    self.current_page = len(self.current_pdf) - 1
                    
                self.display_page()
                self.update_document_info()
                self.update_status("Page deleted")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete page:\n{str(e)}")
                
    def toggle_dark_mode(self):
        """Toggle dark mode (placeholder)."""
        messagebox.showinfo("Coming Soon", "Dark mode will be available in a future update!")
        
    def on_file_selected(self, event):
        """Handle file selection from listbox."""
        # Placeholder for future file management
        pass
        
    def show_help(self):
        """Show help dialog."""
        help_text = """ScalPDF - Secure PDF Viewer & Editor

🚀 QUICK START:
• Click "Open" to load a PDF file
• Use navigation buttons to browse pages
• Use zoom controls to adjust view
• Access PDF tools from the toolbar

📖 PDF VIEWING:
• Navigate: First/Previous/Next/Last page buttons
• Zoom: Zoom in/out, fit to width
• Rotate: Rotate current page
• View document information in right panel

✏️ PDF EDITING:
• Merge: Combine multiple PDFs into one
• Split: Extract specific pages or ranges
• Compress: Reduce file size
• Extract: Save specific pages

🛡️ SECURITY:
• Encrypt: Password-protect PDFs with AES-256
• Decrypt: Remove password protection
• Offline: All processing done locally
• Privacy: No data collection or telemetry

🔧 KEYBOARD SHORTCUTS:
• Ctrl+O: Open PDF
• Ctrl+S: Save PDF
• Page Up/Down: Navigate pages
• Ctrl++/-: Zoom in/out
• F1: Show this help

📋 SYSTEM REQUIREMENTS:
• Python 3.7+
• PyMuPDF (for PDF processing)
• PIL/Pillow (for image display)
• tkinter (usually included)

🆘 SUPPORT:
Visit: https://github.com/yashrajy264/scal-pdf

ScalPDF v1.0.0 - Secure, Offline, Privacy-First
"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("ScalPDF Help")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, help_text)
        text_widget.configure(state=tk.DISABLED)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        
    def run(self):
        """Run the application."""
        try:
            # Bind keyboard shortcuts
            self.root.bind('<Control-o>', lambda e: self.open_pdf())
            self.root.bind('<Control-s>', lambda e: self.save_pdf())
            self.root.bind('<Prior>', lambda e: self.prev_page())  # Page Up
            self.root.bind('<Next>', lambda e: self.next_page())   # Page Down
            self.root.bind('<Control-plus>', lambda e: self.zoom_in())
            self.root.bind('<Control-minus>', lambda e: self.zoom_out())
            self.root.bind('<F1>', lambda e: self.show_help())
            
            # Start the GUI
            self.root.mainloop()
            
        except KeyboardInterrupt:
            pass
        finally:
            # Clean up
            if self.current_pdf:
                self.current_pdf.close()

def main():
    """Main entry point."""
    print("🚀 Starting ScalPDF...")
    print("=" * 50)
    print("ScalPDF - Secure PDF Viewer & Editor")
    print("Version 1.0.0")
    print("Offline • Privacy-First • Secure")
    print("=" * 50)
    
    try:
        app = ScalPDFApp()
        app.run()
    except Exception as e:
        print(f"❌ Error starting ScalPDF: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to show error in GUI if possible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("ScalPDF Error", f"Failed to start ScalPDF:\n\n{str(e)}")
        except:
            pass

if __name__ == "__main__":
    main()
