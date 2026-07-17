import re
from decimal import Decimal
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from shared.models import BookCard, BookDetail

from travessa import config


def _text(soup: BeautifulSoup, selector: str) -> str | None:
    element = soup.select_one(selector)
    if element is None:
        return None
    text = element.get_text(" ", strip=True)
    return text or None


def _link_text(soup: BeautifulSoup, selector: str) -> str | None:
    elements = soup.select(selector)
    values = [element.get_text(" ", strip=True) for element in elements]
    return " | ".join(value for value in values if value) or None


def _price(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"R\$\s*([\d.]+,\d{2})", value)
    if not match:
        return None
    normalized = match.group(1).replace(".", "").replace(",", ".")
    return float(Decimal(normalized))


def _product_id(product_url: str) -> str | None:
    segments = [segment for segment in urlparse(product_url).path.split("/") if segment]
    try:
        return segments[segments.index("artigo") + 1]
    except (ValueError, IndexError):
        return None


def parse_card(element: Tag, category: str, category_path: str) -> BookCard | None:
    cover = element.select_one("a.cover[href*='/artigo/']")
    if cover is None:
        return None

    product_url = urljoin(config.BASE_URL, cover["href"])
    prices = [
        price
        for price in (_price(item.get_text(" ", strip=True)) for item in element.select(".price, .de"))
        if price is not None
    ]
    author = element.select_one(".subtitle")
    image = cover.select_one("img[src]")
    return BookCard(
        source_site=config.SOURCE_SITE,
        product_url=product_url,
        product_id=_product_id(product_url),
        title=cover.get("title") or cover.get_text(" ", strip=True),
        author=(author.get("name") or author.get_text(" ", strip=True)) if author else None,
        category=category,
        category_path=category_path,
        list_price=prices[0] if prices else None,
        best_price=prices[-1] if prices else None,
        cover_url=urljoin(config.BASE_URL, image["src"]) if image else None,
    )


def parse_listing(html: str, category: str, category_path: str) -> list[BookCard]:
    soup = BeautifulSoup(html, "lxml")
    cards: list[BookCard] = []
    seen_urls: set[str] = set()
    for cover in soup.select("a.cover[href*='/artigo/']"):
        container = cover.find_parent(class_="productBox") or cover.parent
        card = parse_card(container, category, category_path)
        if card and card.product_url not in seen_urls:
            seen_urls.add(card.product_url)
            cards.append(card)
    return cards


def next_page_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    link = soup.select_one("#wctPaginacao_pagingControl a.next[href]")
    if link is None or link["href"].startswith("javascript:"):
        return None
    return urljoin(f"{config.BASE_URL}/", link["href"])


def parse_detail(html: str, product_url: str, category: str | None) -> BookDetail:
    soup = BeautifulSoup(html, "lxml")
    participants = _text(soup, "#lblTituloDadosParticipantes")
    translator_match = re.search(r"TRADUTOR\s*:\s*(.+)$", participants or "", re.IGNORECASE)
    cover = soup.select_one("#imgArtigo[src]")
    list_price = _price(_text(soup, "#litPrecoOri"))
    best_price = _price(_text(soup, "#litPreco"))

    technical_sheet = {
        "title": _text(soup, "#lblDadosNome"),
        "isbn": _text(soup, "#lblDadosIsbn"),
        "language": _text(soup, "#lblDadosIdioma"),
        "binding": _text(soup, "#lblDadosEncadernacao"),
        "dimensions": _text(soup, "#lblDadosFormato"),
        "pages": _text(soup, "#lblDadosPaginas"),
        "collection": _text(soup, "#lblDadosColecao"),
        "year": _text(soup, "#lblDadosAnoEdicao"),
        "edition": _text(soup, "#lblDadosEdicao"),
        "participants": participants,
    }
    technical_sheet = {
        key: value for key, value in technical_sheet.items() if value
    }

    title = cover.get("alt") if cover else None
    return BookDetail(
        source_site=config.SOURCE_SITE,
        product_url=product_url,
        product_id=_product_id(product_url),
        title=title or _text(soup, "#lblDadosNome") or "",
        author=_link_text(soup, "#lblNomAutor a.txtConteudo"),
        publisher=_link_text(soup, "#lblNomProdutor a.txtConteudo"),
        synopsis=_text(soup, "#lblSinopse"),
        isbn=_text(soup, "#lblDadosIsbn"),
        year=_text(soup, "#lblDadosAnoEdicao"),
        edition=_text(soup, "#lblDadosEdicao"),
        pages=_text(soup, "#lblDadosPaginas"),
        language=_text(soup, "#lblDadosIdioma"),
        binding=_text(soup, "#lblDadosEncadernacao"),
        dimensions=_text(soup, "#lblDadosFormato"),
        translator=translator_match.group(1).strip() if translator_match else None,
        category=category,
        list_price=list_price,
        best_price=best_price,
        cover_url=urljoin(config.BASE_URL, cover["src"]) if cover else None,
        technical_sheet=technical_sheet,
    )
