"""Internal Private Certificate Authority (x509 PKI) for mTLS Client Identity."""

import base64
import contextlib
import hashlib
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import NamedTuple

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

DEFAULT_CERTS_DIR = (
    Path(__file__).resolve().parent.parent.parent / "apps" / "apisix" / "conf" / "certs"
)


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
        ca_cert_path: Path | str | None = None,
        ca_key_path: Path | str | None = None,
        auto_persist: bool = True,
    ) -> None:
        if ca_cert_pem and ca_key_pem:
            self.ca_key = serialization.load_pem_private_key(
                ca_key_pem.encode("utf-8"),
                password=None,
            )
            self.ca_cert = x509.load_pem_x509_certificate(ca_cert_pem.encode("utf-8"))
            return

        cert_file = (
            Path(ca_cert_path) if ca_cert_path else (DEFAULT_CERTS_DIR / "ca.crt")
        )
        key_file = Path(ca_key_path) if ca_key_path else (DEFAULT_CERTS_DIR / "ca.key")

        if auto_persist and cert_file.exists() and key_file.exists():
            self.ca_key = serialization.load_pem_private_key(
                key_file.read_bytes(),
                password=None,
            )
            self.ca_cert = x509.load_pem_x509_certificate(cert_file.read_bytes())
        else:
            self.ca_key, self.ca_cert = self._generate_root_ca()
            if auto_persist:
                with contextlib.suppress(OSError):
                    cert_file.parent.mkdir(parents=True, exist_ok=True)
                    cert_file.write_text(self.ca_cert_pem, encoding="utf-8")
                    key_file.write_text(self.ca_key_pem, encoding="utf-8")

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

    def issue_server_certificate(
        self,
        sans: list[str],
        validity_days: int = 365,
    ) -> IssuedCertificate:
        """Issue an SSL server certificate with SANs (Subject Alternative Names) for APISIX."""
        import ipaddress

        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DUT AI Gateway"),
                x509.NameAttribute(
                    NameOID.COMMON_NAME, sans[0] if sans else "localhost"
                ),
            ]
        )
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=validity_days)
        serial_number = x509.random_serial_number()

        san_list = []
        for san in sans:
            try:
                ip = ipaddress.ip_address(san)
                san_list.append(x509.IPAddress(ip))
            except ValueError:
                san_list.append(x509.DNSName(san))

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.ca_cert.subject)
            .public_key(server_key.public_key())
            .serial_number(serial_number)
            .not_valid_before(now)
            .not_valid_after(expires_at)
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            )
            .sign(self.ca_key, hashes.SHA256())
        )

        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
        key_pem = server_key.private_bytes(
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

    def get_or_create_server_certificate(
        self,
        sans: list[str] | None = None,
        server_cert_path: Path | str | None = None,
        server_key_path: Path | str | None = None,
    ) -> IssuedCertificate:
        """Load or create persistent server SSL certificate for APISIX."""
        sans = sans or ["localhost", "127.0.0.1", "apisix", "gateway"]
        cert_file = (
            Path(server_cert_path)
            if server_cert_path
            else (DEFAULT_CERTS_DIR / "server.crt")
        )
        key_file = (
            Path(server_key_path)
            if server_key_path
            else (DEFAULT_CERTS_DIR / "server.key")
        )

        if cert_file.exists() and key_file.exists():
            with contextlib.suppress(Exception):
                cert_pem = cert_file.read_text(encoding="utf-8")
                key_pem = key_file.read_text(encoding="utf-8")
                fingerprint = self.compute_cert_fingerprint(cert_pem)
                return IssuedCertificate(
                    cert_pem=cert_pem,
                    key_pem=key_pem,
                    fingerprint=fingerprint,
                    serial="",
                    expires_at=datetime.now(UTC) + timedelta(days=365),
                )

        issued = self.issue_server_certificate(sans=sans)
        with contextlib.suppress(OSError):
            cert_file.parent.mkdir(parents=True, exist_ok=True)
            cert_file.write_text(issued.cert_pem, encoding="utf-8")
            key_file.write_text(issued.key_pem, encoding="utf-8")
        return issued

    @staticmethod
    def compute_cert_fingerprint(cert_pem: str) -> str:
        """Compute SHA-256 fingerprint from a PEM certificate string."""
        cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
        return cert.fingerprint(hashes.SHA256()).hex()

    @staticmethod
    def hash_virtual_key(virtual_key: str) -> str:
        """Hash a virtual key using SHA-256 for secure storage."""
        return hashlib.sha256(virtual_key.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_client_signature(
        cert_pem: str,
        signature_b64: str,
        timestamp: str,
        method: str,
        path: str,
        max_skew_seconds: int = 300,
    ) -> bool:
        """Verify HTTP-layer Proof-of-Possession signature signed by client.key."""
        try:
            ts = int(timestamp)
        except (TypeError, ValueError):
            return False

        if abs(int(time.time()) - ts) > max_skew_seconds:
            return False

        try:
            cert = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
            public_key = cert.public_key()
            if not isinstance(public_key, rsa.RSAPublicKey):
                return False
            signature = base64.b64decode(signature_b64, validate=True)
            payload = f"{ts}:{method.upper()}:{path}".encode()
            public_key.verify(
                signature,
                payload,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False
