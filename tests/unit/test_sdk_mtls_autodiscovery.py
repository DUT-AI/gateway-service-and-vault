from pathlib import Path

import httpx
import pytest
from dut_vault_sdk.client import VaultClient, resolve_mtls_cert


def test_resolve_mtls_cert_from_default_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    monkeypatch.delenv("SSL_KEY_FILE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert resolve_mtls_cert() is None

    dut_dir = tmp_path / ".dut-vault"
    dut_dir.mkdir()
    crt = dut_dir / "client.crt"
    key = dut_dir / "client.key"
    crt.write_text("CERT")
    key.write_text("KEY")

    assert resolve_mtls_cert() == (str(crt), str(key))


def test_vault_client_gateway_client_injects_headers_and_base_url(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    monkeypatch.delenv("SSL_KEY_FILE", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setenv("X_VIRTUAL_KEY", "vk_test_123")

    vault = VaultClient(base_url="https://gateway.dutai.io.vn/")

    sync_client = vault.gateway_client("llm", timeout=15.0)
    try:
        assert isinstance(sync_client, httpx.Client)
        assert str(sync_client.base_url) == "https://gateway.dutai.io.vn/services/llm/"
        assert sync_client.headers["X-Virtual-Key"] == "vk_test_123"
    finally:
        sync_client.close()

    async_client = vault.async_gateway_client("llm")
    assert isinstance(async_client, httpx.AsyncClient)
    assert str(async_client.base_url) == "https://gateway.dutai.io.vn/services/llm/"
    assert async_client.headers["X-Virtual-Key"] == "vk_test_123"
