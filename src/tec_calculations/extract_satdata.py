import re

def deciding_satnum(start_time, end_time):
    valid_sat = [0 for _ in range(32)]  # 32個の衛星番号のカウント用リスト
    valid_list = set()  # valid_satに対応する衛星番号を格納するセット

    # iの範囲(0 <= i <= 30)で繰り返し処理
    for i in range(31):  # 0 <= i <= 30
        stec_file = f"../data/rdrnx/rdrnx_output_{i}.txt"
        current_sat_id = None
        found_start_time = False
        found_end_time = False

        with open(stec_file, 'r', encoding='utf-8') as file:
            for line in file:
                cleaned_line = line.strip()

                # 衛星番号の検出
                if cleaned_line.startswith("> sat#"):
                    match = re.match(r"> sat#\s*(\d+)", cleaned_line)
                    if match:
                        current_sat_id = int(match.group(1))
                        #print(f"{i} {current_sat_id}")
                        found_start_time = False  # 新しい衛星番号が見つかると、時間のフラグをリセット
                        found_end_time = False
                else:
                    parts = cleaned_line.split()
                    if len(parts) == 2:
                        try:
                            time = float(parts[0])

                            # start_timeに一致するデータが見つかった場合
                            if time == start_time - 2.25:
                                found_start_time = True
                            
                            # end_timeに一致するデータが見つかった場合
                            elif time == end_time:
                                found_end_time = True

                            # 両方が見つかった場合かつ衛星番号が存在する場合のみvalid_satに追加
                            if found_start_time and found_end_time and current_sat_id is not None:
                                valid_sat[current_sat_id - 1] += 1  # 衛星番号に対するカウントを増やす
                                found_start_time = False  # 同じ衛星で複数追加を防ぐ
                                found_end_time = False
                        except ValueError:
                            continue

    # valid_satの中でカウントが30回になった衛星番号をvalid_listに追加
    #print(valid_sat)
    for i, count in enumerate(valid_sat):
        if count == 31:  # 31回検出された衛星番号をvalid_listに追加
            valid_list.add(i + 1)  # 衛星番号は1から始まるので、インデックスに+1を加える

    #print("Valid Satellites:", valid_list)
    return valid_list

