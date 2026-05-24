from urllib.parse import parse_qs, quote_plus, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


SEARCH_URL = "https://duckduckgo.com/html/?q={query}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search public webpages and return a small list of title/url dicts."""
    url = SEARCH_URL.format(query=quote_plus(query))
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for link in soup.select(".result__a"):
        title = link.get_text(" ", strip=True)
        href = normalize_url(link.get("href"))

        if not title or not href:
            continue

        parsed = urlparse(href)
        if parsed.scheme not in {"http", "https"}:
            continue

        results.append({"title": title, "url": href})

        if len(results) >= max_results:
            break

    return results


def normalize_url(href: str | None) -> str | None:
    if not href:
        return None

    absolute_url = urljoin("https://duckduckgo.com", href)
    parsed = urlparse(absolute_url)
    query = parse_qs(parsed.query)

    if "uddg" in query:
        return unquote(query["uddg"][0])

    return absolute_url
