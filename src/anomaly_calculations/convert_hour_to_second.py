import datetime

# 時刻を秒単位に変換する関数
def time_to_seconds(dt):
    return dt.hour * 3600 + dt.minute * 60 + dt.second

def convert_vtectime_to_seconds():
    for i in range(31):
        input_file_path = f"../data/vtec/vtec_{i}.txt"
        output_file_path = f"../data/vtec/vtec_{i}_output.txt"
        
        with open(input_file_path, 'r') as input_file:
            all_data = input_file.readlines()
            l = len(all_data)
        
        # 時刻の取得
        for i in range(20):
            first_line = all_data[i]
            x = float(first_line.split()[0]) * 100
            if x == int(x):
                start_time = all_data[i].split()[0]
                break
    
        time_delta = datetime.timedelta(seconds=30)
        start_time = float(start_time)
        total_seconds = int(start_time * 3600)  # 時間を秒に変換して整数化
        hours = total_seconds // 3600           # 時を計算
        minutes = (total_seconds % 3600) // 60  # 残り秒数を分に変換
        seconds = total_seconds % 60            # 残りの秒数
        
        # datetime を秒単位に変換
        base_time = datetime.datetime(2011, 3, 11, hour=hours, minute=minutes, second=seconds)
        
        # 基準時刻を秒単位で表示
        base_seconds = time_to_seconds(base_time)
        #print(base_time)  # 秒単位で表示
        
        # 新しい時刻を秒単位で計算
        new_times = [round(base_seconds + i * time_delta.total_seconds(), 3) for i in range(l)]

        # ファイルに新しい時間（秒）と元のデータを書き込む
        with open(output_file_path, 'w') as output_file:
            for i in range(l):
                # 元データの時間部分を新しい時間（秒）に置き換え
                new_line = f"{new_times[i]} {all_data[i].split()[1]}\n"
                output_file.write(new_line)

if __name__ == "__main__":
    convert_vtectime_to_seconds()

