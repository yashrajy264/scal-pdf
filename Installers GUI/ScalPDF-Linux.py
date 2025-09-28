#!/usr/bin/env python3
"""
ScalPDF - Linux Compatible Version
Self-contained PDF application that installs its own dependencies
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
import importlib.util

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies."""
    dependencies = {
        'fitz': 'PyMuPDF',
        'PIL': 'Pillow', 
        'pikepdf': 'pikepdf',
        'cryptography': 'cryptography',
        'argon2': 'argon2-cffi'
    }
    
    missing = []
    for module, package in dependencies.items():
        if importlib.util.find_spec(module) is None:
            missing.append(package)
    
    if missing:
        print(f"🔧 Installing missing dependencies: {', '.join(missing)}")
        print("This is a one-time setup...")
        
        for package in missing:
            print(f"📦 Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
                return False
        
        print("✅ All dependencies installed!")
        return True
    
    return True

# Install dependencies first
if not check_and_install_dependencies():
    print("❌ Failed to install dependencies. Please run:")
    print("pip install --user PyMuPDF Pillow pikepdf cryptography argon2-cffi")
    sys.exit(1)

# Now import the main application
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Import PDF processing libraries (now they should be available)
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

class ScalPDFLinux:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScalPDF - Secure PDF Viewer & Editor (Linux)")
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
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
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
        
        title_label = ttk.Label(title_frame, text="🔒 ScalPDF Linux", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Secure PDF Viewer & Editor • Offline • Privacy-First")
        subtitle_label.pack(anchor=tk.W)
        
        # Version info
        version_frame = ttk.Frame(header_frame)
        version_frame.pack(side=tk.RIGHT)
        
        version_label = ttk.Label(version_frame, text="v1.0.0 Linux", font=('Arial', 10))
        version_label.pack(anchor=tk.E)
        
        status_text = "✅ Ready" if HAS_PYMUPDF else "⚠️ Installing..."
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
        
        # Left panel - File browser
        left_panel = ttk.LabelFrame(paned_window, text="Files", padding=5)
        paned_window.add(left_panel, weight=1)
        
        # File listbox
        self.file_listbox = tk.Listbox(left_panel, height=10)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Right panel - Info
        right_panel = ttk.LabelFrame(paned_window, text="Information", padding=5)
        paned_window.add(right_panel, weight=1)
        
        self.info_text = scrolledtext.ScrolledText(right_panel, width=30, height=20, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self, parent):
        """Create status bar."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready - ScalPDF Linux v1.0.0", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dependency status
        deps_text = f"PyMuPDF: {'✅' if HAS_PYMUPDF else '❌'} | PIL: {'✅' if HAS_PIL else '❌'} | pikepdf: {'✅' if HAS_PIKEPDF else '❌'}"
        deps_label = ttk.Label(status_frame, text=deps_text, font=('Arial', 8))
        deps_label.pack(side=tk.RIGHT)
        
    def show_welcome(self):
        """Show welcome message."""
        welcome_text = "🔒 ScalPDF Linux - Auto-Installing Dependencies\n\n"
        
        if HAS_PYMUPDF and HAS_PIL and HAS_PIKEPDF and HAS_CRYPTO:
            welcome_text += "✅ All dependencies available!\n"
            welcome_text += "🎉 Ready to use - click Open to load a PDF\n\n"
        else:
            welcome_text += "🔧 Dependencies installed automatically\n"
            welcome_text += "📦 PyMuPDF, Pillow, pikepdf, cryptography\n\n"
            
        welcome_text += "🛡️ Features:\n"
        welcome_text += "• PDF Viewing with zoom and navigation\n"
        welcome_text += "• PDF Merging and splitting\n"
        welcome_text += "• PDF Compression\n"
        welcome_text += "• AES-256 Encryption/Decryption\n"
        welcome_text += "• Completely offline operation\n"
        welcome_text += "• No data collection or telemetry\n\n"
        welcome_text += "📂 Click 'Open' to load a PDF file!"
        
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
            messagebox.showerror("Error", "PyMuPDF is required for PDF viewing.\n\nPlease restart the application to complete dependency installation.")
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
            
        # Simple split - ask for page range
        page_range = tk.simpledialog.askstring("Split PDF", 
            f"Enter page range (1-{len(self.current_pdf)}):\nExample: 1-5 or 3,7,9")
        
        if page_range:
            try:
                # Parse page range
                pages = []
                for part in page_range.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        pages.extend(range(start-1, end))  # Convert to 0-based
                    else:
                        pages.append(int(part)-1)  # Convert to 0-based
                
                # Ask for output file
                output_file = filedialog.asksaveasfilename(
                    title="Save split PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")]
                )
                
                if output_file:
                    new_doc = fitz.open()
                    for page_num in pages:
                        if 0 <= page_num < len(self.current_pdf):
                            new_doc.insert_pdf(self.current_pdf, from_page=page_num, to_page=page_num)
                    
                    new_doc.save(output_file)
                    new_doc.close()
                    
                    messagebox.showinfo("Success", f"Extracted {len(pages)} pages to:\n{output_file}")
                    self.update_status(f"Split PDF: {len(pages)} pages extracted")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to split PDF:\n{str(e)}")
                
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
            
    def show_help(self):
        """Show help dialog."""
        help_text = """ScalPDF Linux - Help

🚀 FEATURES:
• PDF Viewing with zoom and navigation
• PDF Merging and splitting  
• PDF Compression to reduce file size
• AES-256 Encryption and decryption
• Completely offline operation

🔧 DEPENDENCIES:
This version automatically installs required dependencies:
• PyMuPDF - PDF processing
• Pillow - Image handling  
• pikepdf - Advanced PDF operations
• cryptography - Encryption support

📋 USAGE:
1. Click "Open" to load a PDF
2. Use navigation buttons to browse pages
3. Use toolbar for PDF operations
4. All processing is done locally

🛡️ PRIVACY:
• No internet connection required
• No data collection or telemetry
• Files processed locally only
• Your documents remain private

Visit: https://github.com/yashrajy264/scal-pdf
"""
        
        messagebox.showinfo("ScalPDF Help", help_text)
        
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
    print("🚀 Starting ScalPDF Linux...")
    print("=" * 50)
    print("ScalPDF - Secure PDF Viewer & Editor")
    print("Linux Version with Auto-Dependency Installation")
    print("=" * 50)
    
    try:
        app = ScalPDFLinux()
        app.run()
    except Exception as e:
        print(f"❌ Error starting ScalPDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
