# ScalPDF - Secure PDF Management Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/scalpdf)

**ScalPDF** is a privacy-first, cross-platform desktop application for secure PDF management. Built with Python and Qt, it provides comprehensive PDF operations while maintaining complete offline functionality and user privacy.

## 🔒 Privacy Guarantee

- **100% Offline**: Never connects to the internet
- **No Telemetry**: Zero data collection or analytics
- **Local Processing**: All operations happen on your device
- **No Cloud**: Your files never leave your computer
- **Open Source**: Fully auditable code

## ✨ Features

### 📖 PDF Viewing & Navigation
- Fast PDF rendering with PyMuPDF
- Tabbed document interface
- Zoom, rotate, and page navigation
- Thumbnail panel with page previews
- Text search within documents

### ✏️ Annotations
- Highlight and underline text
- Sticky notes and comments
- Free text annotations
- Export/import annotations (XFDF format)
- Annotation management panel

### 🔧 PDF Editing
- **Merge**: Combine multiple PDFs with page range selection
- **Split**: Extract pages or split by page count
- **Reorder**: Drag and drop page reordering
- **Delete**: Remove unwanted pages
- **Rotate**: Rotate pages individually or in bulk

### 🗜️ Compression
- **Smart Compression**: Three quality presets (Max Quality, Balanced, Max Compression)
- **Image Optimization**: Downsample and recompress images
- **PDF Optimization**: Remove unused objects and linearize
- **Size Analysis**: Preview compression potential before processing

### 🔐 Security & Encryption
- **AES-256-GCM Encryption**: Military-grade encryption
- **Argon2id Key Derivation**: Secure password-based encryption
- **Password Strength Checker**: Real-time password security analysis
- **Memory Protection**: Secure key handling and memory wiping
- **Permission Control**: Prevent copying and printing

### 💻 Command Line Interface
Powerful CLI for batch operations and automation:

```bash
# Compress PDFs
scalpdf compress document.pdf --preset balanced -o compressed.pdf

# Encrypt files
scalpdf encrypt sensitive.pdf -o encrypted.scalpdf

# Merge multiple PDFs
scalpdf merge file1.pdf file2.pdf file3.pdf -o merged.pdf

# Split PDFs
scalpdf split large.pdf -o ./pages/ --method each

# Get PDF information
scalpdf info document.pdf --all
```

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- Windows 10+ or Linux (Ubuntu 20.04+, Fedora 35+, etc.)

### From Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/scalpdf.git
   cd scalpdf
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # GUI
   python main.py
   
   # CLI
   python -m cli.cli --help
   ```

### Pre-built Binaries

Download pre-built executables from the [Releases](https://github.com/yourusername/scalpdf/releases) page:

- **Windows**: `ScalPDF-Windows.zip`
- **Linux**: `ScalPDF-Linux.tar.gz` or `ScalPDF-x86_64.AppImage`

## 🔨 Building from Source

### Build Requirements
```bash
pip install PyInstaller
```

### Build Commands

```bash
# Build for current platform
python build.py

# Build with specific options
python build.py --platform linux --clean

# Build CLI only
python build.py --cli-only

# Debug build
python build.py --debug
```

### Platform-Specific Builds

**Windows**:
```bash
python build.py --platform windows
# Creates: ScalPDF-Windows.zip
```

**Linux**:
```bash
python build.py --platform linux
# Creates: ScalPDF-Linux.tar.gz and ScalPDF-x86_64.AppImage
```

## 📚 Usage

### GUI Application

1. **Open PDFs**: File → Open or drag and drop
2. **View Documents**: Use toolbar for zoom, navigation, and view options
3. **Add Annotations**: Select annotation tools from the right panel
4. **Edit PDFs**: Use toolbar buttons for merge, split, compress operations
5. **Secure Files**: Encrypt/decrypt using the security menu

### Command Line

```bash
# View all available commands
scalpdf --help

# Compress with custom settings
scalpdf compress input.pdf --quality 80 --dpi 200 -o output.pdf

# Encrypt with security options
scalpdf encrypt document.pdf --no-copy --no-print -o secure.scalpdf

# Merge with page ranges
scalpdf merge doc1.pdf doc2.pdf -o merged.pdf --pages "1-3" --pages "all"

# Split by page range
scalpdf split document.pdf -o ./extracted/ --method range --range "5-10,15,20-25"
```

## 🏗️ Architecture

```
scalpdf/
├── main.py              # GUI entry point
├── core/                # Core functionality
│   ├── viewer.py        # PDF viewing (PyMuPDF)
│   ├── crypto.py        # Encryption (AES-256-GCM + Argon2id)
│   ├── compress.py      # PDF compression (pikepdf + Pillow)
│   ├── editor.py        # PDF editing operations
│   └── annotations.py   # Annotation management
├── ui/                  # PySide6 GUI components
│   ├── main_window.py   # Main application window
│   ├── dialogs.py       # Dialog windows
│   └── ...              # Other UI components
├── cli/                 # Command-line interface
│   └── cli.py           # Click-based CLI
└── tests/               # Unit tests (pytest)
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/scalpdf.git
cd scalpdf
pip install -e .
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=cli

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest tests/test_crypto.py  # Specific module
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking (if mypy is installed)
mypy core/ cli/
```

## 🛡️ Security

### Encryption Details
- **Algorithm**: AES-256-GCM (Authenticated encryption)
- **Key Derivation**: Argon2id with configurable parameters
- **Salt**: 32-byte random salt per document
- **Nonce**: 12-byte random nonce per encryption
- **Memory Protection**: Keys are wiped from memory after use

### Security Best Practices
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Keep encrypted files and passwords separate
- Regularly update the application
- Verify file integrity after operations

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyMuPDF**: Fast PDF rendering and text extraction
- **pikepdf**: PDF manipulation and optimization
- **PySide6**: Cross-platform GUI framework
- **cryptography**: Modern cryptographic library
- **argon2-cffi**: Secure password hashing
- **Pillow**: Image processing capabilities

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/scalpdf/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/scalpdf/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/scalpdf/discussions)

## 🗺️ Roadmap

### Planned Features
- **Digital Signatures**: PDF signing and verification
- **OCR Integration**: Text recognition for scanned PDFs
- **Form Handling**: Interactive PDF form support
- **Batch Processing**: GUI batch operations
- **Plugin System**: Extensible architecture
- **Themes**: Dark/light theme support
- **Redaction**: Secure content removal

### Version History
- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Enhanced compression and CLI improvements (planned)
- **v1.2.0**: Digital signatures and OCR support (planned)

---

**ScalPDF** - Your documents, your privacy, your control. 🔒
