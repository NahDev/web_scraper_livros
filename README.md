# Multi-bookstore book scraper

Python scraper that catalogs books from Brazilian bookstores and processes the
results through Bronze, Silver, and Gold data layers. It collects listing cards,
visits each product page, normalizes book metadata, and stores the final records
in SQLite for analysis or machine-learning workflows.

## Supported bookstores

- **Martins Fontes Paulista** (`martins_fontes`) — VTEX catalog API.
- **Livraria da Vila** (`livraria_da_vila`) — VTEX catalog API, including
  pagination beyond the platform's standard result window.
- **Livrarias Curitiba** (`livrarias_curitiba`) — VTEX catalog API.
- **Livraria da Travessa** (`travessa`) — HTML category, listing, and product
  page parsing.
- **Editora Nova Fronteira** (`nova_fronteira`) — Loja Integrada HTML and
  schema.org metadata parsing.

Each bookstore module contains:

- `config.py`: URLs, request delay, page size, and default execution limits.
- `scraper/categories.py`: category discovery.
- `scraper/listings.py`: pagination and listing-card collection.
- `scraper/products.py`: product-page collection.
- `parsers/`: bookstore-specific response parsing.
- `start.py`: complete Bronze → Silver → Gold pipeline.

## Data architecture

### Bronze

Preserves the data collected from the source in JSON Lines format:

```text
data/bronze/<site>/listings/<run_id>.jsonl
data/bronze/<site>/products/<run_id>.jsonl
```

Listing and product-page records remain separate so the original extraction
results can be inspected or reprocessed.

### Silver

Joins listing cards with product details, removes duplicate product URLs,
cleans HTML, normalizes page counts and years, and applies a common schema:

```text
data/silver/<site>/<run_id>.jsonl
```

Fields include title, author, publisher, synopsis, ISBN, year, edition, pages,
language, binding, dimensions, weight, translator, category, prices, cover URL,
technical sheet, source URL, and extraction timestamp.

### Gold

Upserts normalized books by product URL into:

```text
data/gold/books.db
```

The SQLite database is shared by all bookstore pipelines and is ready for SQL
queries, analytics, or downstream machine-learning preparation.

Generated data and database files are excluded from Git.

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- Internet access to the supported storefronts

## Installation

```bash
git clone git@github.com:NahDev/web_scraper_livros.git
cd web_scraper_livros
uv sync
```

## Usage

Runs are limited by default to one category, one page per category, and ten
product pages. This provides a safe smoke test before a full extraction.

Run any bookstore:

```bash
uv run martins-fontes
uv run livraria-da-vila
uv run livrarias-curitiba
uv run livraria-travessa
uv run nova-fronteira
```

Run every available category, page, and product:

```bash
uv run martins-fontes --full
uv run livraria-da-vila --full
uv run livrarias-curitiba --full
uv run livraria-travessa --full
uv run nova-fronteira --full
```

Set custom limits:

```bash
uv run nova-fronteira \
  --max-categories 2 \
  --max-pages-per-category 3 \
  --max-products 50
```

The same options are available for every bookstore command:

- `--max-categories`: maximum number of categories to process.
- `--max-pages-per-category`: maximum listing pages per category.
- `--max-products`: maximum product pages to visit.
- `--full`: removes all three limits.

`main.py` is a shortcut for the default Martins Fontes run:

```bash
uv run python main.py
```

## Shared modules

- `shared/models.py`: Pydantic models for listing, product-detail, and normalized
  book records.
- `shared/utils/http.py`: HTTP client with request throttling, redirects,
  timeouts, and exponential retries.
- `shared/storage/bronze_silver.py`: JSONL persistence and loading.
- `shared/silver.py`: common cleaning, merging, and normalization.
- `shared/database/connection.py`: SQLAlchemy schema and SQLite upserts.
- `shared/utils/logging.py`: consistent English-language logs.

## Project structure

```text
.
├── livraria_da_vila/
├── livrarias_curitiba/
├── martins_fontes/
├── nova_fronteira/
├── travessa/
├── shared/
│   ├── database/
│   ├── storage/
│   └── utils/
├── data/                  # generated locally and ignored by Git
├── main.py
└── pyproject.toml
```

## Responsible use

The scrapers include request delays and retries. Before running a full
extraction, review each website's terms of service and robots policy, keep the
configured throttling enabled, and avoid unnecessary repeated requests.
