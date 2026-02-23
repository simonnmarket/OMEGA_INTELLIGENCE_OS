# MEMORY_ID: TASK_ML_SETUP
# TIMESTAMP: 2025-11-09T21:38:00+01:00
# AUTHOR: Cursor_Omega

"""
Preparação de dados históricos para modelos de ML.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd  # type: ignore

from Core.Database import DataPoint, get_engine


def export_timeseries(symbol: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> pd.DataFrame:
    """
    Exporta série temporal de preços para um símbolo específico.
    """

    engine = get_engine()
    query = (
        DataPoint.__table__.select()
        .where(DataPoint.metal == symbol)
        .order_by(DataPoint.timestamp.asc())
    )
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if start:
        df = df[df["timestamp"] >= start]
    if end:
        df = df[df["timestamp"] <= end]

    df.set_index("timestamp", inplace=True)
    df.rename(columns={"price": "close"}, inplace=True)
    return df[["close"]]


def save_timeseries_csv(symbol: str, output_path: str) -> str:
    """
    Salva a série temporal em CSV e retorna o caminho.
    """

    df = export_timeseries(symbol)
    if df.empty:
        raise ValueError(f"Nenhum dado encontrado para {symbol}.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output)
    return str(output)

