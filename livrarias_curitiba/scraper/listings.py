import logging
from typing import Any

from shared.models import BookCard
from shared.utils.http import HttpClient

from livrarias_curitiba import config
from livrarias_curitiba.parsers.vtex_parser import parse_card
from livrarias_curitiba.scraper.categories import Category

logger = logging.getLogger(__name__)


def _search_url(
    category: Category,
    start: int,
    end: int,
    ordering: str | None = None,
) -> str:
    path = "/".join(category.path_segments)
    category_map = ",".join("c" for _ in category.path_segments)
    url = (
        f"{config.BASE_URL}/api/catalog_system/pub/products/search/{path}"
        f"?map={category_map}&_from={start}&_to={end}"
    )
    return f"{url}&_O={ordering}" if ordering else url


def _total_from_resources(resources: str | None) -> int | None:
    if not resources or "/" not in resources:
        return None
    try:
        return int(resources.split("/")[1])
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
        category_urls: set[str] = set()
        total: int | None = None
        orderings = (
            [None]
            if max_pages_per_category is not None
            else ["OrderByNameASC", "OrderByNameDESC"]
        )

        for ordering in orderings:
            page_index = 0
            while max_pages_per_category is None or page_index < max_pages_per_category:
                start = page_index * config.PAGE_SIZE
                if start > 2500:
                    break

                end = start + config.PAGE_SIZE - 1
                response = client.get(_search_url(category, start, end, ordering))
                products: list[dict[str, Any]] = response.json()
                total = _total_from_resources(response.headers.get("resources"))
                if not products:
                    break

                for product in products:
                    card = parse_card(
                        product,
                        category.name,
                        "/".join(category.path_segments),
                    )
                    category_urls.add(card.product_url)
                    if card.product_url not in seen_urls:
                        seen_urls.add(card.product_url)
                        cards.append(card)

                page_index += 1
                logger.info(
                    "Listings page scraped | category=%s order=%s page=%s products=%s total_hint=%s",
                    category.name,
                    ordering or "default",
                    page_index,
                    len(products),
                    total,
                )
                if (
                    len(products) < config.PAGE_SIZE
                    or (total is not None and len(category_urls) >= total)
                ):
                    break

            if total is not None and len(category_urls) >= total:
                break

    return cards
