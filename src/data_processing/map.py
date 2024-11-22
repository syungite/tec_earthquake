import folium

def read_locations_from_file(file_path):
    locations = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            lat, lon, rnx = line.strip().split(", ")
            lat, lon = float(lat), float(lon)
            locations.append({"lat": lat, "lon": lon, "rnx": rnx})
    return locations

def show_map(center_coordinate):
    # setting the center point
    center_lat, center_lon = center_coordinate[0], center_coordinate[1]

    # create map
    mymap = folium.Map(location=[center_lat, center_lon], zoom_start=10)

    # load coordinate data from map.txt
    locations = read_locations_from_file("../data/map.txt")

    # 各ポイントを地図上に追加
    for loc in locations:
        folium.Marker([loc["lat"], loc["lon"]], popup=f"Lat: {loc['lat']}, Lon: {loc['lon']}, {loc['rnx']}").add_to(mymap)

    # 地図をHTMLファイルに保存
    mymap.save("../data/map.html")

    print("Map has been saved to map.html.")

if __name__ == "__main__":
    # example (kitaibaraki)
    coordinates = (3.6800309526E+01,  1.4075391238E+02)
    show_map(coordinates)

