import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from shared.models import BookCard, BookDetail, BookSilver

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def _run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _write_jsonl(path: Path, records: Iterable[object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for record in records:
            payload = record.model_dump(mode="json") if hasattr(record, "model_dump") else record
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return path


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_bronze_listings(site: str, cards: list[BookCard], run_id: str | None = None) -> Path:
    stamp = run_id or _run_stamp()
    path = DATA_DIR / "bronze" / site / "listings" / f"{stamp}.jsonl"
    return _write_jsonl(path, cards)


def save_bronze_products(site: str, details: list[BookDetail], run_id: str | None = None) -> Path:
    stamp = run_id or _run_stamp()
    path = DATA_DIR / "bronze" / site / "products" / f"{stamp}.jsonl"
    return _write_jsonl(path, details)


def save_silver_books(site: str, books: list[BookSilver], run_id: str | None = None) -> Path:
    stamp = run_id or _run_stamp()
    path = DATA_DIR / "silver" / site / f"{stamp}.jsonl"
    return _write_jsonl(path, books)


def latest_jsonl(folder: Path) -> Path | None:
    files = sorted(folder.glob("*.jsonl"))
    return files[-1] if files else None


def load_bronze_listings(site: str, path: Path | None = None) -> list[BookCard]:
    target = path or latest_jsonl(DATA_DIR / "bronze" / site / "listings")
    if target is None:
        return []
    return [BookCard.model_validate(item) for item in _read_jsonl(target)]


def load_bronze_products(site: str, path: Path | None = None) -> list[BookDetail]:
    target = path or latest_jsonl(DATA_DIR / "bronze" / site / "products")
    if target is None:
        return []
    return [BookDetail.model_validate(item) for item in _read_jsonl(target)]


def load_silver_books(site: str, path: Path | None = None) -> list[BookSilver]:
    target = path or latest_jsonl(DATA_DIR / "silver" / site)
    if target is None:
        return []
    return [BookSilver.model_validate(item) for item in _read_jsonl(target)]
