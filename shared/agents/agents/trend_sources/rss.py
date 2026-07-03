from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlparse

import httpx

from agents.trend_research import TrendDataSource, TrendResearchInput, TrendSignal


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    return unescape(re.sub(r"\s+", " ", cleaned)).strip()


def _platform_from_feed_url(feed_url: str) -> str:
    host = urlparse(feed_url).netloc.lower()
    if "reddit" in host:
        return "reddit"
    if "youtube" in host:
        return "youtube"
    return "rss"


class RssTrendDataSource(TrendDataSource):
    """Fetch trend signals from public RSS feeds (Reddit subreddits, blogs, etc.)."""

    def __init__(self, feed_urls: list[str], *, timeout_seconds: float = 10.0) -> None:
        self.feed_urls = [url.strip() for url in feed_urls if url.strip()]
        self.timeout_seconds = timeout_seconds

    def fetch_signals(self, *, input_data: TrendResearchInput) -> list[TrendSignal]:
        platforms = {platform.lower() for platform in input_data.target_platforms}
        niche = input_data.creator_niche.strip()
        signals: list[TrendSignal] = []

        for feed_url in self.feed_urls:
            platform = _platform_from_feed_url(feed_url)
            if platform == "reddit":
                if not platforms.intersection({"instagram", "tiktok", "youtube", "x", "multi"}):
                    continue
            elif platform not in platforms and platform != "rss":
                continue
            signals.extend(self._fetch_feed(feed_url=feed_url, platform=platform, niche=niche))

        return signals[:12]

    def _fetch_feed(self, *, feed_url: str, platform: str, niche: str) -> list[TrendSignal]:
        try:
            response = httpx.get(
                feed_url,
                timeout=self.timeout_seconds,
                headers={"User-Agent": "CreatorOS-TrendBot/1.0"},
                follow_redirects=True,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError:
            return []

        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        mapped_platform = "instagram" if platform == "reddit" else platform
        results: list[TrendSignal] = []

        for index, item in enumerate(items[:6]):
            title = _strip_html(
                (item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
            )
            if not title:
                continue
            description = _strip_html(
                item.findtext("description")
                or item.findtext("summary")
                or item.findtext("{http://www.w3.org/2005/Atom}summary")
                or ""
            )
            link = (item.findtext("link") or "").strip()
            strength = max(55, 90 - index * 5)
            results.append(
                TrendSignal(
                    topic=f"{title} ({niche})",
                    platform=mapped_platform if mapped_platform in {"instagram", "tiktok", "youtube", "x"} else "instagram",
                    signal_summary=description[:280] or f"Trending discussion relevant to {niche}.",
                    signal_strength=strength,
                    source=f"rss:{feed_url}" + (f"|{link}" if link else ""),
                )
            )
        return results
