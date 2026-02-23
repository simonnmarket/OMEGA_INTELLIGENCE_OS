# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T19:59:30+01:00
# AUTHOR: Cursor_Omega

"""
Cliente HTTP para captura de cotações no portal Kitco.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

import requests
from bs4 import BeautifulSoup  # type: ignore

from .Config import KITCO_URL, METALS, REQUEST_TIMEOUT_SECONDS
from .Logger import get_logger

logger = get_logger("prometheus.kitco.client")


def _parse_price(raw_value: str) -> float:
    clean = raw_value.replace(",", "").strip()
    return float(clean)


def collect_prices() -> List[Dict[str, object]]:
    """
    Coleta preços de metais no Kitco.

    Retorna lista de dicionários contendo:
    - metal
    - price
    - source
    - collected_at (UTC)
    """

    logger.info("Iniciando coleta de dados no Kitco (%s)", KITCO_URL)

    try:
        response = requests.get(KITCO_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Erro ao consultar Kitco: %s", exc)
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    collected_at = datetime.now(timezone.utc)

    results: List[Dict[str, object]] = []
    for metal in METALS:
        span_id = f"liveSpot{metal.capitalize()}"
        node = soup.find("span", {"id": span_id})
        if node is None:
            logger.warning("Elemento %s não encontrado na página.", span_id)
            continue

        value = node.get_text(strip=True)
        try:
            price = _parse_price(value)
        except ValueError:
            logger.error("Não foi possível converter preço %s para %s", value, metal)
            continue

        logger.info("✅ %s: %.2f", metal, price)
        results.append(
            {
                "metal": metal,
                "price": price,
                "source": "kitco",
                "collected_at": collected_at,
            }
        )

    return results

