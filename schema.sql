-- schema.sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    step TEXT NOT NULL,          -- e.g. 'cleanser', 'serum', 'moisturizer', 'sunscreen'
    skin_types TEXT NOT NULL,    -- e.g. 'oily,dry', 'combination,sensitive'
    concerns TEXT NOT NULL,      -- e.g. 'acne,hyperpigmentation'
    fragrance_free INTEGER,      -- 1 = yes, 0 = no
    cruelty_free INTEGER,        -- 1 = yes, 0 = no
    price REAL,
    url TEXT                     -- product’s online page
);