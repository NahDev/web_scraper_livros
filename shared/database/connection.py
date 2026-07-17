from pathlib import Path

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    select,
)
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

from shared.models import BookSilver
from shared.storage.bronze_silver import DATA_DIR

metadata = MetaData()

books_table = Table(
    "books",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_site", String(64), nullable=False),
    Column("product_url", String(512), nullable=False, unique=True),
    Column("product_id", String(64)),
    Column("title", String(512), nullable=False),
    Column("author", String(512)),
    Column("publisher", String(256)),
    Column("synopsis", Text),
    Column("isbn", String(32)),
    Column("year", String(32)),
    Column("edition", String(128)),
    Column("pages", Integer),
    Column("language", String(64)),
    Column("binding", String(64)),
    Column("dimensions", String(64)),
    Column("weight", String(64)),
    Column("translator", String(256)),
    Column("category", String(256)),
    Column("category_path", String(512)),
    Column("list_price", Float),
    Column("best_price", Float),
    Column("cover_url", String(512)),
    Column("technical_sheet", Text),
    Column("scraped_at", DateTime),
)


def get_engine(database_path: Path | None = None) -> Engine:
    path = database_path or (DATA_DIR / "gold" / "books.db")
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}", future=True)


def init_database(engine: Engine | None = None) -> Engine:
    database = engine or get_engine()
    metadata.create_all(database)
    return database


def upsert_books(books: list[BookSilver], engine: Engine | None = None) -> int:
    database = engine or init_database()
    if not books:
        return 0

    rows = []
    for book in books:
        payload = book.model_dump(mode="python")
        payload["technical_sheet"] = str(payload.get("technical_sheet") or {})
        rows.append(payload)

    statement = sqlite_insert(books_table).values(rows)
    update_columns = {
        column.name: statement.excluded[column.name]
        for column in books_table.columns
        if column.name not in {"id", "product_url"}
    }
    statement = statement.on_conflict_do_update(
        index_elements=["product_url"],
        set_=update_columns,
    )
    with database.begin() as connection:
        connection.execute(statement)
    return len(rows)


def count_books(engine: Engine | None = None) -> int:
    database = engine or get_engine()
    with database.connect() as connection:
        return int(connection.execute(select(func.count()).select_from(books_table)).scalar_one())
