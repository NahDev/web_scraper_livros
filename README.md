# Multi-bookstore scraper (bronze → silver → gold)

## Sites
- `martins_fontes` — implemented (VTEX API)
- `livraria_da_vila` — implemented (VTEX API)
- `travessa` — implemented (HTML)
- `livrarias_curitiba` — implemented (VTEX API)

## Layers
- **Bronze**: raw listings (`data/bronze/<site>/listings`) and product details (`data/bronze/<site>/products`)
- **Silver**: cleaned joined records (`data/silver/<site>`)
- **Gold**: SQLite ready for ML (`data/gold/books.db`)

## Run Martins Fontes
```bash
uv sync
uv run martins-fontes
```

Limited by default (1 category, 1 page, 10 products). Full scrape:
```bash
uv run martins-fontes --full
```

Custom limits:
```bash
uv run martins-fontes --max-categories 2 --max-pages-per-category 1 --max-products 20
```

## Run Livraria da Vila
```bash
uv run livraria-da-vila
```

Full scrape:
```bash
uv run livraria-da-vila --full
```

Custom limits:
```bash
uv run livraria-da-vila --max-categories 2 --max-pages-per-category 1 --max-products 20
```

## Run Livrarias Curitiba
```bash
uv run livrarias-curitiba
```

Full scrape:
```bash
uv run livrarias-curitiba --full
```

Custom limits:
```bash
uv run livrarias-curitiba --max-categories 2 --max-pages-per-category 1 --max-products 20
```

## Run Livraria Travessa
```bash
uv run livraria-travessa
```

Full scrape:
```bash
uv run livraria-travessa --full
```

Custom limits:
```bash
uv run livraria-travessa --max-categories 2 --max-pages-per-category 1 --max-products 20
```

Or:
```bash
uv run python main.py
```
