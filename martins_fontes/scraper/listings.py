from __future__ import annotations

import logging
from typing import Any

from shared.models import BookCard
from shared.utils.http import HttpClient

from martins_fontes import config
from martins_fontes.parsers.vtex_parser import parse_card
from martins_fontes.scraper.categories import Category

logger = logging.getLogger(__name__)


def _search_url(category: Category, start: int, end: int) -> str:
    path = "/".join(category.path_segments)
    map_param = ",".join(["c"] * len(category.path_segments))
    return (
        f"{config.BASE_URL}/api/catalog_system/pub/products/search/{path}"
        f"?map={map_param}&_from={start}&_to={end}"
    )


def _total_from_resources(header: str | None) -> int | None:
    if not header or "/" not in header:
        return None
    try:
        return int(header.split("/")[1])
    except ValueError:
        return None


def scrape_listings(
    client: HttpClient,
    categories: list[Category],
    max_pages_per_category: int | None = None,
) -> list[BookCard]:
    cards: list[BookCard] = []
    seen_urls: set[str] = set()

    for category in categories:
        page_index = 0
        while True:
            if max_pages_per_category is not None and page_index >= max_pages_per_category:
                break

            start = page_index * config.PAGE_SIZE
            end = start + config.PAGE_SIZE - 1
            url = _search_url(category, start, end)
            response = client.get(url)
            products: list[dict[str, Any]] = response.json()
            total = _total_from_resources(response.headers.get("resources"))

            if not products:
                break

            for product in products:
                card = parse_card(product, category.name, "/".join(category.path_segments))
                if card.product_url in seen_urls:
                    continue
                seen_urls.add(card.product_url)
                cards.append(card)

            logger.info(
                "Listings page scraped | category=%s page=%s products=%s total_hint=%s",
                category.name,
                page_index + 1,
                len(products),
                total,
            )

            page_index += 1
            if total is not None and end + 1 >= total:
                break
            if len(products) < config.PAGE_SIZE:
                break

    return cards
