# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def load_urls_from_sheet():
    # 認証情報とスコープを設定
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your-service-account.json", scope)
    client = gspread.authorize(creds)

    # シートを取得
    SPREADSHEET_NAME = "価格DB_URLリスト"
    sheet = client.open(SPREADSHEET_NAME).worksheet("urls")

    # 全データ（1行目のヘッダーを除く）
    rows = sheet.get_all_values()[1:]

    # URLとポイント還元をタプルで返す（ポイントが空欄でもOK）
    return [(row[0], row[1] if len(row) > 1 else "") for row in rows if row[0].strip()]

# 動作確認
if __name__ == "__main__":
    for url, pt in load_urls_from_sheet():
        print(f"{url} → {pt}")
