# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 2025-11-09T20:01:00+01:00
# AUTHOR: Cursor_Omega

"""
Dashboard Streamlit para visualização das cotações Kitco.
"""

from __future__ import annotations

import pandas as pd  # type: ignore
import streamlit as st  # type: ignore

from .Repository import engine


def render_dashboard(limit: int = 200) -> None:
    st.title("Painel de Metais Preciosos - Kitco")
    query = f"""
        SELECT metal, price, source, collected_at
        FROM metal_prices
        ORDER BY collected_at DESC
        LIMIT {limit}
    """

    df = pd.read_sql_query(query, engine)
    if df.empty:
        st.info("Nenhum dado disponível.")
        return

    st.dataframe(df)
    df["collected_at"] = pd.to_datetime(df["collected_at"])
    grouped = df.groupby(["collected_at", "metal"])["price"].mean().reset_index()
    pivot = grouped.pivot(index="collected_at", columns="metal", values="price")
    st.line_chart(pivot)

