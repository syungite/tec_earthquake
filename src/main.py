import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from anomaly_calculations import calc_anomaly, convert_hour_to_second, anomaly_plotting
from data_processing import filterdata, ftp, mapping_points, sort_by_distance
from tec_calculations import calc_fortran, vtec_calculator, extract_satdata

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Current Working Directory: {os.getcwd()}")

    center_rinex = "0214"
    year, month, day = 2011, 3, 11
    start_time, end_time = 4.5, 6
    is_recent = True

    timelist = []
    if(is_recent): timelist = []

    file_name = f"../data/coordinate/{year}/{center_rinex}.{str(year)[-2:]}.pos"
    j_name, coordinates, rinex = sort_by_distance.parse_pos_file(file_name, year, month, day)
    center_coordinate = (coordinates[0], coordinates[1])
    print(center_coordinate)

    subprocess.run("rm -f /home/blue/heki/data/obs/*", shell=True)
    subprocess.run("rm -f /home/blue/heki/data/nav/*", shell=True)
    excluded_rinex_file = '/home/blue/heki/data/excluded_rinex.txt'
    sort_by_distance.process_pos_files(year, month, day, center_coordinate, excluded_rinex_file)
    mapping_points.show_map(center_coordinate)
    ftp.download_and_process_data(year, month, day, is_recent)

    with open('../data/list.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    print("\n\033[32mstart fortran (parallel)\033[0m")

    # Fortranを並列実行する関数
    def parallel_call_fortran(args):
        return calc_fortran.call_fortran(*args)

    args_list = [(year, month, day, i, location) for i, location in enumerate(locations)]

    with ProcessPoolExecutor() as executor:
        executor.map(parallel_call_fortran, args_list)

    print("\n\033[32mend fortran\033[0m")

    satlist, valid_sat = extract_satdata.deciding_satnum(start_time, end_time)
    filterdata.filterdata(satlist)

    print("\n\033[32mstart calculating stec (parallel)\033[0m")

    # VTEC計算を並列実行する関数
    def parallel_vtec_calculator(args):
        return vtec_calculator.calculate_vtec(*args)

    with open('../data/listfilter.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    args_list_vtec = [
        (
            f"/home/blue/heki/data/satpos/rdeph_output_{i}.txt",
            f"/home/blue/heki/data/stec/rdrnx_output_{i}.txt",
            f"/home/blue/heki/data/vtec/vtec_{i}.txt",
            f"/home/blue/heki/data/obs/{location}{calc_fortran.date_to_day_of_year(year, month, day)}0.{str(year)[-2:]}o",
            valid_sat
        )
        for i, location in enumerate(locations)
    ]

    with ProcessPoolExecutor() as executor:
        executor.map(parallel_vtec_calculator, args_list_vtec)

    print("\033[32mend calculating stec\033[0m")

    convert_hour_to_second.convert_vtectime_to_seconds()
    anomaly = calc_anomaly.calc_anomally_and_plot(start_time, end_time)
    plotting_path = "../data/anomaly_plot1.png"
    anomaly_plotting.anomaly_plotting(anomaly, plotting_path)

    print("\033[32mplotting anomaly is done\033[0m")

if __name__ == "__main__":
    main()

