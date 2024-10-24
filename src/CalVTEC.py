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
                        f1 = 1.57542
                        f2 = 1.22760
                        stec = value * (f1 * f2)**2 /((f1**2 - f2**2)*40.308)*100  # Calculate STEC
                        data.append((time, stec))  # Add data to the list
                    except ValueError:
                        # Invalid data line, skip
                        continue

    return data

def find_nearest_time_blocks(ctheta_time, input_obs):
    """
    Find STEC data within a time window centered around ctheta_time.
    """
    block_size = 0.05  # Time block size of 0.05 hours (3 minutes)
    half_block = block_size / 2  # Time block will extend 1.5 minutes before and after ctheta_time
    nearest_stec = []
    
    for stec_time, stec_value in input_obs:
        if abs(stec_time - ctheta_time) <= half_block:  # Check within the half-block range
            nearest_stec.append((stec_time, stec_value))
    
    return nearest_stec


def calculate_vtec(input_nav, input_obs ,input_pos, output_file_path, target_date):

    # 座標データを取得
    x, y, z, lat, lon = get_position_data(input_pos, target_date)

    # 取得した座標データを使ってベクトルを計算
    NN, NE, OR = calculate_vector(x, y, z, lat, lon)

    # GetSatData.py を呼び出し、衛星データを取得
    satellite_data = get_satellite_data(input_nav)


    # STECファイルからsat# 26のデータを抽出
    #stec_file = input("PATH to STEC file")
    sat_number = 26
    obs_data = extract_sat_data_from_stec(sat_number, input_obs)
    # define R and Hiono
    R = 6371
    hiono = 300

    # Prepare data for output
    output_data = []

    # OR との計算を行い RS を求める
    for sat_num, data in satellite_data.items():
        if sat_num != sat_number:  # 衛星番号が一致しない場合はスキップ
            continue
        for ut_time, x_sat, y_sat, z_sat in data:
            # print(f"UT time: {ut_time}")
            RS = np.array([x_sat, y_sat, z_sat]) - OR
            # RS の長さを計算
            rs_length = np.linalg.norm(RS)

            # NN と NE のドット積を計算
            nn_dot = np.dot(NN, RS)  # NN と RS のドット積
            ne_dot = np.dot(NE, RS)  # NE と RS のドット積

             # ctheta, cphi を計算
            ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length if rs_length != 0 else 0
            cphi = math.sqrt(1-(R*ctheta/(R+hiono))**2)

            # STECデータのうち、cthetaの時間に対応するデータを取得
            relevant_stec = find_nearest_time_blocks(ut_time, obs_data)
            # 抽出したSTECデータとcthetaを掛ける
            for stec_time, stec_value in relevant_stec:
                vtec = stec_value * cphi
                #print(f"stec: {stec_value}")
                #print(f"vtec: {vtec}")
                output_data.append((stec_time, vtec))  # Store the results for output
    
    # 出力先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w') as output_file:
        # vtecのデータを保存する処理をここに追加
        for stec_time, vtec in output_data:  # resultsリストを使用
            output_file.write(f"{stec_time} {vtec}\n")

    print(f"Results saved to {output_file_path}")


def main():
    # STECファイルからsat# 26のデータを抽出
    stec_file = input("PATH to STEC file")
    sat_number = input("SELECT satellite number")
    input_obs = extract_sat_data_from_stec(sat_number, stec_file)
    # 衛星データファイルを取得　satTest.py
    input_nav = input("処理する .txt ファイル名(衛星)を入力してください: ")
    # GetPositionData.py から座標データを取得
    input_pos = input("Enter the relative path of the file (default: ../data/00R015.24.pos): ")
    target_date = input("Enter the target date (YYYY MM DD): ")   
    output_calvtec = f"../data/vtec/vtec_test.txt" 
    calculate_vtec(input_nav, input_obs ,input_pos, output_calvtec ,target_date)

if __name__ == "__main__":
    main()





