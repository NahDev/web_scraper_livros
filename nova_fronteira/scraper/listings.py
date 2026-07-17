import logging

from shared.models import BookCard
from shared.utils.http import HttpClient

from nova_fronteira.parsers.html_parser import has_next_page, parse_listing
from nova_fronteira.scraper.categories import Category

logger = logging.getLogger(__name__)


def scrape_listings(
    client: HttpClient,
    categories: list[Category],
    max_pages_per_category: int | None = None,
) -> list[BookCard]:
    cards: list[BookCard] = []
    seen_urls: set[str] = set()

    for category in categories:
        page_number = 1
        while max_pages_per_category is None or page_number <= max_pages_per_category:
            response = client.get(f"{category.url}?pagina={page_number}")
            page_cards = parse_listing(response.text, category.name, category.path)
            new_cards = [card for card in page_cards if card.product_url not in seen_urls]
            if not new_cards:
                break

            for card in new_cards:
                seen_urls.add(card.product_url)
                cards.append(card)

            logger.info(
                "Listings page scraped | category=%s page=%s products=%s",
                category.name,
                page_number,
                len(new_cards),
            )

            if not has_next_page(response.text, page_number):
                break
            page_number += 1

    return cards
