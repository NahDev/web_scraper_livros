import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from shared.models import BookCard, BookDetail

from nova_fronteira import config

TECHNICAL_LABELS = {
    "Autor": "author",
    "Autora": "author",
    "Tradutor": "translator",
    "Editora": "publisher",
    "Edição": "edition",
    "Ano": "year",
    "Ano de edição": "year",
    "Data da publicação": "year",
    "Páginas": "pages",
    "Número de páginas": "pages",
    "Idioma": "language",
    "Acabamento": "binding",
    "Formato": "binding",
    "Dimensões": "dimensions",
    "Peso": "weight",
    "ISBN-13": "isbn",
    "ISBN-10": "isbn10",
    "ISBN": "isbn",
    "Capa comum": "binding_pages",
    "Capa dura": "binding_pages",
    "Capa flexível": "binding_pages",
    "Capa dupla": "binding_pages",
    "Lançamento": "release",
    "lancamento": "release",
}

_LABEL_ALTERNATION = "|".join(
    re.escape(label) for label in sorted(TECHNICAL_LABELS, key=len, reverse=True)
)
_PAIR_PATTERN = re.compile(
    rf"({_LABEL_ALTERNATION})\s*:\s*(.*?)(?=\s*(?:{_LABEL_ALTERNATION})\s*:|$)"
)

_CLEAN = str.maketrans({"\u200f": "", "\u200e": "", "\xa0": " "})


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    text = value.translate(_CLEAN)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _sell_price(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_card(container: Tag, category: str, category_path: str) -> BookCard | None:
    name_link = container.select_one("a.nome-produto[href]")
    if name_link is None:
        return None

    price_tag = container.select_one("strong.preco-promocional[data-sell-price]")
    sku = container.select_one(".produto-sku")
    card_root = container.find_parent(class_=re.compile("produto")) or container
    image = card_root.select_one("img[src], img[data-src]")
    cover = None
    if image is not None:
        cover = image.get("src") or image.get("data-src")
        if cover and "--" in cover:
            cover = None

    return BookCard(
        source_site=config.SOURCE_SITE,
        product_url=urljoin(config.BASE_URL, name_link["href"]),
        product_id=_clean(sku.get_text(strip=True)) if sku else None,
        title=_clean(name_link.get_text(" ", strip=True)) or "",
        category=category,
        category_path=category_path,
        best_price=_sell_price(price_tag.get("data-sell-price")) if price_tag else None,
        cover_url=urljoin(config.BASE_URL, cover) if cover else None,
    )


def parse_listing(html: str, category: str, category_path: str) -> list[BookCard]:
    soup = BeautifulSoup(html, "lxml")
    cards: list[BookCard] = []
    seen_urls: set[str] = set()
    for container in soup.select(".info-produto"):
        card = parse_card(container, category, category_path)
        if card and card.product_url not in seen_urls:
            seen_urls.add(card.product_url)
            cards.append(card)
    return cards


def has_next_page(html: str, current_page: int) -> bool:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.select("a[href*='pagina=']"):
        match = re.search(r"pagina=(\d+)", anchor["href"])
        if match and int(match.group(1)) > current_page:
            return True
    return False


def _parse_technical(description: str) -> tuple[str, dict[str, str]]:
    text = _clean(description.replace("\n", " "))
    if not text:
        return "", {}

    technical: dict[str, str] = {}
    matches = list(_PAIR_PATTERN.finditer(text))
    for match in matches:
        label, field = match.group(1), TECHNICAL_LABELS[match.group(1)]
        value = match.group(2).strip().strip("-–—").strip()
        if field == "binding_pages":
            technical.setdefault("binding", label.lower())
            page_match = re.search(r"\d+", value)
            if page_match:
                technical.setdefault("pages", page_match.group())
        elif value:
            technical.setdefault(field, value)

    synopsis = text[: matches[0].start()].strip() if matches else text
    technical.pop("isbn10", None)
    technical.pop("release", None)
    return synopsis, technical


def _meta(soup: BeautifulSoup, itemprop: str) -> str | None:
    tag = soup.select_one(f"[itemprop={itemprop}]")
    if tag is None:
        return None
    return _clean(tag.get("content") or tag.get_text(" ", strip=True))


def parse_detail(html: str, product_url: str, category: str | None) -> BookDetail:
    soup = BeautifulSoup(html, "lxml")
    description_tag = soup.select_one("#descricao, [itemprop=description]")
    synopsis, technical = _parse_technical(
        description_tag.get_text("\n", strip=True) if description_tag else ""
    )

    author = _meta(soup, "brand")
    if author:
        author = re.sub(r"^Marca:\s*", "", author).strip()
    author = technical.get("author") or author

    image = soup.select_one("[itemprop=image][src], .imagem-produto img[src]")
    cover = None
    if image is not None:
        cover = image.get("src") or image.get("data-src")
        if cover and "--" in cover:
            cover = None

    return BookDetail(
        source_site=config.SOURCE_SITE,
        product_url=product_url,
        product_id=_meta(soup, "sku"),
        title=_meta(soup, "name") or (_clean(soup.h1.get_text(" ", strip=True)) if soup.h1 else ""),
        author=author,
        publisher=technical.get("publisher"),
        synopsis=synopsis or None,
        isbn=technical.get("isbn") or _meta(soup, "sku"),
        year=technical.get("year"),
        edition=technical.get("edition"),
        pages=technical.get("pages"),
        language=technical.get("language"),
        binding=technical.get("binding"),
        dimensions=technical.get("dimensions"),
        weight=technical.get("weight"),
        translator=technical.get("translator"),
        category=category,
        best_price=_sell_price(_meta(soup, "price")),
        cover_url=urljoin(config.BASE_URL, cover) if cover else None,
        technical_sheet=technical,
    )
