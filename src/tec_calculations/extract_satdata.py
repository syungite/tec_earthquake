import re

def deciding_satnum(start_time, end_time):
    satlist = [[] for _ in range(32)]  # hold observation number correspond to each satellite number
    valid_sat = -1

    for i in range(40):  
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
                                satlist[current_sat_id - 1].append(i) 
                                found_start_time = False  # 同じ衛星で複数追加を防ぐ
                                found_end_time = False
                        except ValueError:
                            continue
        
        for j in range(32):
            if len(satlist[j]) == 31: # Number of observation points to be obtained
                valid_sat = j + 1
                return satlist[j], valid_sat
    
    return satlist, valid_sat

if __name__ == "__main__":
    deciding_satnum(0, 2)

