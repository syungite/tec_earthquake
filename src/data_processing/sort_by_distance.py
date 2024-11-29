import math
import glob
from geopy.distance import geodesic
#from map import read_locations_from_file
def parse_pos_file(file_path, year, month, day):
    month,day =10, 1
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
    return geodesic(coord1, coord2).kilometers

def process_pos_files(year, month, day, center_coordinate):
    pos_files = glob.glob(f"/home/blue/heki/data/coordinate/{year}/*.pos")
    distances = []

    if not pos_files:
        print("No .pos files found in the directory.")
        return

    for file in pos_files:
        j_name, coordinates, rinex = parse_pos_file(file, year, month, day)
        if j_name and coordinates:
            distance = calculate_distance(center_coordinate, coordinates)
            distances.append((j_name, distance, rinex, coordinates))

    if not distances:
        print("No distances calculated.")
        return

    distances.sort(key=lambda x: x[1])
    # 結果をlist.txtに書き出し
    with open("/home/blue/heki/data/list.txt", 'w', encoding='utf-8') as f:
        for cnt, (j_name, distance, rinex, coordinates) in enumerate(distances):
            #if cnt < 52 and rinex != '1176':
            if cnt < 34 and rinex != '1170' and rinex != '0761' and rinex != '0351':
            #if cnt < 31:
                print(f"{j_name}: {rinex}")
                f.write(f"{j_name}: {rinex}\n")
                #lat, lon = coordinates
                #f.write(f"{lat}, {lon}\n")


    # 結果をmap.txtに座標形式で書き出し
    with open("/home/blue/heki/data/map.txt", 'w', encoding='utf-8') as f:
        for cnt, (j_name, _, rinex, coordinates) in enumerate(distances):
            #if cnt < 52 and rinex != '1176':
            if cnt < 33 and rinex != '1170' and rinex != '0761':
                lat, lon = coordinates
                f.write(f"{lat}, {lon}, {j_name}\n")

# 単独で実行された場合
if __name__ == "__main__":
    year, month, day = 2011, 3, 11
    center_coordinate = (3.6800309526E+01,  1.4075391238E+02)
    process_pos_files(year, month, day, center_coordinate)
    #read_locations_from_file("../../data/map.txt")


