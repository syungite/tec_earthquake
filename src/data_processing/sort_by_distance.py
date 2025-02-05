import math
import glob
from geopy.distance import geodesic

# 除外するRINEXコードが書かれたファイルを読み込む
def load_excluded_rinex(file_path):
    excluded_rinex = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            excluded_rinex.add(line.strip())  # 改行や空白を除去
    return excluded_rinex

def parse_pos_file(file_path, year, month, day):
    month, day = 10, 1
    """POSファイルの解析"""
    j_name = None
    coordinates = None
    rinex = None  # rinexの初期化
    target_date = f" {year} {str(month).zfill(2)} {str(day).zfill(2)} 12:00:00"

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(" J_NAME"):
                j_name = line.split()[1]
            if line.startswith(" RINEX"):
                rinex = line.split()[1]
            if line.startswith(target_date):
                data = line.split()
                lat = float(data[7])
                lon = float(data[8])
                coordinates = (lat, lon)
                break

    return j_name, coordinates, rinex

def calculate_distance(coord1, coord2):
    """2地点間の距離を計算"""
    return geodesic(coord1, coord2).kilometers

def process_pos_files(year, month, day, center_coordinate, excluded_rinex_file):
    """
    POSファイルを処理し、距離を計算
    緯度、経度から2地点間の距離を求める
    """
    pos_files = glob.glob(f"/home/blue/tec_earthquake/data/coordinate/{year}/*.pos")
    distances = []

    if not pos_files:
        print("No .pos files found in the directory.")
        return

    # 除外リストを読み込む
    excluded_rinex = load_excluded_rinex(excluded_rinex_file)

    for file in pos_files:
        j_name, coordinates, rinex = parse_pos_file(file, year, month, day)
        if j_name and coordinates and rinex not in excluded_rinex:
            distance = calculate_distance(center_coordinate, coordinates)
            distances.append((j_name, distance, rinex, coordinates))

    if not distances:
        print("No distances calculated.")
        return

    distances.sort(key=lambda x: x[1])

    # 結果をlist.txtに書き出し
    with open("/home/blue/tec_earthquake/data/list.txt", 'w', encoding='utf-8') as f:
        cnt = 0
        for j_name, distance, rinex, coordinates in distances:
            if cnt < 50 and rinex not in excluded_rinex:  # 最大40行
                print(f"{j_name}: {rinex}")
                f.write(f"{j_name}: {rinex}\n")
                cnt += 1

    # 結果をmap.txtに座標形式で書き出し
    with open("/home/blue/tec_earthquake/data/map.txt", 'w', encoding='utf-8') as f:
        cnt = 0
        for j_name, _, rinex, coordinates in distances:
            if cnt < 50 and rinex not in excluded_rinex:  # 除外リストに入っているコードをスキップ
                lat, lon = coordinates
                f.write(f"{lat}, {lon}, {j_name}\n")
                cnt += 1

# 単独で実行された場合
if __name__ == "__main__":
    year, month, day = 2011, 3, 11
    center_coordinate = (3.6800309526E+01,  1.4075391238E+02)
    excluded_rinex_file = '/home/blue/tec_earthquake/data/excluded_rinex.txt'  # 除外リストファイル
    process_pos_files(year, month, day, center_coordinate, excluded_rinex_file)



