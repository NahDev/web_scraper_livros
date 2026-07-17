from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from shared.utils.http import HttpClient

from martins_fontes import config


@dataclass
class Category:
    category_id: int
    name: str
    url: str
    path_segments: list[str]


def _path_segments(url: str) -> list[str]:
    path = urlparse(url).path.strip("/")
    return [segment for segment in path.split("/") if segment]


def _flatten_livros(nodes: list[dict], collected: list[Category] | None = None) -> list[Category]:
    collected = collected if collected is not None else []
    for node in nodes:
        url = node.get("url") or ""
        segments = _path_segments(url)
        if segments and segments[0] == "livros" and len(segments) >= 2:
            collected.append(
                Category(
                    category_id=int(node["id"]),
                    name=node["name"],
                    url=url,
                    path_segments=segments,
                )
            )
        children = node.get("children") or []
        if children:
            _flatten_livros(children, collected)
    return collected


def fetch_categories(client: HttpClient, max_categories: int | None = None) -> list[Category]:
    response = client.get(f"{config.BASE_URL}{config.CATEGORY_TREE_PATH}")
    tree = response.json()
    livros = next((node for node in tree if node.get("name") == "Livros"), None)
    if livros is None:
        return []
    categories = _flatten_livros(livros.get("children") or [])
    # Prefer top-level categories (livros/<slug>) to avoid tiny subcategories first
    top_level = [item for item in categories if len(item.path_segments) == 2]
    ordered = top_level or categories
    if max_categories is not None:
        return ordered[:max_categories]
    return ordered
