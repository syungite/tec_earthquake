import os

# 座標データを取得して出力結果をファイルに保存する関数
def get_position_data(file_name, target_date, Position):
    # ファイル名の下2桁を使って年度を取得
    year_suffix = file_name[-6:-4]  # ファイル名の下2桁を取得 (例: '24' -> '2024')
    search_year = f" 20{year_suffix}"  # '20' + ファイル名の下2桁 (例: '24' -> '2024')

    # 保存するファイル名を生成し、dataディレクトリに保存
    output_file_name = f"{Position}_{target_date.replace(' ', '_')}.txt"
    output_file_path = os.path.join("..", "data", output_file_name)

    found = False

    with open(file_name, 'r', encoding='utf-8') as file, open(output_file_path, 'w', encoding='utf-8') as output_file:
        print("File opened successfully.")
        output_file.write(f"Results for date: {target_date}\n")
        output_file.write(f"Source file: {file_name}\n\n")

        for line in file:
            if line.startswith(search_year):  # 年度に基づいて行を探す

                # 行をスペースで分割
                parts = line.split()

                if len(parts) < 9:
                    print("Not enough data in line:", line.strip())
                    output_file.write(f"Not enough data in line: {line.strip()}\n")
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
                    height = float(parts[9])  # 高さ

                    # 結果を出力
                    result = (
                        f"Date: {date}\n"
                        f"X (m): {x}\n"
                        f"Y (m): {y}\n"
                        f"Z (m): {z}\n"
                        f"Latitude (deg): {lat}\n"
                        f"Longitude (deg): {lon}\n"
                        f"Height (m): {height}\n"
                    )
                    print(result)
                    output_file.write(result)

                    found = True
                    break

        if not found:
            message = "No data found for the given date.\n"
            print(message)
            output_file.write(message)

    print(f"Results saved to {output_file_path}")
    return x,y,z,lat,lon 


# メインの処理
if __name__ == "__main__":
    # ファイル名の入力（デフォルトのパスを使用）
    file_name = input("Enter the relative path of the file (default: ../data/00R015.24.pos): ")
    if not file_name:
        file_name = os.path.join("..", "data", "00R015.24.pos")

    # ターゲット日付の入力
    target_date = input("Enter the target date (YYYY MM DD): ")
    Position = input("Enter the position: ")

    # 座標データを取得してファイルに保存
    get_position_data(file_name, target_date, Position)

