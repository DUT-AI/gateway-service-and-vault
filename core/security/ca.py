"""Internal Private Certificate Authority (x509 PKI) for mTLS Client Identity."""

import hashlib
from datetime import UTC, datetime, timedelta
from typing import NamedTuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class IssuedCertificate(NamedTuple):
    cert_pem: str
    key_pem: str
    fingerprint: str
    serial: str
    expires_at: datetime


class PrivateCA:
    """In-memory or persistent x509 Root CA for issuing mTLS client certificates."""

    def __init__(
        self,
        ca_cert_pem: str | None = None,
        ca_key_pem: str | None = None,
    ) -> None:
        if ca_cert_pem and ca_key_pem:
            self.ca_key = serialization.load_pem_private_key(
                ca_key_pem.encode("utf-8"),
                password=None,
            )
            self.ca_cert = x509.load_pem_x509_certificate(ca_cert_pem.encode("utf-8"))
        else:
            self.ca_key, self.ca_cert = self._generate_root_ca()

    @staticmethod
    def _generate_root_ca() -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
        """Generate a self-signed Root CA certificate and private key."""
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DUT AI Gateway"),
                x509.NameAttribute(NameOID.COMMON_NAME, "DUT AI Internal Root CA"),
            ]
        )
        now = datetime.now(UTC)
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=3650))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=True,
                    crl_sign=True,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(key, hashes.SHA256())
        )
        return key, cert

    @property
    def ca_cert_pem(self) -> str:
        return self.ca_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

    @property
    def ca_key_pem(self) -> str:
        return self.ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

    def issue_client_certificate(
        self,
        common_name: str,
        validity_days: int = 30,
    ) -> IssuedCertificate:
        """Issue a client x509 certificate signed by this CA for mTLS."""
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DUT AI Gateway Client"),
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ]
        )
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=validity_days)
        serial_number = x509.random_serial_number()

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.ca_cert.subject)
            .public_key(client_key.public_key())
            .serial_number(serial_number)
            .not_valid_before(now)
            .not_valid_after(expires_at)
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
                critical=False,
            )
            .sign(self.ca_key, hashes.SHA256())
        )

        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        key_pem = client_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        fingerprint = cert.fingerprint(hashes.SHA256()).hex()

        return IssuedCertificate(
            cert_pem=cert_pem,
            key_pem=key_pem,
            fingerprint=fingerprint,
            serial=str(serial_number),
            expires_at=expires_at,
        )

    @staticmethod
    def compute_cert_fingerprint(cert_pem: str) -> str:
        """Compute SHA-256 fingerprint from a PEM certificate string."""
        cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
        return cert.fingerprint(hashes.SHA256()).hex()

    @staticmethod
    def hash_virtual_key(virtual_key: str) -> str:
        """Hash a virtual key using SHA-256 for secure storage."""
        return hashlib.sha256(virtual_key.encode("utf-8")).hexdigest()
