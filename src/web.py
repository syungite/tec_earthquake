import requests
from bs4 import BeautifulSoup
import pandas as pd

# スクレイピングするURL
url = "https://terras.gsi.go.jp/observation_code.php#name1"  # 対象のURLを入力

# ページを取得
response = requests.get(url)
response.raise_for_status()

# HTML解析
soup = BeautifulSoup(response.text, 'html.parser')

# 表を取得
table = soup.find('table')

# 表ヘッダー（列名）
headers = ['ID', 'Code', 'Location', 'Prefecture', 'Site', 'Receiver', 'Antenna']

# データを抽出
data = []
rows = table.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [col.text.strip() for col in cols]
    if cols:
        data.append(cols)

# データフレームに変換
df = pd.DataFrame(data, columns=headers)

# デバッグ出力
print("Headers:", headers)
print("Data example:", data[:5])

# Excelに保存
excel_path = 'output.xlsx'
df.to_excel(excel_path, index=False)
print(f"データが {excel_path} に保存されました。")

# CSVに保存
csv_path = 'output.csv'
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"データが {csv_path} に保存されました。")


