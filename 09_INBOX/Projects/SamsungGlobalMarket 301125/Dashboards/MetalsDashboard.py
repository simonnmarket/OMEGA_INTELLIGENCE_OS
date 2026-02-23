# MEMORY_ID: TASK_SENTIMENT_DASHBOARD
# TIMESTAMP: 2025-11-09T21:40:00+01:00
# AUTHOR: Cursor_Omega

"""
Dashboard Streamlit para acompanhamento dos metais.
"""

from __future__ import annotations

import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import streamlit as st  # type: ignore

from Core.Database import DataPoint, get_engine
from Core.Feeds.News import collect_news_with_sentiment


def load_data() -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(DataPoint.__table__.select(), conn)
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def render():
    st.set_page_config(page_title="Prometheus Metals Dashboard", layout="wide")
    st.title("Prometheus Metals Dashboard")

    df = load_data()
    if df.empty:
        st.warning("Nenhum dado disponível. Execute o Core para coletar registros.")
        return

    metals = sorted(df["metal"].dropna().unique())
    selected_metals = st.multiselect("Metais", metals, default=metals[:3])

    filtered = df[df["metal"].isin(selected_metals)]
    if filtered.empty:
        st.info("Selecione ao menos um metal com dados.")
        return

    fig = px.line(filtered, x="timestamp", y="price", color="metal", title="Histórico de preços")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Últimas notícias e sentimento")
    news = collect_news_with_sentiment()
    if not news:
        st.info("Coleta de notícias desabilitada ou sem resultados recentes.")
    else:
        for article in news:
            sentiment = article["sentiment"]
            st.write(f"**{article['title']}** ({article['published_at']})")
            st.write(article["description"])
            st.write(f"Sentimento: {sentiment}")
            st.write(f"[Link]({article['url']})")
            st.markdown("---")


if __name__ == "__main__":
    render()

