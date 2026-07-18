"""Shared game data fetching functions."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx

_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

STATUS_URL = "https://files.publishing.production.jxp.jagex.com/osrs/osrs.json"
OSRS_NEWS_URL = "https://secure.runescape.com/m=news/latestNews.json"
RS3_NEWS_URL = "https://secure.runescape.com/m=news/l={locale}/latestNews.json"
RS3_NEWS_FALLBACK_URL = "https://secure.runescape.com/m=news/l=0/latestNews.json"

_MAX_RETRIES = 3
_RETRY_DELAY = 0.5
_REQUEST_TIMEOUT = 10


class GameError(Exception):
    pass


def check_status() -> dict[str, Any]:
    try:
        r = httpx.get(STATUS_URL, timeout=_REQUEST_TIMEOUT)
        r.raise_for_status()
        data: dict[str, Any] = r.json()
        return data
    except Exception as e:
        raise GameError(str(e)) from e


def _fetch_with_retry(
    url: str,
    *,
    params: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    latin1: bool = False,
) -> list[dict[str, str]]:
    for _attempt in range(_MAX_RETRIES):
        try:
            r = httpx.get(url, params=params, headers=headers, timeout=_REQUEST_TIMEOUT)
            if r.status_code == 200:
                data = json.loads(r.content.decode("latin-1")) if latin1 else r.json()
                articles = list(data.get("newsItems", []))
                if articles:
                    return articles
            time.sleep(_RETRY_DELAY)
        except httpx.HTTPError:
            time.sleep(_RETRY_DELAY)
    return []


def fetch_news(game: str, count: int = 5, locale: int = 0) -> list[dict[str, str]]:
    if game == "osrs":
        articles = _fetch_with_retry(OSRS_NEWS_URL, params={"oldschool": "1"})
    else:
        urls = [RS3_NEWS_URL.format(locale=locale)]
        if locale:
            urls.append(RS3_NEWS_FALLBACK_URL)
        articles = []
        for url in urls:
            articles = _fetch_with_retry(url, headers={"User-Agent": _USER_AGENT}, latin1=True)
            if articles:
                break
    return articles[:count]
