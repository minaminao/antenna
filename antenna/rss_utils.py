import feedparser
from bs4 import BeautifulSoup


def get_entries(url: str) -> tuple[str, list[tuple[str, str, str]]]:
    entries: list[tuple[str, str, str]] = []
    try:
        d = feedparser.parse(url)
    except Exception:
        return "", entries

    feed_title: str = d.feed.title
    for entry in d.entries:
        description = BeautifulSoup(entry.description, "html.parser").text.strip()
        entries.append((entry.title, entry.link, description))
    return feed_title, entries
