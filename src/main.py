import os
from anomaly_calculations import calc_anomaly, convert_hour_to_second, anomaly_plotting
from data_processing import ftp, mapping_points, sort_by_distance
from tec_calculations import calc_fortran, vtec_calculator

def main():
    # カレントディレクトリをスクリプトが存在する src に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Current Working Directory: {os.getcwd()}")

    """
    If you want to decide center station, check at https://terras.gsi.go.jp/observation_code.php
    Analysis date and time is define here
    """
    center_rinex = "0214"
    year, month, day = 2011, 3, 11
    start_time, end_time = 4.5, 6.5

    file_name = f"../data/coordinate/{year}/{center_rinex}.{str(year)[-2:]}.pos"
    j_name, coordinates, rinex = sort_by_distance.parse_pos_file(file_name, year, month, day)
    center_coordinate = (coordinates[0],  coordinates[1])

    sort_by_distance.process_pos_files(year, month, day, center_coordinate)
    mapping_points.show_map(center_coordinate)
    ftp.download_and_process_data(year, month, day)
    
    print("\n\033[32mstart tec calculations\033[0m")
    # Read list.txt for location names
    with open('../data/list.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    for i, location in enumerate(locations, 0):
        calc_fortran.call_fortran(year, month, day, i, location)

        # Call vtec_calculator.py to calculate VTEC for each location
        input_nav = f"../data/rdeph/rdeph_output_{i}.txt"  # Generated satellite data
        input_stec = f"../data/rdrnx/rdrnx_output_{i}.txt"  # Generated STEC data 
        output_calcvtec = f"../data/vtec/vtec_{i}.txt"  # VTEC result output
        day_of_year = calc_fortran.date_to_day_of_year(year, month, day)

        obs_file = f"../data/obs/{location}{day_of_year}0.{str(year)[-2:]}o"
        vtec_calculator.calculate_vtec(input_nav, input_stec, output_calcvtec, obs_file)
    
    convert_hour_to_second.convert_vtectime_to_seconds()
    anomaly = calc_anomaly.calc_anomally_and_plot(start_time, end_time)
    plotting_path = "../data/anomaly_plot1.png"
    anomaly_plotting.anomaly_plotting(anomaly, plotting_path)
    
    print("\033[32mplotting anomaly is done\033[0m")
    



if __name__ == "__main__":
    main()