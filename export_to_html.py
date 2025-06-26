import sqlite3
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === スプレッドシートから対象URLを取得 ===
def load_urls_from_sheet():
    SPREADSHEET_ID = "12H-PLrGe7NkrkJWPfkM0SHQ4g4Xe50yG2GoJOIvPFOE"
    SHEET_NAME = "urls"

    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your-service-account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return sheet.col_values(1)[1:]  # A列のURL（ヘッダー除く）

# === URL取得 ===
urls = load_urls_from_sheet()
placeholders = ",".join("?" for _ in urls)

# === DB接続 & データ取得 ===
conn = sqlite3.connect("/Users/tosakamidzuki/Desktop/price_tracker.db")
cursor = conn.cursor()

query = f"""
SELECT
  p.name,
  p.cpu,
  p.gpu,
  p.ram,
  p.storage,
  p.url,
  p.reference_price,
  pr.price,
  pr.point_return,
  pr.actual_price
FROM products p
JOIN (
  SELECT product_id, MAX(updated_at) as latest
  FROM prices
  GROUP BY product_id
) latest_price ON p.id = latest_price.product_id
JOIN prices pr ON pr.product_id = latest_price.product_id AND pr.updated_at = latest_price.latest
WHERE p.url IN ({placeholders})
ORDER BY pr.actual_price ASC
"""

cursor.execute(query, urls)
products = cursor.fetchall()
conn.close()

# === HTML構築 ===
html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>価格推移DB - 一覧</title>
<style>
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
th {{ background-color: #f2f2f2; }}
a {{ color: #1a0dab; text-decoration: none; }}
@media (max-width: 768px) {{
table {{ font-size: 14px; }}
td, th {{ padding: 4px; }}
}}
</style>
</head>
<body>
<h1>価格推移DB（{datetime.now().strftime("%Y-%m-%d")} 時点）</h1>
<table>
<thead>
<tr>
<th>商品名</th>
<th>通常価格</th>
<th>現在価格</th>
<th>ポイント還元</th>
<th>実質価格</th>
<th>割引率</th>
<th>買い時？</th>
<th>CPU</th>
<th>GPU</th>
<th>メモリ</th>
<th>ストレージ</th>
</tr>
</thead>
<tbody>
"""

# === 商品ごとにテーブル行を作成 ===
for name, cpu, gpu, ram, storage, url, reference_price, price, point_return, actual_price in products:
    # 割引率の計算（reference_priceがある場合）
    if reference_price and reference_price > 0:
        discount_rate = round((reference_price - price) / reference_price * 100, 1)
    else:
        discount_rate = 0

    # 買い時判定
    if discount_rate >= 20:
        buy_status = "🔥買い時！"
    elif discount_rate >= 10:
        buy_status = "👌まあまあお得"
    else:
        buy_status = "😐通常価格"

    # HTML行の組み立て
    html += f"""
<tr>
<td><a href="{url}" target="_blank">{name}</a></td>
<td>{f"{reference_price:,}円" if reference_price is not None else "-"}</td>
<td>{f"{price:,}円" if price is not None else "-"}</td>
<td>{f"{point_return}pt" if point_return is not None else "0pt"}</td>
<td>{f"{actual_price:,}円" if actual_price is not None else "-"}</td>
<td>{'-' if discount_rate <= 0 else f'-{discount_rate}%'}</td>
<td>{buy_status}</td>
<td>{cpu}</td>
<td>{gpu}</td>
<td>{ram}</td>
<td>{storage}</td>
</tr>
"""

# === HTMLクローズ ===
html += """
</tbody>
</table>
</body>
</html>
"""

# === ファイル保存 ===
with open("products.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTMLファイルを出力しました → products.html")
