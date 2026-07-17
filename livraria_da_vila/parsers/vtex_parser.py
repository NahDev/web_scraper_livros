from typing import Any

from shared.models import BookCard, BookDetail

from livraria_da_vila import config


def _first(value: Any) -> str | None:
    if isinstance(value, list):
        return str(value[0]).strip() if value else None
    return str(value).strip() if value is not None else None


def _prices(product: dict[str, Any]) -> tuple[float | None, float | None]:
    try:
        offer = product["items"][0]["sellers"][0]["commertialOffer"]
    except (KeyError, IndexError, TypeError):
        return None, None
    return offer.get("ListPrice"), offer.get("Price")


def _cover_url(product: dict[str, Any]) -> str | None:
    try:
        return product["items"][0]["images"][0]["imageUrl"]
    except (KeyError, IndexError, TypeError):
        return None


def _technical_sheet(product: dict[str, Any]) -> dict[str, Any]:
    return {
        field: product[field]
        for field in product.get("allSpecifications") or []
        if field in product
    }


def _dimensions(product: dict[str, Any]) -> str | None:
    values = [
        _first(product.get("Altura")),
        _first(product.get("Largura")),
        _first(product.get("Profundidade")),
    ]
    return " x ".join(value for value in values if value) or None


def parse_card(
    product: dict[str, Any],
    category: str,
    category_path: str,
) -> BookCard:
    list_price, best_price = _prices(product)
    return BookCard(
        source_site=config.SOURCE_SITE,
        product_url=product["link"],
        product_id=_first(product.get("productId")),
        title=product.get("productName") or "",
        author=_first(product.get("Autor")),
        category=category,
        category_path=category_path,
        list_price=list_price,
        best_price=best_price,
        cover_url=_cover_url(product),
    )


def parse_detail(
    product: dict[str, Any],
    fallback_category: str | None = None,
) -> BookDetail:
    list_price, best_price = _prices(product)
    technical_sheet = _technical_sheet(product)
    return BookDetail(
        source_site=config.SOURCE_SITE,
        product_url=product["link"],
        product_id=_first(product.get("productId")),
        title=product.get("productName") or "",
        author=_first(product.get("Autor")),
        publisher=_first(product.get("Editora")) or product.get("brand"),
        synopsis=_first(product.get("Sinopse")) or _first(product.get("description")),
        isbn=_first(product.get("ISBN")),
        year=_first(product.get("Ano de Edição")),
        edition=_first(product.get("Edição")),
        pages=_first(product.get("Número de Páginas")),
        language=_first(product.get("Idioma")),
        binding=_first(product.get("Acabamento")),
        dimensions=_dimensions(product),
        weight=_first(product.get("Peso")),
        translator=_first(product.get("Tradutor")),
        category=fallback_category,
        list_price=list_price,
        best_price=best_price,
        cover_url=_cover_url(product),
        technical_sheet=technical_sheet,
    )
