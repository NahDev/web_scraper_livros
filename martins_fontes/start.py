from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone

from shared.database.connection import init_database, upsert_books
from shared.silver import merge_to_silver
from shared.storage.bronze_silver import (
    save_bronze_listings,
    save_bronze_products,
    save_silver_books,
)
from shared.utils.http import HttpClient
from shared.utils.logging import setup_logging

from martins_fontes import config
from martins_fontes.scraper.categories import fetch_categories
from martins_fontes.scraper.listings import scrape_listings
from martins_fontes.scraper.products import scrape_products

logger = logging.getLogger(__name__)


def start(
    max_categories: int | None = config.DEFAULT_MAX_CATEGORIES,
    max_pages_per_category: int | None = config.DEFAULT_MAX_PAGES_PER_CATEGORY,
    max_products: int | None = config.DEFAULT_MAX_PRODUCTS,
) -> None:
    setup_logging()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    logger.info(
        "Starting Martins Fontes pipeline | run_id=%s max_categories=%s max_pages=%s max_products=%s",
        run_id,
        max_categories,
        max_pages_per_category,
        max_products,
    )

    with HttpClient(delay_seconds=config.REQUEST_DELAY_SECONDS) as client:
        categories = fetch_categories(client, max_categories=max_categories)
        logger.info("Categories selected | count=%s", len(categories))

        cards = scrape_listings(
            client,
            categories,
            max_pages_per_category=max_pages_per_category,
        )
        listings_path = save_bronze_listings(config.SOURCE_SITE, cards, run_id=run_id)
        logger.info("Bronze listings saved | count=%s path=%s", len(cards), listings_path)

        details = scrape_products(client, cards, max_products=max_products)
        products_path = save_bronze_products(config.SOURCE_SITE, details, run_id=run_id)
        logger.info("Bronze products saved | count=%s path=%s", len(details), products_path)

    silver_books = merge_to_silver(cards, details)
    silver_path = save_silver_books(config.SOURCE_SITE, silver_books, run_id=run_id)
    logger.info("Silver books saved | count=%s path=%s", len(silver_books), silver_path)

    engine = init_database()
    upserted = upsert_books(silver_books, engine=engine)
    logger.info("Gold upsert finished | count=%s", upserted)


def main() -> None:
    parser = argparse.ArgumentParser(description="Martins Fontes bookstore scraper")
    parser.add_argument("--max-categories", type=int, default=config.DEFAULT_MAX_CATEGORIES)
    parser.add_argument(
        "--max-pages-per-category",
        type=int,
        default=config.DEFAULT_MAX_PAGES_PER_CATEGORY,
    )
    parser.add_argument("--max-products", type=int, default=config.DEFAULT_MAX_PRODUCTS)
    parser.add_argument(
        "--full",
        action="store_true",
        help="Scrape all categories/pages/products (no limits)",
    )
    args = parser.parse_args()

    if args.full:
        start(max_categories=None, max_pages_per_category=None, max_products=None)
    else:
        start(
            max_categories=args.max_categories,
            max_pages_per_category=args.max_pages_per_category,
            max_products=args.max_products,
        )


if __name__ == "__main__":
    main()
