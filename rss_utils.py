import feedparser
from bs4 import BeautifulSoup


def get_entries(url):
    entries = []
    try:
        d = feedparser.parse(url)
    except:
        return entries
    for entry in d.entries:
        description = BeautifulSoup(entry.description, "html.parser").text.strip()
        entries.append((entry.title, entry.link, description))
    return entries