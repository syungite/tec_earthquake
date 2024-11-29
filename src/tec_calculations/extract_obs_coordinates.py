import math
import numpy as np

def calculate_vector(a, b, c, lat, lon):
    rlat = math.radians(lat)
    rlon = math.radians(lon)

    NN = np.array([-math.sin(rlat) * math.cos(rlon), -math.sin(rlat) * math.sin(rlon), math.cos(rlat)])
    NE = np.array([-math.sin(rlon), math.cos(rlon), 0])
    OR = np.array([a, b, c])
    
    return NN, NE, OR

def extract_coordinates_from_obs(obs_file):
    lat, lon, h = None, None, None

    with open(obs_file, 'r') as f:
        for line in f:
            # 「APPROX POSITION XYZ」を含む行を探す
            if "APPROX POSITION XYZ" in line:
                parts = line.split()
                if len(parts) >= 4:
                    # XYZ座標を取得してfloatに変換
                    x, y, z = map(float, parts[0:3])
                    # ECEF座標 (x, y, z) を 緯度、経度、標高に変換します
                    lat, lon, h = ecef_to_geodetic(x, y, z)
                break

    if lat is None or lon is None or h is None:
        raise ValueError("緯度、経度、標高がobsファイルから取得できませんでした。")
    
    NN, NE, OR = calculate_vector(x, y, z, lat, lon)
    return NN, NE, OR


def ecef_to_geodetic(x, y, z):
    """
    ECEF座標を緯度、経度、標高に変換します。

    Parameters:
    x, y, z (float): ECEF座標

    Returns:
    tuple: (lat, lon, h) 緯度（度）、経度（度）、標高（メートル）
    """
    import math

    # WGS84の定数
    a = 6378137.0         # 長半径
    f = 1 / 298.257223563 # 扁平率
    e2 = 2 * f - f ** 2   # 離心率の2乗

    # 経度
    lon = math.atan2(y, x)
    
    # 初期推定値
    p = math.sqrt(x ** 2 + y ** 2)
    lat = math.atan2(z, p * (1 - e2))
    
    # ニュートン法で緯度と標高を計算
    for _ in range(5): # 5回反復で十分な精度が得られる
        N = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        h = p / math.cos(lat) - N
        lat = math.atan2(z, p * (1 - e2 * (N / (N + h))))

    # 度に変換
    lat = math.degrees(lat)
    lon = math.degrees(lon)
    
    return lat, lon, h
