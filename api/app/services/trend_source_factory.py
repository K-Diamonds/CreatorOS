from __future__ import annotations

from agents.trend_research import MockTrendDataSource, TrendDataSource
from agents.trend_sources.rss import RssTrendDataSource

from app.core.config import Settings


def build_trend_data_source(settings: Settings) -> TrendDataSource:
    mode = settings.trend_data_source.strip().lower()
    if mode == "mock":
        return MockTrendDataSource()

    rss_urls = settings.trend_rss_feed_urls
    if mode in {"rss", "auto"} and rss_urls:
        return RssTrendDataSource(rss_urls)

    return MockTrendDataSource()
