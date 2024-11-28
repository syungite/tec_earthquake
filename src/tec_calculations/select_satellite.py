import numpy as np
import math
from tec_calculations.extract_sat_coordinates import get_satellite_data
from tec_calculations.extract_obs_coordinates import extract_coordinates_from_obs

def selecting_sat(input_nav, obs_file, start_time, end_time, valid_sat):
    NN, NE, OR = extract_coordinates_from_obs(obs_file)
    best_num, min_rs_sum = -1, float('inf')  # 最小値を無限大で初期化

    for i in range(1, 33):
        if i not in valid_sat:
            continue

        satellite_data = get_satellite_data(input_nav, i)
        if not satellite_data:
            continue

        # データを辞書形式にして、時間でアクセスできるようにする
        sat_data_dict = {time: (x, y, z) for time, x, y, z in satellite_data}

        # RS_SIPの合計値を計算
        rs_sum = 0
        for time in sat_data_dict:
            if start_time <= time <= end_time:
                x_sat, y_sat, z_sat = sat_data_dict[time]
                OS = np.array([x_sat, y_sat, z_sat])
                RS = OS - OR
                rs_length = np.linalg.norm(RS, ord=2)  # ベクトルの長さ
                nn_dot = np.dot(NN, RS)
                ne_dot = np.dot(NE, RS)
                ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length 
                stheta = math.sqrt(1-ctheta**2)
                RS_SIP = RS * 300 * 1000 / (rs_length*stheta) 
                rs_sum += np.linalg.norm(RS, ord=2)

        # 合計値が最小の衛星を探す
        if rs_sum < min_rs_sum and rs_sum > 0:
            best_num = i
            min_rs_sum = rs_sum

        #print(f"Satellite {i}: RS sum = {rs_sum}")

    print(f"Best Satellite: {best_num} with RS sum = {min_rs_sum}")
    return best_num





