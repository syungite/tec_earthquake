import requests

def get_coordinate(place_name):
    """
    国土地理院APIを使用して、場所名から緯度経度を取得する関数。
    """
    url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    params = {"q": place_name}
    r = requests.get(url, params=params)
    
    # HTTPエラー処理
    if r.status_code != 200:
        print(f"HTTPエラー：{r.status_code}")
        return None, None
    
    data = r.json()
    
    # データが空の場合
    if not data:
        print("データが見つかりませんでした。")
        return None, None
    
    # 完全一致する施設名が見つかればその緯度経度を返す
    for row in data:
        if row["properties"]["title"].startswith(place_name):
            coordinate = row["geometry"]["coordinates"]
            title = row["properties"]["title"]
            return coordinate, title
    
    # 見つからなかった場合
    print("指定された場所が見つかりませんでした。")
    return None, None

# 本田技研工業伊東研修センターの緯度経度を取得
coordinates, title = get_coordinate("京都市立花背第二中学校")

if coordinates:
    print(f"{title} の緯度経度は: {coordinates}")
else:
    print("緯度経度が取得できませんでした。")
