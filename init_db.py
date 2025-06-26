import sqlite3

conn = sqlite3.connect("price_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    maker TEXT,
    model_number TEXT,
    cpu TEXT,
    gpu TEXT,
    ram TEXT,
    storage TEXT,
    reference_price INTEGER,
    url TEXT,
    thumbnail_url TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    price INTEGER NOT NULL,
    discount_rate REAL,
    is_on_sale BOOLEAN,
    updated_at DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
""")

conn.commit()
conn.close()

print("✅ データベースとテーブルを作成しました！")
