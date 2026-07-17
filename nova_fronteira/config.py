SOURCE_SITE = "nova_fronteira"
BASE_URL = "https://www.novafronteira.com.br"
CATALOG_PATH = "/livros"
REQUEST_DELAY_SECONDS = 0.35

# Collections that are not real book categories
IGNORED_SLUGS = {
    "precos",
    "baixou",
    "ocultar",
    "pod",
    "conexao-literaria",
    "selecao_especial",
    "selecao-de-boxes",
    "kits-especiais",
}

DEFAULT_MAX_CATEGORIES = 1
DEFAULT_MAX_PAGES_PER_CATEGORY = 1
DEFAULT_MAX_PRODUCTS = 10
