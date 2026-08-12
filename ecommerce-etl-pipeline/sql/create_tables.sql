-- Products table. sku is unique so re-running the DAG updates existing
-- rows instead of creating duplicates (idempotency requirement).
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    product_url VARCHAR(1000) NOT NULL,
    image_url VARCHAR(1000),
    price_current NUMERIC(10, 2),
    price_original NUMERIC(10, 2),
    stock_quantity INTEGER,
    in_stock BOOLEAN,
    category VARCHAR(255),
    scraped_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Variants table. A product can have zero or more variants (size, color,
-- etc). scrapeme.live products don't have real variants, so this stays
-- empty for them - the pipeline should handle that gracefully rather
-- than failing.
CREATE TABLE IF NOT EXISTS product_variants (
    id SERIAL PRIMARY KEY,
    product_sku VARCHAR(100) NOT NULL REFERENCES products(sku) ON DELETE CASCADE,
    variant_type VARCHAR(50),
    variant_value VARCHAR(255),
    variant_stock INTEGER,
    UNIQUE (product_sku, variant_type, variant_value)
);

CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_variants_product_sku ON product_variants(product_sku);
