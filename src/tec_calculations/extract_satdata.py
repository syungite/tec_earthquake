import re
import math

def deciding_satnum(start_time, end_time):
    # 各衛星の観測ファイルインデックスを格納するリスト（32個の衛星）
    satlist = [[] for _ in range(32)]  
    valid_sat = -1

    # 調査対象の時間データを作成（重複を避けるためにsetを使用）
    """
    setを使う意味
    例えばstart_time = 10 end_time = 12 とする
    このとき
    17行目では {8, 9, 10, 11} がcheck_timeに格納される
    18行目では {7.75, 8, 9, 10, 12} となる
    -> start_time = 10.25 のようなコーナーケースにも対応させる
    """
    check_time = set(range(math.ceil(start_time - 2.25), int(end_time) + 1))
    check_time.update([start_time - 2.25, end_time])  # 開始と終了時間も追加
    print(check_time)


    """
    実際の処理は各観測点（28行目のiに相当)に対して
    衛星番号（44行目から）を正規表現を使って検出
    全ての観測点がそろった衛星を戻り値として返す
    """
    for i in range(50):  
        stec_file = f"../data/rdrnx/rdrnx_output_{i}.txt"
        sat_file = f"../data/rdeph/rdeph_output_{i}.txt"
        current_sat_id = None
        cnt = 0

        try:
             # `sat_file` が空でないことを確認
            with open(sat_file, 'r', encoding='utf-8') as sf:
                if not sf.read().strip():  # 空ファイルの場合は次のループへ
                    continue
            with open(stec_file, 'r', encoding='utf-8') as file:
                for line in file:
                    cleaned_line = line.strip()

                    # 衛星番号の検出
                    if cleaned_line.startswith("> sat#"):
                        match = re.match(r"> sat#\s*(\d+)", cleaned_line)
                        if match:
                            current_sat_id = int(match.group(1))
                            cnt = 0  # 新しい衛星番号が見つかったらカウントをリセット
                    else:
                        parts = cleaned_line.split()
                        if len(parts) == 2:
                            try:
                                time = float(parts[0])
                                # 時間がcheck_timeに含まれている場合、カウントを増加
                                if time in check_time:
                                    cnt += 1

                                # すべての時間に一致し、衛星番号が有効な場合
                                if cnt == len(check_time) and current_sat_id is not None:
                                    satlist[current_sat_id - 1].append(i)
                                    cnt = 0  # 一致したらリセット
                            except ValueError:
                                continue  # データが不正な場合はスキップ

            # 31個の観測点が揃った衛星を特定する
            for j in range(32):
                if len(satlist[j]) == 31:
                    valid_sat = j + 1
                    return satlist[j], valid_sat  # 最初に見つかった有効な衛星を返す                            
        except FileNotFoundError:
            continue  # ファイルが存在しない場合はスキップ

    # 31個の観測点が揃った衛星を特定する
    for j in range(32):
        if len(satlist[j]) == 31:
            valid_sat = j + 1
            return satlist[j], valid_sat  # 最初に見つかった有効な衛星を返す

    return satlist, valid_sat  # 条件を満たす衛星がない場合のデフォルト戻り値

if __name__ == "__main__":
    result, valid_sat = deciding_satnum(0, 2)
    print("結果:", result)
    print("有効な衛星番号:", valid_sat)


