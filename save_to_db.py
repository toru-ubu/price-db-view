from scrape_dospara import scrape_product
from load_urls_from_sheet import load_urls_from_sheet
import sqlite3
from datetime import datetime

# URLを正規化する関数（末尾スラッシュ・前後空白を除去）
def normalize_url(url):
    return url.strip().rstrip("/")

# スクレイピング対象URLの読み込み（URLだけを正規化して取り出す）
urls = [normalize_url(url) for url, _ in load_urls_from_sheet()]

# DB接続
conn = sqlite3.connect("/Users/tosakamidzuki/Desktop/price_tracker.db")
cursor = conn.cursor()

# 商品ごとに処理
for url in urls:
    product = scrape_product(url)
    if product is None:
        print(f"⚠️ エラー: {url}（スクレイピングに失敗しました）")
        continue

    # URLを正規化
    product["url"] = normalize_url(product["url"])

    try:
        price = int(str(product["price"]).replace(",", "").replace("円", ""))
    except ValueError:
        print(f"⚠️ 価格が不正なためスキップ：{product['url']} → {product['price']}")
        continue

    # 商品がすでに登録されているかチェック
    cursor.execute("SELECT id FROM products WHERE url = ?", (product["url"],))
    result = cursor.fetchone()

    if result:
        product_id = result[0]
        # 🆕 form_factor を後付けで更新
        cursor.execute("""
            UPDATE products
            SET form_factor = ?
            WHERE id = ?
        """, (product.get("form_factor", "unknown"), product_id))
    else:
        # 新規商品として登録
        cursor.execute("""
            INSERT INTO products (
                name, maker, model_number,
                cpu, gpu, ram, storage,
                reference_price, url, thumbnail_url,
                form_factor
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product["name"],
            "",  # maker
            "",  # model_number
            product["specs"].get("CPU", ""),
            product["specs"].get("GPU", ""),
            product["specs"].get("メモリ", ""),
            product["specs"].get("ストレージ", ""),
            price,
            product["url"],
            "",  # thumbnail_url
            product.get("form_factor", "unknown")
        ))
        product_id = cursor.lastrowid

    # ✅ 日時で保存（%Y-%m-%d %H:%M:%S 形式）
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"🕒 保存予定の updated_at: {updated_at}")

    # prices テーブルに価格履歴を登録
    cursor.execute("""
        INSERT INTO prices (
            product_id, price, discount_rate, is_on_sale, updated_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        product_id,
        price,
        None,
        False,
        updated_at
    ))


    print(f"✅ 保存成功: {product['name']}（{price}円） - 形状: {product.get('form_factor')}")

# コミット＆クローズ
conn.commit()
conn.close()
