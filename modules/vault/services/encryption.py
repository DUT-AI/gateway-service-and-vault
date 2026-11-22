"""AES-256-GCM Authenticated Encryption Service for Vault Secrets."""

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class VaultEncryptionService:
    """Provides hardware-accelerated AES-256-GCM authenticated encryption."""

    def __init__(self, master_key: str) -> None:
        # Derive a deterministic 32-byte (256-bit) key from the master secret
        self._key = hashlib.sha256(master_key.encode("utf-8")).digest()
        self._aesgcm = AESGCM(self._key)

    def encrypt(
        self, plaintext: str, associated_data: str = ""
    ) -> tuple[str, str, str]:
        """Encrypt plaintext using AES-256-GCM.

        Returns:
            tuple of (ciphertext_b64, nonce_b64, auth_tag_b64)
        """
        nonce = os.urandom(12)  # 96-bit standard nonce for GCM
        ad = associated_data.encode("utf-8") if associated_data else None
        encrypted_bytes = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), ad)

        # In cryptography AESGCM, the 16-byte tag is appended to the end of ciphertext
        ciphertext = encrypted_bytes[:-16]
        auth_tag = encrypted_bytes[-16:]

        return (
            base64.b64encode(ciphertext).decode("utf-8"),
            base64.b64encode(nonce).decode("utf-8"),
            base64.b64encode(auth_tag).decode("utf-8"),
        )

    def decrypt(
        self,
        ciphertext_b64: str,
        nonce_b64: str,
        auth_tag_b64: str,
        associated_data: str = "",
    ) -> str:
        """Decrypt AES-256-GCM ciphertext and verify authentication tag.

        Raises:
            cryptography.exceptions.InvalidTag: If data has been tampered with.
        """
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        auth_tag = base64.b64decode(auth_tag_b64)
        ad = associated_data.encode("utf-8") if associated_data else None

        # Recombine ciphertext + 16-byte tag
        payload = ciphertext + auth_tag
        decrypted_bytes = self._aesgcm.decrypt(nonce, payload, ad)
        return decrypted_bytes.decode("utf-8")
