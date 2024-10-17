
# 座標データを取得して出力結果をファイルに保存する関数
def get_position_data(file_name, target_date):
    # ファイル名の下2桁を使って年度を取得
    year_suffix = file_name[-6:-4]  # ファイル名の下2桁を取得 (例: '24' -> '2024')
    search_year = f" 20{year_suffix}"  # '20' + ファイル名の下2桁 (例: '24' -> '2024')

    found = False

    # ファイルを開いて座標データを検索・保存
    with open(file_name, 'r', encoding='utf-8') as file:

        for line in file:
            if line.startswith(search_year):  # 年度に基づいて行を探す

                # 行をスペースで分割
                parts = line.split()

                if len(parts) < 9:
                    continue

                # 日付が一致するか確認
                date = f"{parts[0]} {parts[1]} {parts[2]}"

                if date == target_date:
                    # 座標データを取得
                    x = float(parts[4])  # X座標
                    y = float(parts[5])  # Y座標
                    z = float(parts[6])  # Z座標
                    lat = float(parts[7])  # 緯度
                    lon = float(parts[8])  # 経度
                    # height = float(parts[9])  # 高さ


                    found = True
                    break

        if not found:
            message = "No data found for the given date.\n"
            print(message)

    # 結果のファイルパスと座標データを返す
    return x, y, z, lat, lon




