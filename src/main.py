"""
If you want to decide center station, check at https://terras.gsi.go.jp/observation_code.php
Analysis date and time is define here
"""

import os
import math
import subprocess
from anomaly_calculations import calc_anomaly, convert_hour_to_second, anomaly_plotting
from data_processing import filterdata, ftp, mapping_points, sort_by_distance
from tec_calculations import calc_fortran, vtec_calculator, extract_satdata

def main():
    # カレントディレクトリをスクリプトが存在する src に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Current Working Directory: {os.getcwd()}")

    center_rinex = "0644"
    year, month, day = 2011, 12, 1
    start_time, end_time = 3, 5
    timelist = []
    is_recent = False

    if is_recent == True:
        """
        If the analysis time is recent, 
        subtract 0.008 from the end time
        and make a timelist of the English characters between the end time and the end time.
        """
        end_time -= 0.008
        timelist = [chr(i+97) for i in range(math.floor(start_time - 2.25), math.ceil(end_time))]
        print(timelist)

    file_name = f"../data/coordinate/{year}/{center_rinex}.{str(year)[-2:]}.pos"
    j_name, coordinates, rinex = sort_by_distance.parse_pos_file(file_name, year, month, day)
    center_coordinate = (coordinates[0],  coordinates[1])
    print(center_coordinate)
    #data processing directory
    subprocess.run("rm -f /home/blue/heki/data/obs/*", shell=True)
    subprocess.run("rm -f /home/blue/heki/data/obs/*", shell=True)
    #Acquire more data for an observation point (40) than the required number of data (31)
    excluded_rinex_file = '/home/blue/heki/data/excluded_rinex.txt'
    sort_by_distance.process_pos_files(year, month, day, center_coordinate, excluded_rinex_file)
    mapping_points.show_map(center_coordinate)
    ftp.download_and_process_data(year, month, day, timelist)
    print("\n\033[32mend ftp connecting\033[0m")
    
    # Read list.txt for location names
    with open('../data/list.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    print("\n\033[32mstart fortran\033[0m")
    for i, location in enumerate(locations, 0):
        calc_fortran.call_fortran(year, month, day, i, location)
    print("\n\033[32mend fortran\033[0m")

    satlist, valid_sat = extract_satdata.deciding_satnum(start_time, end_time)
    print(satlist)
    print(valid_sat)
    filterdata.filterdata(satlist)

    print("\n\033[32mstart calculating stec\033[0m")
    with open('../data/listfilter.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]
    for i, location in enumerate(locations, 0):
        # Call vtec_calculator.py to calculate VTEC for each location
        input_satpos = f"/home/blue/heki/data/satpos/rdeph_output_{i}.txt"  # Generated satellite data
        input_stec = f"/home/blue/heki/data/stec/rdrnx_output_{i}.txt"  # Generated STEC data 
        output_calcvtec = f"/home/blue/heki/data/vtec/vtec_{i}.txt"  # VTEC result output
        day_of_year = calc_fortran.date_to_day_of_year(year, month, day)
        obs_file = f"/home/blue/heki/data/obs/{location}{day_of_year}0.{str(year)[-2:]}o"
        vtec_calculator.calculate_vtec(input_satpos, input_stec, output_calcvtec, obs_file, valid_sat)
    
    # anomaly calculating directory
    convert_hour_to_second.convert_vtectime_to_seconds()
    anomaly = calc_anomaly.calc_anomally_and_plot(start_time, end_time)
    plotting_path = "../data/anomaly_plotexp.png"
    anomaly_plotting.anomaly_plotting(anomaly, plotting_path)
    
    print("\033[32mplotting anomaly is done\033[0m")
    
if __name__ == "__main__":
    main()
