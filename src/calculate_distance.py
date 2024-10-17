import math
import glob
from geopy.distance import geodesic

def parse_pos_file(file_path):
    j_name = None
    coordinates = None
    target_date = " 2024 01 01 12:00:00"

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith(" J_NAME"):
                j_name = line.split()[1]
                print(f"Found J_NAME: {j_name}")  # J_NAMEを見つけたら表示
            if line.startswith(target_date):
                data = line.split()
                lat = float(data[7])
                lon = float(data[8])
                coordinates = (lat, lon)
                print(f"Found coordinates: {coordinates}")  # 座標を見つけたら表示
                break

    return j_name, coordinates

def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

kitaibaraki_coordinates = (36.800303696, 140.75393788)
pos_files = glob.glob("../data/coordinate/2024/*.pos")
distances = []

if not pos_files:
    print("No .pos files found in the directory.")  # .posファイルが見つからない場合

for file in pos_files:
    j_name, coordinates = parse_pos_file(file)
    if j_name and coordinates:
        if j_name != "北茨城":
            distance = calculate_distance(kitaibaraki_coordinates, coordinates)
            distances.append((j_name, distance))

if not distances:
    print("No distances calculated.")  # 距離が計算されなかった場合

distances.sort(key=lambda x: x[1])
for j_name, distance in distances:
    print(f"{j_name}: {distance:.2f} km")
