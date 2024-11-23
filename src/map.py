import folium

def read_locations_from_file(file_path):
    locations = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            lat, lon, rnx = line.strip().split(", ")
            lat, lon = float(lat), float(lon)
            locations.append({"lat": lat, "lon": lon, "rnx": rnx})
    return locations

# 中心点の設定（例として北茨城）
center_lat, center_lon = 36.800303696, 140.75393788

# 地図の作成
mymap = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# map.txt から座標データを読み込む
locations = read_locations_from_file("../data/map.txt")

# 各ポイントを地図上に追加
for loc in locations:
    folium.Marker([loc["lat"], loc["lon"]], popup=f"Lat: {loc['lat']}, Lon: {loc['lon']}, {loc['rnx']}").add_to(mymap)

# 地図をHTMLファイルに保存
mymap.save("../data/map.html")

print("Map has been saved to map.html.")

