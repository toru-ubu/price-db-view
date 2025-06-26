# -*- coding: utf-8 -*-

import sqlite3
import datetime
from load_urls_from_sheet import load_urls_from_sheet

# データベースのパス
DB_PATH = "/Users/tosakamidzuki/Desktop/price_tracker.db"

# スプレッドシートからURLとポイント還元額のマップを取得
url_point_map = {
    url: pt for url, pt in load_urls_from_sheet()
}

# 大還元祭のポイント付与条件（閾値：還元pt）
bonus_campaign_thresholds = [
    (800000, 100000),
    (700000, 60000),
    (600000, 50000),
    (500000, 40000),
    (400000, 30000),
    (300000, 20000),
    (200000, 15000),
    (100000, 10000),
]

# DB接続
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 各商品の最新価格データを取得
cursor.execute("""
SELECT
    p.id,
    p.name,
    p.url,
    p.form_factor,
    p.reference_price,
    pr.id,
    pr.price
FROM products p
JOIN prices pr ON p.id = pr.product_id
WHERE pr.updated_at = (
    SELECT MAX(updated_at)
    FROM prices
    WHERE product_id = p.id
)
""")

rows = cursor.fetchall()

for prod_id, name, url, form_factor, reference_price, price_id, price in rows:
    summer_point = url_point_map.get(url)
    selected_campaign = None
    selected_point = 0

    # ① 夏のボーナス先取りキャンペーン（スプレッドシートに値がある）
    if summer_point:
        selected_campaign = "夏のボーナス先取りキャンペーン"
        selected_point = int(float(summer_point.replace(",", "")))

    # ② 決算先取り大還元祭（GALLERIAデスクトップ、10万円以上）
    elif "galleria" in name.lower() and form_factor == "desktop" and price >= 100000:
        for threshold, pt in bonus_campaign_thresholds:
            if price >= threshold:
                selected_campaign = "決算先取り大還元祭"
                selected_point = pt
                break

    # 更新処理（実質価格・割引率も保存）
    if selected_campaign and selected_point:
        actual_price = price - selected_point

        # 割引率計算（参考価格が有効なときのみ）
        discount_rate = None
        if reference_price and reference_price > 0:
            discount_rate = round((reference_price - actual_price) / reference_price * 100, 1)

        cursor.execute("""
        UPDATE prices
        SET point_return = ?, campaign_name = ?, actual_price = ?, discount_rate = ?
        WHERE id = ?
        """, (selected_point, selected_campaign, actual_price, discount_rate, price_id))

        print("🏷 適用: {} → {}（{}pt / 実質 ¥{} / 割引率 {}%）".format(
            name, selected_campaign, selected_point, actual_price,
            f"{discount_rate:.1f}" if discount_rate is not None else "N/A"))

# コミット＆クローズ
conn.commit()
conn.close()


