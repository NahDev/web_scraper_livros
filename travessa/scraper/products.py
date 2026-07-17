import logging

from shared.models import BookCard, BookDetail
from shared.utils.http import HttpClient

from travessa.parsers.html_parser import parse_detail

logger = logging.getLogger(__name__)


def scrape_products(
    client: HttpClient,
    cards: list[BookCard],
    max_products: int | None = None,
) -> list[BookDetail]:
    targets = cards[:max_products] if max_products is not None else cards
    details: list[BookDetail] = []

    for index, card in enumerate(targets, start=1):
        response = client.get(card.product_url)
        details.append(
            parse_detail(response.text, str(response.url), card.category)
        )
        if index % 10 == 0 or index == len(targets):
            logger.info("Products scraped | progress=%s/%s", index, len(targets))

    return details
