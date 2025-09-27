#!/usr/bin/env python3
"""
ScalPDF Installation Test Script
Tests the installation and verifies all components work
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


def print_status(message, success=True):
    """Print status message with color."""
    symbol = "✅" if success else "❌"
    print(f"{symbol} {message}")


def test_python_version():
    """Test Python version compatibility."""
    print("🔍 Testing Python version...")
    
    version = sys.version_info
    if version >= (3, 11):
        print_status(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.11+", False)
        return False


def test_dependencies():
    """Test if all dependencies can be imported."""
    print("📦 Testing dependencies...")
    
    dependencies = [
        ("PySide6", "PySide6"),
        ("PyMuPDF", "fitz"),
        ("pikepdf", "pikepdf"),
        ("Pillow", "PIL"),
        ("cryptography", "cryptography"),
        ("argon2-cffi", "argon2"),
        ("click", "click")
    ]
    
    all_good = True
    for name, module in dependencies:
        try:
            __import__(module)
            print_status(f"{name}")
        except ImportError:
            print_status(f"{name} - Not installed", False)
            all_good = False
    
    return all_good


def test_core_modules():
    """Test ScalPDF core modules."""
    print("🔧 Testing ScalPDF core modules...")
    
    # Add parent directory to path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    modules = [
        ("Crypto", "core.crypto"),
        ("Viewer", "core.viewer"),
        ("Compress", "core.compress"),
        ("Editor", "core.editor"),
        ("Annotations", "core.annotations"),
        ("CLI", "cli.cli")
    ]
    
    all_good = True
    for name, module in modules:
        try:
            __import__(module)
            print_status(f"{name} module")
        except ImportError as e:
            print_status(f"{name} module - {e}", False)
            all_good = False
    
    return all_good


def test_gui_import():
    """Test GUI components."""
    print("🖥️  Testing GUI components...")
    
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    try:
        import ui.main_window
        print_status("GUI components")
        return True
    except ImportError as e:
        print_status(f"GUI components - {e}", False)
        return False


def test_crypto_functionality():
    """Test basic crypto functionality."""
    print("🔐 Testing encryption functionality...")
    
    try:
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from core.crypto import PDFCrypto
        
        crypto = PDFCrypto()
        test_data = b"Test PDF data for encryption"
        password = "test_password_123"
        
        # Test encryption
        encrypted_data, salt, nonce = crypto.encrypt_pdf(test_data, password)
        print_status("PDF encryption")
        
        # Test decryption
        decrypted_data = crypto.decrypt_pdf(encrypted_data, password, salt, nonce)
        
        if decrypted_data == test_data:
            print_status("PDF decryption")
            return True
        else:
            print_status("PDF decryption - Data mismatch", False)
            return False
            
    except Exception as e:
        print_status(f"Encryption test - {e}", False)
        return False


def test_cli_functionality():
    """Test CLI functionality."""
    print("💻 Testing CLI functionality...")
    
    try:
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from cli.cli import cli
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        if result.exit_code == 0 and "ScalPDF" in result.output:
            print_status("CLI interface")
            return True
        else:
            print_status("CLI interface - Help command failed", False)
            return False
            
    except Exception as e:
        print_status(f"CLI test - {e}", False)
        return False


def test_installation_paths():
    """Test if installation paths exist (for installed version)."""
    print("📁 Testing installation paths...")
    
    system = platform.system().lower()
    
    if system == "linux":
        paths = [
            Path.home() / ".local/share/scalpdf",
            Path.home() / ".local/bin/scalpdf",
            Path.home() / ".local/bin/scalpdf-cli",
            Path.home() / ".local/share/applications/scalpdf.desktop"
        ]
    elif system == "windows":
        paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "ScalPDF",
            Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs/ScalPDF.lnk"
        ]
    else:
        print_status("Installation paths - Unsupported platform", False)
        return False
    
    all_exist = True
    for path in paths:
        if path.exists():
            print_status(f"Found: {path}")
        else:
            print_status(f"Missing: {path}", False)
            all_exist = False
    
    return all_exist


def main():
    """Main test function."""
    print("🧪 ScalPDF Installation Test")
    print("=" * 40)
    print()
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Core Modules", test_core_modules),
        ("GUI Components", test_gui_import),
        ("Crypto Functionality", test_crypto_functionality),
        ("CLI Functionality", test_cli_functionality),
    ]
    
    # Only test installation paths if not in development directory
    if not (Path.cwd() / "main.py").exists():
        tests.append(("Installation Paths", test_installation_paths))
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test failed with exception: {e}", False)
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✅" if result else "❌"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! ScalPDF is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
