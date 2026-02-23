# MEMORY_ID: TASK_METALS_ADAPTER
# TIMESTAMP: 2025-11-09T21:29:00+01:00
# AUTHOR: Cursor_Omega

"""
Testes para o MetalsClient.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import pytest  # type: ignore

from Modules.Metals.MetalsClient import MetalsClient


class DummyService:
    def __init__(self, prices: List[dict]):
        self.prices = prices
        self.called = 0

    def run_collection_cycle(self) -> List[dict]:
        self.called += 1
        return self.prices


def test_metals_client_coletar_dados(monkeypatch):
    fake_prices = [
        {
            "metal": "gold",
            "price": 2100.5,
            "source": "kitco",
            "collected_at": datetime.now(timezone.utc),
        }
    ]

    dummy = DummyService(fake_prices)
    monkeypatch.setattr(
        "Modules.Metals.MetalsClient.MetalsKitcoService",
        lambda alert_limits: dummy,
    )

    client = MetalsClient({"alert_limits": {"gold": 2000}})
    dados = list(client.coletar_dados())

    assert dummy.called == 1
    assert len(dados) == 1
    assert dados[0]["metal"] == "gold"
    assert dados[0]["preco"] == 2100.5
    assert "collected_at" in dados[0]


def test_metals_client_usa_alert_limits_default(monkeypatch):
    dummy = DummyService([])
    monkeypatch.setattr(
        "Modules.Metals.MetalsClient.MetalsKitcoService",
        lambda alert_limits: dummy,
    )

    client = MetalsClient({})
    list(client.coletar_dados())

    assert dummy.called == 1

