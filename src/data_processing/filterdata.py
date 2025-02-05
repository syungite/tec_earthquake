import shutil

def copy_file_with_new_name(source_file_pattern, dest_dir, new_index, original_index):
    """指定されたパターンに従ってファイルをコピーし、新しい名前を付けます。"""
    # ファイル名に新しいインデックスを適用
    source_file = source_file_pattern.format(i=original_index)
    dest_file = f"{dest_dir}output_{new_index}.txt"  # 新しい名前でコピー先を指定
    
    try:
        shutil.copy(source_file, dest_file)
        print(f"Copied {source_file} to {dest_file}")
    except FileNotFoundError:
        print(f"File not found: {source_file}")
    except Exception as e:
        print(f"Error copying file {source_file} to {dest_file}: {e}")

def filterdata(satlist):
    data_list = []

    # list.txt の読み取り
    with open("/home/blue/tec_earthquake/data/list.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()  # 余分な空白や改行を除去
            if line:  # 空行をスキップ
                # 場所名とコードを分割
                location, code = line.split(": ")
                data_list.append((location, code))
    
    # listfilter.txt に対応する場所を書き込む
    with open("/home/blue/tec_earthquake/data/listfilter.txt", "w", encoding="utf-8") as filter_file:
        for i in satlist:
            location, code = data_list[i]  # インデックスに対応する場所
            filter_file.write(f"{location}: {code}\n")
    
    # ファイルコピー処理
    for new_index, original_index in enumerate(satlist):
        # rdeph ディレクトリのファイルをコピーし、rdeph_output_0.txt, rdeph_output_1.txt,... に変更
        source_file_pattern_rdeph = "/home/blue/tec_earthquake/data/rdeph/rdeph_output_{i}.txt"
        source_file_pattern_rdrnx = "/home/blue/tec_earthquake/data/rdrnx/rdrnx_output_{i}.txt"
        
        dest_dir = "/home/blue/tec_earthquake/data/satpos/rdeph_"
        
        # rdeph 出力ファイルをコピー
        copy_file_with_new_name(source_file_pattern_rdeph, dest_dir, new_index, original_index)
        
        # rdrnx 出力ファイルをコピー
        dest_dir_rdrnx = "/home/blue/tec_earthquake/data/stec/rdrnx_"  # 別のディレクトリにコピー
        copy_file_with_new_name(source_file_pattern_rdrnx, dest_dir_rdrnx, new_index, original_index)

# 呼び出し例
if __name__ == "__main__":
    # satlist に基づいてファイル名を変更
    satlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33]
    filterdata(satlist)


