from agents.trend_research import TrendResearchInput
from agents.trend_sources.rss import RssTrendDataSource


def test_rss_trend_source_parses_feed(monkeypatch) -> None:
    sample = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel>
      <item>
        <title>Instagram Reels hooks that convert</title>
        <description>Creators are testing short hooks for beauty content.</description>
        <link>https://example.com/post-1</link>
      </item>
    </channel></rss>
    """

    class _FakeResponse:
        text = sample

        def raise_for_status(self) -> None:
            return None

    monkeypatch.setattr(
        "agents.trend_sources.rss.httpx.get",
        lambda *args, **kwargs: _FakeResponse(),
    )

    source = RssTrendDataSource(["https://www.reddit.com/r/InstagramMarketing/.rss"])
    signals = source.fetch_signals(
        input_data=TrendResearchInput(
            creator_niche="beauty",
            target_platforms=["instagram"],
            audience_description="18-34 beauty enthusiasts",
        )
    )
    assert len(signals) == 1
    assert "Instagram Reels hooks" in signals[0].topic
    assert signals[0].source.startswith("rss:")
