# -*- coding: utf-8 -*-
import subprocess

PYTHON_PATH = "/Users/tosakamidzuki/price-db-venv/bin/python"
DESKTOP_PATH = "/Users/tosakamidzuki/Desktop"

print("🚀 スクレイピングを開始します...")
subprocess.call([PYTHON_PATH, f"{DESKTOP_PATH}/save_to_db.py"])

print("🏷 キャンペーン適用処理を実行します...")
subprocess.call([PYTHON_PATH, f"{DESKTOP_PATH}/apply_campaigns.py"])

print("📝 HTMLを出力します...")
subprocess.call([PYTHON_PATH, f"{DESKTOP_PATH}/export_to_html.py"])

print("✅ 完了！")

subprocess.call(["git", "add", "products.html"])
subprocess.call(["git", "commit", "-m", "Update products.html"])
subprocess.call(["git", "push", "origin", "main"])

print("🚀 GitHubへの反映完了！ https://toru-ubu.github.io/price-db-view/products.html")
