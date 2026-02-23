# MEMORY_ID: TASK_FOREX_MODULE
# TIMESTAMP: 2025-11-09T22:20:00+01:00
# AUTHOR: Cursor_Omega

"""
Testes para ForexClient.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

import pytest  # type: ignore

from Modules.Forex.ForexClient import ForexClient


class DummyResponse:
    def __init__(self, status_code: int, payload: Dict):
        self.status_code = status_code
        self.payload = payload

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")

    def json(self):
        return self.payload


def test_forex_client_coleta(monkeypatch):
    payload = {
        "prices": [
            {
                "instrument": "EUR_USD",
                "bids": [{"price": "1.09500"}],
                "asks": [{"price": "1.09520"}],
            }
        ]
    }

    def fake_get(url, headers=None, params=None, timeout=5):
        return DummyResponse(200, payload)

    monkeypatch.setattr("Modules.Forex.ForexClient.requests.get", fake_get)

    client = ForexClient(
        {
            "api_url": "https://api.example.com/accounts/{account_id}/pricing",
            "account_id": "123",
            "api_token": "TOKEN",
            "instruments": ["EUR_USD"],
        }
    )
    dados = list(client.coletar_dados())

    assert len(dados) == 1
    entry = dados[0]
    assert entry["metal"] == "EUR_USD"
    assert entry["preco"] == pytest.approx((1.09500 + 1.09520) / 2)
    assert entry["bid"] == pytest.approx(1.09500)
    assert entry["ask"] == pytest.approx(1.09520)
    assert isinstance(entry["collected_at"], datetime)
    assert entry["collected_at"].tzinfo == timezone.utc


def test_forex_client_credenciais_invalidas():
    with pytest.raises(ValueError):
        ForexClient({"api_url": "https://url.com", "account_id": "", "api_token": ""})

