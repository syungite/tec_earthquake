# CalVTEC.py
import os
import math
import numpy as np
from GetPositionData import get_position_data
from GetSatData import get_satellite_data

def calculate_vector(a, b, c, lat, lon):
    # 弧度法に変換
    rlat = math.radians(lat)
    rlon = math.radians(lon)

    # 基準となるベクトルを生成
    NN = np.array([-math.sin(rlat) * math.cos(rlon), -math.sin(rlat) * math.sin(rlon), math.cos(rlat)])
    NE = np.array([-math.sin(rlon), math.cos(rlon), 0])
    OR = np.array([a, b, c])
    
    return NN, NE, OR

def extract_sat_data_from_stec(sat_number, stec_file):
    data = []
    with open(stec_file, 'r', encoding='utf-8') as file:
        extracting = False
        for line in file:
            cleaned_line = line.strip()  # Remove leading and trailing spaces

            # Check for satellite number
            if cleaned_line.startswith(f"> sat#{sat_number}"):
                extracting = True
            elif cleaned_line.startswith("> sat#"):
                extracting = False

            # Process data lines
            if extracting and not cleaned_line.startswith("> sat#"):
                parts = cleaned_line.split()
                if len(parts) == 2:  # Check if there are time and value
                    try:
                        time = float(parts[0])  # Convert time to float
                        value = float(parts[1])  # Convert value to float
                        f1 = 1575.42
                        f2 = 1227.60
                        stec = value * (f1 * f2)**2 / (f1**2 - f2**2)  # Calculate STEC
                        data.append((time, stec))  # Add data to the list
                    except ValueError:
                        # Invalid data line, skip
                        continue

    return data




def find_nearest_time_blocks(ctheta_time, stec_data):
    """
    cthetaの時間範囲に基づいて、STECデータのうちその範囲にあるものを見つける
    """
    block_size = 0.05  # 3分間 (0.05時間)の時間ブロック
    nearest_stec = []
    for stec_time, stec_value in stec_data:
        if abs(stec_time - ctheta_time) <= block_size:  # ctheta_timeに近い範囲を探す
            nearest_stec.append((stec_time, stec_value))
    return nearest_stec

def main():
    # 衛星データファイルを取得　satTest.py
    sat_file = input("処理する .txt ファイル名(衛星)を入力してください: ")
    
    # GetPositionData.py から座標データを取得
    file_name = input("Enter the relative path of the file (default: ../data/00R015.24.pos): ")
    target_date = input("Enter the target date (YYYY MM DD): ")
    position = input("Enter the position: ")

    # 座標データを取得
    x, y, z, lat, lon = get_position_data(file_name, target_date, position)

    # 取得した座標データを使ってベクトルを計算
    NN, NE, OR = calculate_vector(x, y, z, lat, lon)

    # GetSatData.py を呼び出し、衛星データを取得
    satellite_data = get_satellite_data(sat_file)


    # STECファイルからsat# 26のデータを抽出
    stec_file = input("PATH to STEC file")
    sat_number = input("SELECT satellite number")
    stec_data = extract_sat_data_from_stec(sat_number, stec_file)

    # define R and Hiono
    R = 6371
    hiono = 300

    # Prepare data for output
    output_data = []

    # OR との計算を行い RS を求める
    for sat_num, data in satellite_data.items():
        if str(sat_num) != sat_number:  # 衛星番号が一致しない場合はスキップ
            continue
        for ut_time, x_sat, y_sat, z_sat in data:
            RS = np.array([x_sat, y_sat, z_sat]) - OR
            # RS の長さを計算
            rs_length = np.linalg.norm(RS)

            # NN と NE のドット積を計算
            nn_dot = np.dot(NN, RS)  # NN と RS のドット積
            ne_dot = np.dot(NE, RS)  # NE と RS のドット積

             # ctheta を計算
            ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length if rs_length != 0 else 0
            # print(f"ctheta: {ctheta},ut_time: {ut_time}, nn_dot: {nn_dot}, ne_dot: {ne_dot}")
            # value_inside_sqrt = 1 - (R * ctheta / (R + hiono)) ** 2
            # print(f"value inside sqrt: {value_inside_sqrt}, ctheta: {ctheta}, R: {R}, hiono: {hiono},nn_dot: {nn_dot}")

            # if value_inside_sqrt < 0:
            #     print("Math domain error detected.")
            #     print(f"ctheta: {ctheta}, value_inside_sqrt: {value_inside_sqrt}")
            #     exit()  # エラーが出た場合、プログラムを終了させる

            cphi = math.sqrt(1-(R*ctheta/(R+hiono))**2)

            # STECデータのうち、cthetaの時間に対応するデータを取得
            relevant_stec = find_nearest_time_blocks(ut_time, stec_data)

            # 抽出したSTECデータとcthetaを掛ける
            for stec_time, stec_value in relevant_stec:
                vtec = stec_value * cphi
                output_data.append((stec_time, vtec))  # Store the results for output
                # print(f"衛星番号: {sat_num}, 時刻: {stec_time}, STEC: {stec_value}, cphi: {cphi}, vtec: {vtec}")

    # 出力ファイルのパスを指定
    output_file_path = os.path.join('..','data', 'vtec.txt')
    
    # 出力先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w') as output_file:
        # vtecのデータを保存する処理をここに追加
        for stec_time, vtec in output_data:  # resultsリストを使用
            output_file.write(f"{stec_time} {vtec}\n")

    print(f"Results saved to {output_file_path}")

if __name__ == "__main__":
    main()





