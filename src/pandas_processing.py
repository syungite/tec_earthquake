import pandas as pd

# 入力ファイルと出力ファイル名
input_file = '/home/blue/heki/src/output.csv'  # 入力ファイル

output_file = 'selected_stations.csv'  # 出力ファイル

# 抽出対象の局名称リスト
target_stations = [
    "宮崎", "広島福山２", "高山", "小渕沢", "富士山"
    "千葉市川", "女川", "京都伏見", "硫黄島１"
]

# CSVデータを読み込む
df = pd.read_csv(input_file)  # ヘッダー行を調整

# 条件に一致する行を抽出
filtered_df = df[df['Location'].isin(target_stations)]

# 必要な列（例: 局番号と局名称）を選択
result_df = filtered_df[['ID', 'Location']]

# 抽出結果を保存
result_df.to_csv(output_file, index=False, encoding='utf-8')

print(f"抽出されたデータを {output_file} に保存しました。")
