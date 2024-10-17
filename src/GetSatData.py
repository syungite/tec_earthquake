# GetSatData.py
import os

def read_satellite_data(file_path):
    # 衛星データを読み込み、衛星番号ごとに並び替える
    satellite_data = {}

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 5:  # 必要なデータが足りない場合はスキップ
                continue

            # データを取得
            ut_time = float(parts[0])  # 時刻
            sat_num = int(parts[1])     # 衛星番号
            x = float(parts[2].replace('D', 'E'))         # X座標
            y = float(parts[3].replace('D', 'E'))         # Y座標
            z = float(parts[4].replace('D', 'E'))         # Z座標

            # 衛星番号ごとにデータを保存
            if sat_num not in satellite_data:
                satellite_data[sat_num] = []
            satellite_data[sat_num].append((ut_time, x, y, z))

    return satellite_data

def save_sorted_data(satellite_data, output_file_path):
    # 衛星データをファイルに保存する
    with open(output_file_path, 'w') as file:
        for sat_num in sorted(satellite_data.keys()):
            for data in satellite_data[sat_num]:
                ut_time, x, y, z = data
                file.write(f"{ut_time} {sat_num} {x} {y} {z}\n")

def get_satellite_data(file_path):
    satellite_data = read_satellite_data(file_path)
    return satellite_data

# メインの処理
if __name__ == "__main__":
    input_file = input("処理する .txt ファイル名を入力してください: ")
    output_file = input("出力ファイル名を入力してください (default: sorted_data.txt): ")
    if not output_file:
        output_file = "sorted_data.txt"
    
    satellite_data = get_satellite_data(input_file)
    save_sorted_data(satellite_data, output_file)
    print(f"衛星データが {output_file} に保存されました。")

