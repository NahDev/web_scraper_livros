import logging
from urllib.parse import urlparse

from shared.models import BookCard, BookDetail
from shared.utils.http import HttpClient

from livraria_da_vila import config
from livraria_da_vila.parsers.vtex_parser import parse_detail

logger = logging.getLogger(__name__)


def _link_text(product_url: str) -> str:
    path = urlparse(product_url).path.strip("/")
    return path.removesuffix("/p")


def scrape_products(
    client: HttpClient,
    cards: list[BookCard],
    max_products: int | None = None,
) -> list[BookDetail]:
    targets = cards[:max_products] if max_products is not None else cards
    details: list[BookDetail] = []

    for index, card in enumerate(targets, start=1):
        url = (
            f"{config.BASE_URL}/api/catalog_system/pub/products/search/"
            f"{_link_text(card.product_url)}/p"
        )
        payload = client.get(url).json()
        if not payload:
            logger.warning("Empty product payload | url=%s", card.product_url)
            continue

        details.append(parse_detail(payload[0], fallback_category=card.category))
        if index % 10 == 0 or index == len(targets):
            logger.info("Products scraped | progress=%s/%s", index, len(targets))

    return details
