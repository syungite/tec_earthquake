import os
import shutil

def get_matching_codes(list_file_path):
    """ list.txtから4桁の位置コードを取得する """
    codes = set()  # 一意の位置コードを保持
    with open(list_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) == 2:
                # コード部分を抽出してリストに追加
                code = parts[1].strip()
                if len(code) == 4:  # 4桁のコードのみを追加
                    codes.add(code)
    return codes

def main():
    coordinate_directory = "../data/coordinate/2011"
    pos_directory = "../data/pos"
    list_file_path = "../data/list.txt"

    # 位置コードを取得
    matching_codes = get_matching_codes(list_file_path)

    # ディレクトリ内の.posファイルを処理
    for filename in os.listdir(coordinate_directory):
        if filename.endswith('.pos'):
            file_path = os.path.join(coordinate_directory, filename)

            # ファイル名の最初の2文字を削除
            new_filename = filename[-11:]  # 最初の2文字を削除
            new_file_path = os.path.join(coordinate_directory, new_filename)

            # ファイル名を変更
            os.rename(file_path, new_file_path)

            # 新しいファイル名の末尾4桁を取得
            code = new_filename[-11:-7]  # 例: xxxx.11.pos から xxxx を取得
            print(code)

            # コードがlist.txtに含まれているか確認
            if code in matching_codes:
                # 一致したらposディレクトリにコピー
                shutil.copy(new_file_path, os.path.join(pos_directory, new_filename))
                print(f"Copied {new_filename} to {pos_directory}")

if __name__ == "__main__":
    main()

