"""
ScalPDF Cryptography Module
Handles AES-256-GCM encryption/decryption with Argon2id key derivation
"""

import os
import secrets
from typing import Tuple, Optional
from pathlib import Path
import gc

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class PDFCrypto:
    """Handles PDF encryption and decryption using AES-256-GCM with Argon2id."""
    
    # Argon2id parameters (secure defaults)
    ARGON2_TIME_COST = 3
    ARGON2_MEMORY_COST = 65536  # 64MB
    ARGON2_PARALLELISM = 1
    SALT_LENGTH = 32
    KEY_LENGTH = 32  # 256 bits for AES-256
    NONCE_LENGTH = 12  # 96 bits for GCM
    
    def __init__(self):
        """Initialize the crypto handler."""
        self.ph = PasswordHasher(
            time_cost=self.ARGON2_TIME_COST,
            memory_cost=self.ARGON2_MEMORY_COST,
            parallelism=self.ARGON2_PARALLELISM,
            hash_len=self.KEY_LENGTH,
            salt_len=self.SALT_LENGTH
        )
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using Argon2id.
        
        Args:
            password: User password
            salt: Unique salt for this document
            
        Returns:
            32-byte encryption key
        """
        try:
            # Use Argon2id for key derivation
            key = self.ph.hash(password, salt=salt)
            # Extract the raw hash (key) from the encoded result
            return self.ph.verify(key, password, salt=salt)
        except Exception:
            # Fallback: use the password hasher directly
            import argon2
            return argon2.hash_password_raw(
                password.encode('utf-8'),
                salt,
                time_cost=self.ARGON2_TIME_COST,
                memory_cost=self.ARGON2_MEMORY_COST,
                parallelism=self.ARGON2_PARALLELISM,
                hash_len=self.KEY_LENGTH,
                type=argon2.Type.ID
            )
    
    def encrypt_pdf(self, pdf_data: bytes, password: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt PDF data using AES-256-GCM.
        
        Args:
            pdf_data: Raw PDF file data
            password: Encryption password
            
        Returns:
            Tuple of (encrypted_data, salt, nonce)
        """
        # Generate random salt and nonce
        salt = secrets.token_bytes(self.SALT_LENGTH)
        nonce = secrets.token_bytes(self.NONCE_LENGTH)
        
        # Derive key from password
        key = self._derive_key(password, salt)
        
        try:
            # Encrypt using AES-256-GCM
            aesgcm = AESGCM(key)
            encrypted_data = aesgcm.encrypt(nonce, pdf_data, None)
            
            return encrypted_data, salt, nonce
        finally:
            # Securely wipe key from memory
            self._wipe_memory(key)
    
    def decrypt_pdf(self, encrypted_data: bytes, password: str, salt: bytes, nonce: bytes) -> bytes:
        """
        Decrypt PDF data using AES-256-GCM.
        
        Args:
            encrypted_data: Encrypted PDF data
            password: Decryption password
            salt: Salt used during encryption
            nonce: Nonce used during encryption
            
        Returns:
            Decrypted PDF data
            
        Raises:
            ValueError: If decryption fails (wrong password or corrupted data)
        """
        # Derive key from password
        key = self._derive_key(password, salt)
        
        try:
            # Decrypt using AES-256-GCM
            aesgcm = AESGCM(key)
            decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
            
            return decrypted_data
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
        finally:
            # Securely wipe key from memory
            self._wipe_memory(key)
    
    def encrypt_file(self, input_path: Path, output_path: Path, password: str) -> None:
        """
        Encrypt a PDF file and save to disk.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to save encrypted file
            password: Encryption password
        """
        # Read PDF data
        with open(input_path, 'rb') as f:
            pdf_data = f.read()
        
        # Encrypt
        encrypted_data, salt, nonce = self.encrypt_pdf(pdf_data, password)
        
        # Create encrypted file format:
        # [MAGIC_HEADER][SALT][NONCE][ENCRYPTED_DATA]
        magic_header = b'SCALPDF_ENC_V1'
        
        with open(output_path, 'wb') as f:
            f.write(magic_header)
            f.write(salt)
            f.write(nonce)
            f.write(encrypted_data)
    
    def decrypt_file(self, input_path: Path, output_path: Path, password: str) -> None:
        """
        Decrypt a PDF file and save to disk.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to save decrypted PDF
            password: Decryption password
        """
        with open(input_path, 'rb') as f:
            # Read and verify magic header
            magic_header = f.read(14)  # len('SCALPDF_ENC_V1')
            if magic_header != b'SCALPDF_ENC_V1':
                raise ValueError("Invalid encrypted file format")
            
            # Read salt and nonce
            salt = f.read(self.SALT_LENGTH)
            nonce = f.read(self.NONCE_LENGTH)
            
            # Read encrypted data
            encrypted_data = f.read()
        
        # Decrypt
        decrypted_data = self.decrypt_pdf(encrypted_data, password, salt, nonce)
        
        # Save decrypted PDF
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
    
    def is_encrypted_file(self, file_path: Path) -> bool:
        """
        Check if a file is encrypted by ScalPDF.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is encrypted by ScalPDF
        """
        try:
            with open(file_path, 'rb') as f:
                magic_header = f.read(14)
                return magic_header == b'SCALPDF_ENC_V1'
        except (IOError, OSError):
            return False
    
    @staticmethod
    def _wipe_memory(data: bytes) -> None:
        """
        Attempt to securely wipe sensitive data from memory.
        
        Args:
            data: Bytes to wipe
        """
        if isinstance(data, bytes):
            # Overwrite with random data
            try:
                import ctypes
                ctypes.memset(id(data) + 20, 0, len(data))  # Python bytes object offset
            except:
                pass  # Best effort
        
        # Force garbage collection
        gc.collect()
    
    def generate_strong_password(self, length: int = 32) -> str:
        """
        Generate a cryptographically strong password.
        
        Args:
            length: Password length (default 32)
            
        Returns:
            Strong random password
        """
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def check_password_strength(self, password: str) -> Tuple[int, str]:
        """
        Check password strength.
        
        Args:
            password: Password to check
            
        Returns:
            Tuple of (strength_score_0_to_100, description)
        """
        score = 0
        feedback = []
        
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        else:
            feedback.append("Use at least 8 characters")
        
        if any(c.islower() for c in password):
            score += 15
        else:
            feedback.append("Add lowercase letters")
        
        if any(c.isupper() for c in password):
            score += 15
        else:
            feedback.append("Add uppercase letters")
        
        if any(c.isdigit() for c in password):
            score += 15
        else:
            feedback.append("Add numbers")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 20
        else:
            feedback.append("Add special characters")
        
        if len(set(password)) > len(password) * 0.7:
            score += 10
        else:
            feedback.append("Avoid repeated characters")
        
        if score >= 80:
            description = "Strong"
        elif score >= 60:
            description = "Good"
        elif score >= 40:
            description = "Fair"
        else:
            description = "Weak"
        
        if feedback:
            description += f" - {', '.join(feedback)}"
        
        return min(score, 100), description
