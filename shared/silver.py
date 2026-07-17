import re
from html import unescape
from typing import Any

from shared.models import BookCard, BookDetail, BookSilver


def _first(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return str(value[0]).strip() if value else None
    text = str(value).strip()
    return text or None


def clean_html(value: str | None) -> str | None:
    if not value:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _parse_pages(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    pages = int(match.group()) if match else 0
    return pages or None


def _extract_year(
    year: str | None,
    edition: str | None,
    technical_sheet: dict[str, Any],
) -> str | None:
    candidates = [
        year,
        edition,
        technical_sheet.get("Ano de Edição"),
        technical_sheet.get("Número da edição"),
        technical_sheet.get("Ano"),
    ]
    for candidate in candidates:
        text = _first(candidate)
        if not text:
            continue
        match = re.search(r"(19|20)\d{2}", text)
        if match:
            return match.group()
    return None


def build_silver(card: BookCard | None, detail: BookDetail) -> BookSilver:
    technical_sheet = dict(detail.technical_sheet)
    edition = detail.edition or _first(technical_sheet.get("Número da edição"))
    return BookSilver(
        source_site=detail.source_site,
        product_url=detail.product_url,
        product_id=detail.product_id or (card.product_id if card else None),
        title=detail.title or (card.title if card else ""),
        author=detail.author or (card.author if card else None),
        publisher=detail.publisher,
        synopsis=clean_html(detail.synopsis),
        isbn=detail.isbn,
        year=_extract_year(detail.year, edition, technical_sheet),
        edition=edition,
        pages=_parse_pages(detail.pages),
        language=detail.language,
        binding=detail.binding,
        dimensions=detail.dimensions,
        weight=detail.weight,
        translator=detail.translator,
        category=detail.category or (card.category if card else None),
        category_path=card.category_path if card else None,
        list_price=detail.list_price if detail.list_price is not None else (card.list_price if card else None),
        best_price=detail.best_price if detail.best_price is not None else (card.best_price if card else None),
        cover_url=detail.cover_url or (card.cover_url if card else None),
        technical_sheet=technical_sheet,
        scraped_at=detail.scraped_at,
    )


def merge_to_silver(cards: list[BookCard], details: list[BookDetail]) -> list[BookSilver]:
    cards_by_url = {card.product_url: card for card in cards}
    return [build_silver(cards_by_url.get(detail.product_url), detail) for detail in details]
