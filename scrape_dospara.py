import requests
from bs4 import BeautifulSoup
import time
import random

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; PriceTrackerBot/1.0; +https://toru-ubu.github.io/price-db-view/)"
}

def scrape_product(url):
    try:
        time.sleep(random.uniform(5, 10))  # サーバーに優しい間隔
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"⚠️ スキップ：{url}（{e}）")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')

    # 商品名取得
    name_tag = soup.select_one("h3.p-product-show-detail__product-name-area-product-name")
    name = name_tag.get_text(strip=True) if name_tag else ""

    # 価格取得
    price_tag = soup.select_one("span.num[itemprop='price']")
    price_str = price_tag['content'] if price_tag and price_tag.has_attr("content") else ""
    price = int(price_str) if price_str.isdigit() else None

    # スペック取得
    def get_text(cls):
        tag = soup.select_one(cls)
        return tag.get_text(strip=True) if tag else ""

    specs = {
        "OS": get_text("li.spec-os"),
        "CPU": get_text("li.spec-cpu"),
        "GPU": get_text("li.spec-gpu"),
        "メモリ": get_text("li.spec-memory"),
        "ストレージ": get_text("li.spec-strage")
    }

    # 🧠 形状判定（パンくずリスト）
    form_factor = "unknown"
    breadcrumb = soup.select("ul.c-breadcrumb__list li a")
    breadcrumb_texts = [a.get_text(strip=True) for a in breadcrumb]

    if any("ポータブル" in text for text in breadcrumb_texts):
        form_factor = "portable_gaming_pc"
    elif any("ノート" in text for text in breadcrumb_texts):
        form_factor = "notebook"
    elif any("デスクトップ" in text for text in breadcrumb_texts):
        form_factor = "desktop"

    return {
        "url": url,
        "name": name,
        "price": price,
        "specs": specs,
        "form_factor": form_factor
    }

# 🔍 動作確認用（直接実行時）
if __name__ == "__main__":
    urls = [
        "https://www.dospara.co.jp/TC30/MC16791-SN4808.html",
        "https://www.dospara.co.jp/TC30/MC15116.html"
    ]

    for url in urls:
        product = scrape_product(url)
        if product:
            from pprint import pprint
            pprint(product)
