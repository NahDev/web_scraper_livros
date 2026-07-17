from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from shared.utils.http import HttpClient

from nova_fronteira import config


@dataclass
class Category:
    name: str
    url: str
    path: str


def _is_collection(url: str) -> bool:
    parsed = urlparse(url)
    if not parsed.netloc.endswith("novafronteira.com.br"):
        return False
    segments = [segment for segment in parsed.path.strip("/").split("/") if segment]
    if len(segments) != 1:
        return False
    slug = segments[0]
    return "." not in slug and slug not in config.IGNORED_SLUGS


def fetch_categories(client: HttpClient, max_categories: int | None = None) -> list[Category]:
    catalog = Category(name="Livros", url=f"{config.BASE_URL}{config.CATALOG_PATH}", path="livros")
    categories = [catalog]

    soup = BeautifulSoup(client.get(catalog.url).text, "lxml")
    seen = {catalog.path}
    for anchor in soup.select("a[href]"):
        url = urljoin(config.BASE_URL, anchor["href"])
        name = anchor.get_text(" ", strip=True)
        if not name or not _is_collection(url):
            continue
        slug = urlparse(url).path.strip("/")
        if slug in seen:
            continue
        seen.add(slug)
        categories.append(Category(name=name, url=f"{config.BASE_URL}/{slug}", path=slug))

    return categories[:max_categories] if max_categories is not None else categories
