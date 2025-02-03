"""
If you want to decide center station, check at https://terras.gsi.go.jp/observation_code.php
Analysis date and time is define here

input parameter: center rinex (reference point), date, time is_recent (within one day -> true)
(They are defined in main function)

output: graph of ionosphere anomaly
"""

import os
import math
import csv
from concurrent.futures import ProcessPoolExecutor
from anomaly_calculations import calc_anomaly, convert_hour_to_second, anomaly_plotting
from data_processing import filterdata, ftp, mapping_points, sort_by_distance
from tec_calculations import calc_fortran, vtec_calculator, extract_satdata

def call_fortran_wrapper(args):
    year, month, day, i, location = args
    calc_fortran.call_fortran(year, month, day, i, location)

def calculate_vtec_wrapper(args):
    input_satpos, input_stec, output_calcvtec, obs_file, valid_sat = args
    vtec_calculator.calculate_vtec(input_satpos, input_stec, output_calcvtec, obs_file, valid_sat)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 1. パラメータ設定　（基準点の番号、年月日、時間）
    center_rinex = '0036'
    year, month, day = 2025, 2, 1
    start_time, end_time = 21, 23
    is_recent = True

    # もし一日以内の情報が知りたい場合は　is_recent = true　にしてこの処理を行う
    timelist = []
    if is_recent:
        end_time -= 0.008
        timelist = [chr(i + 97) for i in range(math.floor(start_time - 2.25), math.ceil(end_time))]
        print(timelist)

    # 基準点の(緯度、経度)を求める
    file_name = f"../data/coordinate/2024/{center_rinex}.{24}.pos"
    j_name, coordinates, rinex = sort_by_distance.parse_pos_file(file_name, 2024, 10, 1)
    center_coordinate = (coordinates[0], coordinates[1])
    print(center_coordinate)

    #2. 基準点の周囲の50点を観測点とし、ftpを使用してデータを取得
    excluded_rinex_file = '/home/blue/heki/data/excluded_rinex.txt'
    sort_by_distance.process_pos_files(2024, 10, 1, center_coordinate, excluded_rinex_file)
    mapping_points.show_map(center_coordinate)
    ftp.download_and_process_data(year, month, day, timelist)
    print("\033[32mend ftp connecting\033[0m")

    with open('../data/list.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    #3. 観測点の情報をTEC(電離層の様子を表すパラメータ)に変換
    print("\n\033[32mstart fortran\033[0m")
    with ProcessPoolExecutor() as executor:
        executor.map(call_fortran_wrapper, [(year, month, day, i, loc) for i, loc in enumerate(locations)])
    print("\033[32mend fortran\033[0m")

    #4. 使う衛星を決める
    satlist, valid_sat = extract_satdata.deciding_satnum(start_time, end_time)
    print(satlist)
    print(valid_sat)
    if valid_sat == -1: 
        print(f"{j_name}のデータは得られませんでした。")
        return
    filterdata.filterdata(satlist)

    #5. TEC(電離層の様子を表すパラメータ) を　VTEC(その垂直成分)　に変換
    print("\n\033[32mstart calculating vtec\033[0m")
    vtec_args = [
        (f"/home/blue/heki/data/satpos/rdeph_output_{i}.txt",
         f"/home/blue/heki/data/stec/rdrnx_output_{i}.txt",
         f"/home/blue/heki/data/vtec/vtec_{i}.txt",
         f"/home/blue/heki/data/obs/{loc}{calc_fortran.date_to_day_of_year(year, month, day)}0.{str(year)[-2:]}o",
         valid_sat)
        for i, loc in enumerate(locations)
    ]
    with ProcessPoolExecutor() as executor:
        executor.map(calculate_vtec_wrapper, vtec_args)
    print("\033[32mend vtec calculation\033[0m")

    # 時間表示を秒表示に変換
    convert_hour_to_second.convert_vtectime_to_seconds()

    #6. VTECを電離層の異常を表すパラメータに変換
    anomaly = calc_anomaly.calc_anomally_and_plot(start_time, end_time)

    #7. matplotlibで描画
    if is_recent: end_time += 0.008
    plotting_path = f"../data/anomaly_plot/{j_name}_{center_rinex}/{year}/{month:02}{day:02}_{start_time:02}to{end_time:02}.png"
    title = f"{j_name}_{center_rinex} {month:02}/{day:02}"
    os.makedirs(os.path.dirname(plotting_path), exist_ok=True) 
    anomaly_plotting.anomaly_plotting(anomaly, plotting_path, title, fixed=False)
    print(f"\033[32msaved to {plotting_path}\033[0m")

    plotting_path_fixed = f"../data/anomaly_plot/{j_name}_{center_rinex}/{year}/{month:02}{day:02}_{start_time:02}to{end_time:02}_fixed.png"
    os.makedirs(os.path.dirname(plotting_path_fixed), exist_ok=True)  
    anomaly_plotting.anomaly_plotting(anomaly, plotting_path_fixed, title, fixed=True)
    print(f"\033[32msaved to {plotting_path_fixed}\033[0m")


if __name__ == "__main__":
    main()
