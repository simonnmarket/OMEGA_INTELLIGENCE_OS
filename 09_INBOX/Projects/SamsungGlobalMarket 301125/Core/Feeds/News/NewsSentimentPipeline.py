# MEMORY_ID: TASK_SENTIMENT_DASHBOARD
# TIMESTAMP: 2025-11-09T21:39:00+01:00
# AUTHOR: Cursor_Omega

"""
Pipeline de notícias e análise de sentimento para metais.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore

from Core.Config import ConfigManager
from Core.Logger import get_logger

logger = get_logger("prometheus.news_pipeline")
analyzer = SentimentIntensityAnalyzer()


def fetch_news() -> List[Dict]:
    cfg = ConfigManager.get_instance()
    news_cfg = cfg.get("news", default={})
    if not news_cfg or not news_cfg.get("enabled"):
        logger.info("Coleta de notícias desabilitada.")
        return []

    params = {
        "q": news_cfg.get("query", "gold"),
        "apiKey": news_cfg.get("api_key"),
        "language": "en",
        "pageSize": 20,
        "sortBy": "publishedAt",
    }
    endpoint = news_cfg.get("endpoint", "https://newsapi.org/v2/everything")

    try:
        response = requests.get(endpoint, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as exc:
        logger.warning("Falha ao coletar notícias: %s", exc)
        return []


def enrich_with_sentiment(articles: List[Dict]) -> List[Dict]:
    enriched: List[Dict] = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        text = f"{title}. {description}"
        sentiment = analyzer.polarity_scores(text)
        enriched.append(
            {
                "title": title,
                "description": description,
                "published_at": article.get("publishedAt"),
                "url": article.get("url"),
                "sentiment": sentiment,
            }
        )
    return enriched


def collect_news_with_sentiment() -> List[Dict]:
    articles = fetch_news()
    if not articles:
        return []
    return enrich_with_sentiment(articles)

