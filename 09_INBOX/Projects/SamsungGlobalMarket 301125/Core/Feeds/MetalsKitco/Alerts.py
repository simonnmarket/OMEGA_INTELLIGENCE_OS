# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T20:00:30+01:00
# AUTHOR: Cursor_Omega

"""
Alertas para preços de metais coletados.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from .Logger import get_logger

logger = get_logger("prometheus.kitco.alerts")


def check_price_alerts(
    prices: Iterable[dict],
    limits: Dict[str, float],
) -> List[dict]:
    """
    Avalia preços e dispara alertas quando superar limites.
    Retorna lista dos preços que ultrapassaram limites.
    """

    triggered: List[dict] = []
    for item in prices:
        metal = item.get("metal")
        price = item.get("price")
        if metal is None or price is None:
            continue

        limit = limits.get(metal)
        if limit is None:
            continue

        if price > limit:
            logger.warning(
                "ALERTA: %s com preço %.2f acima do limite %.2f",
                metal,
                price,
                limit,
            )
            triggered.append(item)

    if triggered:
        logger.info("Total de alertas acionados: %d", len(triggered))

    return triggered

