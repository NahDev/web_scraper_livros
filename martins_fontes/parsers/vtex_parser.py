from __future__ import annotations

from typing import Any

from shared.models import BookCard, BookDetail

from martins_fontes import config


def _first(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return str(value[0]).strip() if value else None
    text = str(value).strip()
    return text or None


def _prices(product: dict[str, Any]) -> tuple[float | None, float | None]:
    try:
        offer = product["items"][0]["sellers"][0]["commertialOffer"]
    except (KeyError, IndexError, TypeError):
        return None, None
    best = offer.get("Price")
    listed = offer.get("ListPrice")
    return (
        float(listed) if listed is not None else None,
        float(best) if best is not None else None,
    )


def _cover_url(product: dict[str, Any]) -> str | None:
    try:
        return product["items"][0]["images"][0]["imageUrl"]
    except (KeyError, IndexError, TypeError):
        return None


def _category_name(product: dict[str, Any]) -> str | None:
    categories = product.get("categories") or []
    if not categories:
        return None
    parts = [part for part in categories[0].strip("/").split("/") if part]
    return parts[-1] if parts else None


def _technical_sheet(product: dict[str, Any]) -> dict[str, Any]:
    sheet: dict[str, Any] = {}
    for key in product.get("allSpecifications") or []:
        value = product.get(key)
        if value is not None:
            sheet[key] = value
    return sheet


def parse_card(product: dict[str, Any], category: str | None, category_path: str | None) -> BookCard:
    list_price, best_price = _prices(product)
    return BookCard(
        source_site=config.SOURCE_SITE,
        product_url=product["link"],
        product_id=_first(product.get("productId")),
        title=product.get("productName") or "",
        author=_first(product.get("Autor")),
        category=category or _category_name(product),
        category_path=category_path,
        list_price=list_price,
        best_price=best_price,
        cover_url=_cover_url(product),
    )


def parse_detail(product: dict[str, Any], fallback_category: str | None = None) -> BookDetail:
    list_price, best_price = _prices(product)
    sheet = _technical_sheet(product)
    return BookDetail(
        source_site=config.SOURCE_SITE,
        product_url=product["link"],
        product_id=_first(product.get("productId")),
        title=product.get("productName") or "",
        author=_first(product.get("Autor")) or _first(sheet.get("Autor")),
        publisher=_first(product.get("Editora")) or _first(sheet.get("Editora")) or product.get("brand"),
        synopsis=_first(product.get("description")),
        isbn=_first(product.get("ISBN")) or _first(product.get("Código de barras")),
        year=None,
        edition=_first(product.get("Número da edição")),
        pages=_first(product.get("Número de páginas")),
        language=_first(product.get("Idioma")),
        binding=_first(product.get("Acabamento")),
        dimensions=_first(product.get("Dimensões")),
        weight=_first(product.get("Peso")),
        translator=_first(product.get("Tradutor")),
        category=fallback_category or _category_name(product),
        list_price=list_price,
        best_price=best_price,
        cover_url=_cover_url(product),
        technical_sheet=sheet,
    )
