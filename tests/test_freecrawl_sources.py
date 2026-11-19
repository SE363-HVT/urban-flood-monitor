import io
import time
import unittest
from collections import Counter
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import feedparser

from pipeline import live_free_crawler as crawler


class FreeCrawlSourceTests(unittest.TestCase):
    def setUp(self):
        self.source = crawler.LiveFreeSocialCrawler()
        self.cls = type(self.source)

    def test_google_rotates_and_direct_sources_run_during_cooldown(self):
        with (
            patch.object(self.cls, "_google_next_scan", 0),
            patch.object(self.cls, "_google_circuit_broken_until", 0),
            patch.object(self.cls, "_youtube_next_scan", float("inf")),
            patch.object(self.source, "_fetch_google_query", return_value=[]) as google,
            patch.object(self.source, "_fetch_direct_news_rss", return_value=[]) as news,
            patch.object(self.source, "_fetch_vov_traffic_reports", return_value=[]) as vov,
            patch.object(self.source, "_fetch_1022_public_reports", return_value=[]) as citizen,
            patch.object(crawler.time, "monotonic", return_value=100) as clock,
        ):
            _, first = self.source.poll_live_stream()
            allocation = Counter(call.args[1] for call in google.call_args_list)
            first_queries = {call.args[0] for call in google.call_args_list}
            clock.return_value = 130
            _, second = self.source.poll_live_stream()
            clock.return_value = 250
            _, third = self.source.poll_live_stream()
        self.assertEqual(allocation, {"facebook": 4, "tiktok": 3, "news": 1})
        self.assertEqual([x["google_queries_scheduled"] for x in (first, second, third)], [8, 0, 8])
        self.assertNotEqual(first_queries, {call.args[0] for call in google.call_args_list[8:]})
        for source in (news, vov, citizen):
            self.assertEqual(source.call_count, 3)

    def test_google_respects_retry_after(self):
        error = HTTPError("https://news.google.com", 429, "limited", {"Retry-After": "420"}, io.BytesIO())
        self.addCleanup(error.close)
        with patch.object(self.cls, "_google_circuit_broken_until", 0), patch.object(
            crawler.urllib.request, "urlopen", side_effect=error
        ) as request, patch.object(crawler.time, "time", return_value=1000):
            self.source._fetch_google_query("ngập", "news", 3)
            self.assertEqual(self.cls._google_circuit_broken_until, 1420)
            self.source._fetch_google_query("ngập", "news", 3)
            request.assert_called_once()

    def test_direct_news_filters_unrelated_and_undated_items(self):
        good = feedparser.FeedParserDict(title="TP.HCM ngập sâu trên đường Nguyễn Hữu Cảnh, xe chết máy",
                                         link="https://example.com/flood", published_parsed=time.gmtime(time.time() - 60))
        unrelated = feedparser.FeedParserDict(title="TP.HCM tổ chức hiến máu",
                                              link="https://example.com/other", published_parsed=good.published_parsed)
        undated = feedparser.FeedParserDict(title=good.title, link="https://example.com/undated")
        point = {"street": "Nguyễn Hữu Cảnh", "lat": 10.78, "lon": 106.7}
        with (
            patch.object(crawler.requests, "get", return_value=Mock(ok=True, content=b"")),
            patch.object(crawler.feedparser, "parse", return_value=Mock(entries=[unrelated, undated, good])),
            patch.object(crawler, "match_all_hotspots", return_value=[point]),
        ):
            events = self.source._fetch_direct_news_rss()
        self.assertEqual([event["url"] for event in events], [good.link])

    def test_youtube_emits_verified_short_and_filters_non_flood(self):
        now = int(time.time()) - 30
        point = {"street": "Nguyễn Hữu Cảnh", "lat": 10.78, "lon": 106.7}
        title = "TP.HCM ngập sâu trên đường Nguyễn Hữu Cảnh, xe chết máy"
        with (
            patch.object(crawler, "YoutubeDL"),
            patch.object(self.source, "_youtube_api_candidates", return_value=[
                ("https://www.youtube.com/shorts/12345678901", title, now, "Channel", 0, ""),
                ("https://www.youtube.com/watch?v=12345678902", "TP.HCM tổ chức hiến máu", now, "Channel", 0, ""),
            ]),
            patch.object(crawler, "match_all_hotspots", return_value=[point]),
        ):
            events = self.source._fetch_youtube_hotspots()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["media_type"], "short_video")

    def test_youtube_api_rotation_is_rate_limited(self):
        now = int(time.time())
        with (
            patch.dict(crawler.os.environ, {"YOUTUBE_DATA_API_KEY": "test-key"}),
            patch.object(self.cls, "_youtube_api_next_scan", 0),
            patch.object(self.cls, "_youtube_api_offset", 0),
            patch.object(crawler.requests, "get", return_value=Mock(status_code=200, json=lambda: {})) as request,
        ):
            self.source._youtube_api_candidates(now)
            self.source._youtube_api_candidates(now + 60)
            request.assert_called_once()
            self.source._youtube_api_candidates(now + 1200)
        first, second = request.call_args_list
        self.assertNotEqual(first.kwargs["params"]["q"], second.kwargs["params"]["q"])
        self.assertIn("publishedAfter", first.kwargs["params"])
