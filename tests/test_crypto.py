"""
Tests for ScalPDF cryptography module
"""

import pytest
import tempfile
from pathlib import Path
import secrets

from core.crypto import PDFCrypto


class TestPDFCrypto:
    """Test cases for PDF encryption and decryption."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.crypto = PDFCrypto()
        self.test_password = "test_password_123!"
        self.test_data = b"This is test PDF data for encryption testing."
    
    def test_encrypt_decrypt_data(self):
        """Test basic encryption and decryption of data."""
        # Encrypt data
        encrypted_data, salt, nonce = self.crypto.encrypt_pdf(self.test_data, self.test_password)
        
        # Verify encrypted data is different
        assert encrypted_data != self.test_data
        assert len(salt) == self.crypto.SALT_LENGTH
        assert len(nonce) == self.crypto.NONCE_LENGTH
        
        # Decrypt data
        decrypted_data = self.crypto.decrypt_pdf(encrypted_data, self.test_password, salt, nonce)
        
        # Verify decrypted data matches original
        assert decrypted_data == self.test_data
    
    def test_encrypt_decrypt_file(self):
        """Test file encryption and decryption."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file
            input_file = temp_path / "test_input.pdf"
            input_file.write_bytes(self.test_data)
            
            # Encrypt file
            encrypted_file = temp_path / "test_encrypted.scalpdf"
            self.crypto.encrypt_file(input_file, encrypted_file, self.test_password)
            
            # Verify encrypted file exists and is different
            assert encrypted_file.exists()
            assert encrypted_file.read_bytes() != self.test_data
            
            # Decrypt file
            decrypted_file = temp_path / "test_decrypted.pdf"
            self.crypto.decrypt_file(encrypted_file, decrypted_file, self.test_password)
            
            # Verify decrypted file matches original
            assert decrypted_file.exists()
            assert decrypted_file.read_bytes() == self.test_data
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails decryption."""
        encrypted_data, salt, nonce = self.crypto.encrypt_pdf(self.test_data, self.test_password)
        
        with pytest.raises(ValueError, match="Decryption failed"):
            self.crypto.decrypt_pdf(encrypted_data, "wrong_password", salt, nonce)
    
    def test_is_encrypted_file(self):
        """Test encrypted file detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create and encrypt test file
            input_file = temp_path / "test.pdf"
            input_file.write_bytes(self.test_data)
            
            encrypted_file = temp_path / "test.scalpdf"
            self.crypto.encrypt_file(input_file, encrypted_file, self.test_password)
            
            # Test detection
            assert self.crypto.is_encrypted_file(encrypted_file) is True
            assert self.crypto.is_encrypted_file(input_file) is False
    
    def test_password_strength_checker(self):
        """Test password strength checking."""
        # Weak password
        score, desc = self.crypto.check_password_strength("123")
        assert score < 40
        assert "Weak" in desc
        
        # Strong password
        score, desc = self.crypto.check_password_strength("MyStr0ng!P@ssw0rd123")
        assert score >= 80
        assert "Strong" in desc
    
    def test_generate_strong_password(self):
        """Test strong password generation."""
        password = self.crypto.generate_strong_password(16)
        
        assert len(password) == 16
        
        # Check strength
        score, _ = self.crypto.check_password_strength(password)
        assert score >= 80
    
    def test_different_salts_produce_different_ciphertexts(self):
        """Test that same data with different salts produces different ciphertexts."""
        encrypted1, salt1, nonce1 = self.crypto.encrypt_pdf(self.test_data, self.test_password)
        encrypted2, salt2, nonce2 = self.crypto.encrypt_pdf(self.test_data, self.test_password)
        
        # Salts and nonces should be different
        assert salt1 != salt2
        assert nonce1 != nonce2
        
        # Encrypted data should be different
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same original data
        decrypted1 = self.crypto.decrypt_pdf(encrypted1, self.test_password, salt1, nonce1)
        decrypted2 = self.crypto.decrypt_pdf(encrypted2, self.test_password, salt2, nonce2)
        
        assert decrypted1 == self.test_data
        assert decrypted2 == self.test_data
    
    def test_large_data_encryption(self):
        """Test encryption of larger data."""
        # Create 1MB of test data
        large_data = secrets.token_bytes(1024 * 1024)
        
        encrypted_data, salt, nonce = self.crypto.encrypt_pdf(large_data, self.test_password)
        decrypted_data = self.crypto.decrypt_pdf(encrypted_data, self.test_password, salt, nonce)
        
        assert decrypted_data == large_data
    
    def test_empty_data_encryption(self):
        """Test encryption of empty data."""
        empty_data = b""
        
        encrypted_data, salt, nonce = self.crypto.encrypt_pdf(empty_data, self.test_password)
        decrypted_data = self.crypto.decrypt_pdf(encrypted_data, self.test_password, salt, nonce)
        
        assert decrypted_data == empty_data
    
    def test_unicode_password(self):
        """Test encryption with unicode password."""
        unicode_password = "пароль_测试_🔒"
        
        encrypted_data, salt, nonce = self.crypto.encrypt_pdf(self.test_data, unicode_password)
        decrypted_data = self.crypto.decrypt_pdf(encrypted_data, unicode_password, salt, nonce)
        
        assert decrypted_data == self.test_data
