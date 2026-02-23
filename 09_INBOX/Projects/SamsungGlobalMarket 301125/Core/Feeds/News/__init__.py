# MEMORY_ID: TASK_SENTIMENT_DASHBOARD
# TIMESTAMP: 2025-11-09T21:39:30+01:00
# AUTHOR: Cursor_Omega

"""
Pipeline de notícias e sentimento.
"""

from .NewsSentimentPipeline import collect_news_with_sentiment

__all__ = ["collect_news_with_sentiment"]

