import numpy as np
import math
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def ecef_to_geodetic(x, y, z):
    """
    ECEF座標系から緯度・経度・高さを計算
    """
    a = 6378137.0         # WGS84長半径
    f = 1 / 298.257223563 # 扁平率
    e2 = 2 * f - f ** 2   # 離心率の2乗

    lon = np.arctan2(y, x)  # 経度
    p = np.sqrt(x ** 2 + y ** 2)  # 水平方向距離
    lat = np.arctan2(z, p * (1 - e2))  # 初期緯度推定値

    # 緯度と高さの反復計算
    for _ in range(5):
        N = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
        h = p / np.cos(lat) - N
        lat = np.arctan2(z, p * (1 - e2 * (N / (N + h))))

    # 度に変換
    lat = np.degrees(lat)
    lon = np.degrees(lon)
    
    return lat, lon

def satpos(sat_data_dict, obs_data, OR, NN, NE):
    """
    ランベルト正角円錐図法で観測点とSIP位置を描画
    """
    # Lambert Conformal Conic projection の設定
    proj = ccrs.Mercator(
    central_longitude=140  # 中心経度
    )

    # プロットの作成
    fig, ax = plt.subplots(subplot_kw={'projection': proj}, figsize=(10, 8))
    ax.set_extent([136, 146, 34, 40], crs=ccrs.PlateCarree())  # 描画範囲

    # 海岸線、国境などの特徴を追加
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    # 観測点のプロット
    lat_OR, lon_OR = ecef_to_geodetic(OR[0], OR[1], OR[2])
    ax.plot(lon_OR, lat_OR, color='black', marker='o', markersize=8, transform=ccrs.PlateCarree(), label="Observation Point")

    # 各時間のSIP位置をプロット
    ax.plot()
    for stec_time, _ in obs_data:
        if not (1 < stec_time < 7):  # 時間フィルタリング
            continue
        x_sat, y_sat, z_sat = sat_data_dict.get(stec_time, (None, None, None))
        if x_sat is None:
            continue

        # SIP位置の計算
        OS = np.array([x_sat, y_sat, z_sat])  # 衛星位置ベクトル
        RS = OS - OR                         # 観測点から衛星までのベクトル
        rs_length = np.linalg.norm(RS, ord=2)  # ベクトルの長さ
        nn_dot = np.dot(NN, RS)
        ne_dot = np.dot(NE, RS)
        ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length 
        stheta = math.sqrt(1-ctheta**2)
        RS_SIP = RS * 300 * 1000 / (rs_length*stheta)  # RSを300 kmにスケール
        OS_SIP = OR + RS_SIP                 # SIPのECEF座標
        lat, lon = ecef_to_geodetic(OS_SIP[0], OS_SIP[1], OS_SIP[2])
        # SIP位置をプロット
        if(float(stec_time) - 5.767 == 0): ax.plot(lon, lat, color='k', marker='o', markersize=10, transform=ccrs.PlateCarree())
        else: ax.plot(lon, lat, 'bo', markersize=4, transform=ccrs.PlateCarree())
    latitude = 38 + 6.2 / 60  
    longitude = 142 + 51.6 / 60  
    ax.plot(longitude, latitude, 'ro', transform=ccrs.PlateCarree())
    with open("../data/list1.txt", "r") as f:
        for line in f:
            lat, lon = map(float, line.strip().split(","))
            ax.plot(lon, lat, 'ro', markersize=6, transform=ccrs.PlateCarree())
    # 凡例を追加
    ax.legend(loc='lower left')
    plt.title("Satellite SIP Positions (Lambert Conformal Conic Projection)", fontsize=16)
    plt.savefig("../data/Cartopy.png")
    plt.show()

def main():
    # サンプルデータ準備
    OR = np.array([3875000, 3325000, 3480000])  # 観測点のECEF座標（仮の例）
    
    # 衛星データ（時間に応じたECEF座標）
    sat_data_dict = {
        14.5: (3876000, 3326000, 3481000),
        15.0: (3877000, 3327000, 3482000),
        16.0: (3878000, 3328000, 3483000),
    }

    # 観測データ（ste_time, その他のデータ）
    obs_data = [
        (14.5, None),
        (15.0, None),
        (16.0, None),
        (17.5, None),  # 無視されるデータ
    ]

    # 地図描画
    satpos(sat_data_dict, obs_data, OR)

if __name__ == "__main__":
    main()
