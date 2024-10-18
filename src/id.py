import glob
import os

def parse_pos_file(file_path):
    """ .posファイルからJ_NAMEとRINEXを取得する """
    j_name = None
    RINEX = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith(" RINEX"):
                RINEX = line.split()[1]
            if line.startswith(" J_NAME"):
                j_name = line.split()[1]

    return j_name, RINEX

def main():
    """ メインの処理を行う関数 """
    # ファイルを探索
    pos_files = glob.glob("../data/coordinate/2011/*.pos")
    ids_with_j_names = []

    if not pos_files:
        print("No .pos files found in the directory.")  # .posファイルが見つからない場合
        return

    # ファイルごとにJ_NAMEとRINEXを取得
    for file in pos_files:
        j_name, rinex = parse_pos_file(file)
        if j_name and rinex:
            ids_with_j_names.append((j_name, rinex))

    # RINEXでソート
    ids_with_j_names.sort(key=lambda x: x[1])

    # 結果をファイルに出力
    output_path = os.path.join('..','data', 'id.txt')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        if ids_with_j_names:
            for j_name, rinex in ids_with_j_names:
                output_file.write(f"{j_name}: {rinex}\n")
            print(f"Results saved to {output_path}")
        else:
            output_file.write("No valid J_NAME and RINEX found.\n")
            print(f"No valid J_NAME and RINEX found, empty result file created at {output_path}")

if __name__ == "__main__":
    main()


