from __future__ import annotations

import logging
from urllib.parse import urlparse

from shared.models import BookCard, BookDetail
from shared.utils.http import HttpClient

from martins_fontes import config
from martins_fontes.parsers.vtex_parser import parse_detail

logger = logging.getLogger(__name__)


def _link_text(product_url: str) -> str:
    path = urlparse(product_url).path.strip("/")
    if path.endswith("/p"):
        path = path[:-2]
    return path.strip("/")


def scrape_products(
    client: HttpClient,
    cards: list[BookCard],
    max_products: int | None = None,
) -> list[BookDetail]:
    targets = cards[:max_products] if max_products is not None else cards
    details: list[BookDetail] = []

    for index, card in enumerate(targets, start=1):
        link_text = _link_text(card.product_url)
        url = f"{config.BASE_URL}/api/catalog_system/pub/products/search/{link_text}/p"
        response = client.get(url)
        payload = response.json()
        if not payload:
            logger.warning("Empty product payload | url=%s", card.product_url)
            continue
        detail = parse_detail(payload[0], fallback_category=card.category)
        details.append(detail)
        if index % 10 == 0 or index == len(targets):
            logger.info("Products scraped | progress=%s/%s", index, len(targets))

    return details
