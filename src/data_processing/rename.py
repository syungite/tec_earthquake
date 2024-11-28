import os
import glob
import re  # 正規表現を使って数字部分を抽出

def rename_files(year):
    # 年ごとのディレクトリ内のすべてのファイルを取得
    file_pattern = f"../../data/coordinate/{year}/*.pos"
    matching_files = glob.glob(file_pattern)

    for file_path in matching_files:
        # ファイル名の抽出
        file_name = os.path.basename(file_path)
        
        # 正規表現で数字部分を抽出 (例えば 020855 の部分)
        match = re.match(r"(\d+)\.\d+\.pos", file_name)
        if match:
            rinex_suffix = match.group(1)[-4:]  # 最後の4桁を取得
        else:
            continue  # フォーマットが一致しない場合はスキップ

        # 新しいファイル名の作成
        new_file_name = f"{rinex_suffix}.{str(year)[-2:]}.pos"  # 新しい名前を生成
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)

        # ファイル名の変更
        os.rename(file_path, new_file_path)
        print(f"Renamed: {file_path} -> {new_file_path}")

# 使用例
year = 2024  # 年を指定

rename_files(year)


