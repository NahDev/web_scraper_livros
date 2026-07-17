from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BookCard(BaseModel):
    source_site: str
    product_url: str
    product_id: str | None = None
    title: str
    author: str | None = None
    category: str | None = None
    category_path: str | None = None
    list_price: float | None = None
    best_price: float | None = None
    cover_url: str | None = None
    scraped_at: datetime = Field(default_factory=utc_now)


class BookDetail(BaseModel):
    source_site: str
    product_url: str
    product_id: str | None = None
    title: str
    author: str | None = None
    publisher: str | None = None
    synopsis: str | None = None
    isbn: str | None = None
    year: str | None = None
    edition: str | None = None
    pages: str | None = None
    language: str | None = None
    binding: str | None = None
    dimensions: str | None = None
    weight: str | None = None
    translator: str | None = None
    category: str | None = None
    list_price: float | None = None
    best_price: float | None = None
    cover_url: str | None = None
    technical_sheet: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime = Field(default_factory=utc_now)


class BookSilver(BaseModel):
    source_site: str
    product_url: str
    product_id: str | None = None
    title: str
    author: str | None = None
    publisher: str | None = None
    synopsis: str | None = None
    isbn: str | None = None
    year: str | None = None
    edition: str | None = None
    pages: int | None = None
    language: str | None = None
    binding: str | None = None
    dimensions: str | None = None
    weight: str | None = None
    translator: str | None = None
    category: str | None = None
    category_path: str | None = None
    list_price: float | None = None
    best_price: float | None = None
    cover_url: str | None = None
    technical_sheet: dict[str, Any] = Field(default_factory=dict)
    scraped_at: datetime = Field(default_factory=utc_now)
