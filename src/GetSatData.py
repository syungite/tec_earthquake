
def get_satellite_data(file_path):
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


