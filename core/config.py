class Config:
    DYNAMIC_PAGE_PATTERNS = [
        "react", "angular", "vue", "jquery", "ajax", "window.__INITIAL_STATE__",
        "window.__APP_INITIAL_STATE__"
    ]

    DEFAULT_PRODUCT_PATTERNS = [
        r'/itm/[\d]+',
        r'/p/[\w-]+',
        r'/item/[\w-]+',
        r'/products/[\w-]+',
        r'/dp/[\w-]+',
        r'itm\?[^"]*',
        r'/[\w-]+/p/[\w-]+',
        r'/[\w-]+/itm/[\d]+',
        r'/[\w-]+/item/[\w-]+',
    ]
