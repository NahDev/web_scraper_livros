import logging

from shared.models import BookCard
from shared.utils.http import HttpClient

from travessa.parsers.html_parser import next_page_url, parse_listing
from travessa.scraper.categories import Category

logger = logging.getLogger(__name__)


def scrape_listings(
    client: HttpClient,
    categories: list[Category],
    max_pages_per_category: int | None = None,
) -> list[BookCard]:
    cards: list[BookCard] = []
    seen_urls: set[str] = set()

    for category in categories:
        page_url: str | None = category.url
        page_number = 0
        while page_url and (
            max_pages_per_category is None
            or page_number < max_pages_per_category
        ):
            response = client.get(page_url)
            page_cards = parse_listing(response.text, category.name, category.path)
            for card in page_cards:
                if card.product_url not in seen_urls:
                    seen_urls.add(card.product_url)
                    cards.append(card)

            page_number += 1
            logger.info(
                "Listings page scraped | category=%s page=%s products=%s",
                category.name,
                page_number,
                len(page_cards),
            )
            page_url = next_page_url(response.text)

    return cards
