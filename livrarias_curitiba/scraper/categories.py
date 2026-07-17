from dataclasses import dataclass
from urllib.parse import urlparse

from shared.utils.http import HttpClient

from livrarias_curitiba import config


@dataclass
class Category:
    category_id: int
    name: str
    url: str
    path_segments: list[str]


def _leaf_categories(nodes: list[dict]) -> list[Category]:
    categories: list[Category] = []
    for node in nodes:
        children = node.get("children") or []
        if children:
            categories.extend(_leaf_categories(children))
            continue

        url = node["url"]
        categories.append(
            Category(
                category_id=int(node["id"]),
                name=node["name"],
                url=url,
                path_segments=[
                    segment
                    for segment in urlparse(url).path.strip("/").split("/")
                    if segment
                ],
            )
        )
    return categories


def fetch_categories(client: HttpClient, max_categories: int | None = None) -> list[Category]:
    tree = client.get(f"{config.BASE_URL}{config.CATEGORY_TREE_PATH}").json()
    books = next((node for node in tree if node.get("name") == "Livros"), None)
    if books is None:
        return []

    categories = _leaf_categories(books.get("children") or [])
    return categories[:max_categories] if max_categories is not None else categories
