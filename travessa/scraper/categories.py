from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from shared.utils.http import HttpClient

from travessa import config


@dataclass
class Category:
    name: str
    url: str
    path: str


def _links_at_depth(html: str, prefix: str, depth: int) -> dict[str, str]:
    soup = BeautifulSoup(html, "lxml")
    links: dict[str, str] = {}
    for anchor in soup.find_all("a", href=True):
        url = urljoin(config.BASE_URL, anchor["href"])
        parsed = urlparse(url)
        segments = [segment for segment in parsed.path.strip("/").split("/") if segment]
        if (
            parsed.netloc.endswith("travessa.com.br")
            and len(segments) == depth
            and parsed.path.startswith(prefix)
        ):
            name = anchor.get_text(" ", strip=True)
            if name:
                links[url] = name
    return links


def fetch_categories(client: HttpClient, max_categories: int | None = None) -> list[Category]:
    books_url = f"{config.BASE_URL}{config.BOOKS_PATH}"
    macro_links = _links_at_depth(client.get(books_url).text, "/livros/", 2)
    category_links: dict[str, str] = {}

    for macro_url in macro_links:
        macro_path = urlparse(macro_url).path.rstrip("/") + "/"
        category_links.update(
            _links_at_depth(client.get(macro_url).text, macro_path, 3)
        )

    categories = [
        Category(
            name=name,
            url=url,
            path=urlparse(url).path.strip("/"),
        )
        for url, name in category_links.items()
    ]
    return categories[:max_categories] if max_categories is not None else categories
