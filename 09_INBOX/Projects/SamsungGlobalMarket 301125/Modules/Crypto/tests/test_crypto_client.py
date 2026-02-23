# MEMORY_ID: TASK_CRYPTO_MODULE
# TIMESTAMP: 2025-11-09T22:07:00+01:00
# AUTHOR: Cursor_Omega

"""
Testes para CryptoClient.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import pytest  # type: ignore

from Modules.Crypto.CryptoClient import CryptoClient


class DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")

    def json(self):
        return self.payload


def test_crypto_client_coleta(monkeypatch):
    payloads = {
        "BTCUSDT": {"symbol": "BTCUSDT", "price": "68000.50"},
        "ETHUSDT": {"symbol": "ETHUSDT", "price": "3200.10"},
    }

    def fake_get(url, params=None, timeout=5):
        symbol = params["symbol"]
        return DummyResponse(200, payloads[symbol])

    monkeypatch.setattr("Modules.Crypto.CryptoClient.requests.get", fake_get)

    client = CryptoClient({"symbols": ["BTCUSDT", "ETHUSDT"]})
    dados = list(client.coletar_dados())

    assert len(dados) == 2
    assert dados[0]["metal"] == "BTCUSDT"
    assert dados[0]["preco"] == pytest.approx(68000.50)
    assert isinstance(dados[0]["collected_at"], datetime)
    assert dados[0]["collected_at"].tzinfo == timezone.utc


def test_crypto_client_trata_erros(monkeypatch):
    def fake_get(url, params=None, timeout=5):
        raise requests.RequestException("Timeout")

    monkeypatch.setattr("Modules.Crypto.CryptoClient.requests.get", fake_get)

    client = CryptoClient({"symbols": ["BTCUSDT"]})
    dados = list(client.coletar_dados())

    assert dados == []

