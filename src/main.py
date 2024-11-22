import os
from data_processing import calculate_distance, map, ftp
from calculations import calc_fortran, vtec_calculator, calc_anomaly

def main():
    # カレントディレクトリをスクリプトが存在する src に変更
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Current Working Directory: {os.getcwd()}")
    year, month, day = 2011, 3, 11
    center_rinex = "0214"

    file_name = f"../data/coordinate/{year}/{center_rinex}.{str(year)[-2:]}.pos"
    j_name, coordinates, rinex = calculate_distance.parse_pos_file(file_name, year, month, day)
    center_coordinate = (coordinates[0],  coordinates[1])

    # calculate_distance.process_pos_files(year, month, day, center_coordinate)
    # map.show_map(center_coordinate)
    # ftp.download_and_process_data(year, month, day)

    # Read list.txt for location names
    with open('../data/list.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    for i, location in enumerate(locations, 0):
        calc_fortran.call_fortran(year, month, day, i, location)

        # Call vtec_calculator.py to calculate VTEC for each location
        input_nav = f"../data/rdeph/rdeph_output_{i}.txt"  # Generated satellite data
        input_obs = f"../data/rdrnx/rdrnx_output_{i}.txt"  # Generated STEC data 
        output_calcvtec = f"../data/vtec/vtec_{i}.txt"  # VTEC result output
        day_of_year = calc_fortran.date_to_day_of_year(year, month, day)

        print("Start calculating vtec")
        obs_file = f"../data/obs/{location}{day_of_year}0.{str(year)[-2:]}o"
        vtec_calculator.calculate_vtec(input_nav, input_obs, output_calcvtec, obs_file)

    calc_anomaly.calc_anomally_and_plot()
    



if __name__ == "__main__":
    main()