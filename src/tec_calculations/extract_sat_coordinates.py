def get_satellite_data(file_path, satellite_num):

    satellite_data = []  

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) < 5:  
                continue

            ut_time = float(parts[0])  # 時刻
            sat_num = int(parts[1])   # 衛星番号
            x = float(parts[2].replace('D', 'E'))  # X座標
            y = float(parts[3].replace('D', 'E'))  # Y座標
            z = float(parts[4].replace('D', 'E'))  # Z座標

            if sat_num == satellite_num:
                satellite_data.append((ut_time, x, y, z))

    return satellite_data



