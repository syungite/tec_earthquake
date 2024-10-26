# CalVTEC.py
import os
import math
import numpy as np
import scipy.interpolate as interp
from GetPositionData import get_position_data
from GetSatData import get_satellite_data

# Constants
R = 6371 # Earth's radius in kilometers
hiono = 300 # Ionosphere height in kilometers

def calculate_vector(a, b, c, lat, lon):
    rlat = math.radians(lat)
    rlon = math.radians(lon)

    NN = np.array([-math.sin(rlat) * math.cos(rlon), -math.sin(rlat) * math.sin(rlon), math.cos(rlat)])
    NE = np.array([-math.sin(rlon), math.cos(rlon), 0])
    OR = np.array([a, b, c])
    
    return NN, NE, OR

def extract_sat_data_from_stec(sat_number, stec_file, output_file_path="data.txt"):
    data = []
    with open(stec_file, 'r', encoding='utf-8') as file:
        extracting = False 
        for line in file:
            cleaned_line = line.strip()  # Remove leading and trailing spaces

            # Check for satellite number
            if cleaned_line.startswith(f"> sat#{sat_number}"):
                extracting = True
            elif cleaned_line.startswith("> sat#"):
                extracting = False

            # Process data lines
            if extracting and not cleaned_line.startswith("> sat#"):
                parts = cleaned_line.split()
                if len(parts) == 2:  # Check if there are time and value
                    try:
                        time = float(parts[0])  
                        value = float(parts[1])  
                        f1 = 1.57542 
                        f2 = 1.22760 
                        stec = value * (f1)**2 * (f2)**2 /((f1**2 - f2**2)*40.308) # Calculate STEC
                        data.append((time, value))  
                    except ValueError:
                        continue

    with open(output_file_path, 'w') as output_file:
        for time, stec in data:
            output_file.write(f"{time} {stec}\n")
    return data

# 座標補完を行う関数
def interpolate_satellite_positions(time_points, x_values, y_values, z_values, query_times):
    """
    Interpolate satellite x, y, z positions for the given query_times based on known time_points and x_values, y_values, z_values.
    """
    # Ensure we have at least two points for interpolation
    if len(time_points) < 2:
        raise ValueError("Need at least two points for interpolation")
    
    # Create interpolation functions for x, y, z
    interp_x = interp.interp1d(time_points, x_values, kind='linear', fill_value="extrapolate")
    interp_y = interp.interp1d(time_points, y_values, kind='linear', fill_value="extrapolate")
    interp_z = interp.interp1d(time_points, z_values, kind='linear', fill_value="extrapolate")

    # Interpolate the satellite positions for the desired query times
    interpolated_x = interp_x(query_times)
    interpolated_y = interp_y(query_times)
    interpolated_z = interp_z(query_times)
    
    return interpolated_x, interpolated_y, interpolated_z

def calculate_vtec(input_nav, input_obs, input_pos, output_file_path, target_date):
    # 座標データを取得
    x, y, z, lat, lon = get_position_data(input_pos, target_date)

    # 取得した座標データを使ってベクトルを計算
    NN, NE, OR = calculate_vector(x, y, z, lat, lon)

    # GetSatData.py を呼び出し、衛星データを取得
    satellite_data = get_satellite_data(input_nav)

    # Extract STEC data for the specified satellite number
    sat_number = 26
    obs_data = extract_sat_data_from_stec(sat_number, input_obs)

    # Prepare data for output
    output_data = []

    # Initialize arrays for time and satellite positions to interpolate later
    time_points = []
    x_values = []
    y_values = []
    z_values = []

    for sat_num, data in satellite_data.items():
        if sat_num != sat_number:
            continue
        for ut_time, x_sat, y_sat, z_sat in data:
            time_points.append(ut_time)
            x_values.append(x_sat)
            y_values.append(y_sat)
            z_values.append(z_sat)

    # Interpolate satellite positions for STEC observation times
    obs_times = [stec_time for stec_time, _ in obs_data]
    interpolated_x, interpolated_y, interpolated_z = interpolate_satellite_positions(time_points, x_values, y_values, z_values, obs_times)

    # Calculate VTEC using interpolated satellite positions
    for i, (stec_time, stec_value) in enumerate(obs_data):
        # Interpolated satellite position at stec_time
        x_sat_interp = interpolated_x[i]
        y_sat_interp = interpolated_y[i]
        z_sat_interp = interpolated_z[i]

        # Calculate RS vector
        RS = np.array([x_sat_interp, y_sat_interp, z_sat_interp]) -OR
        rs_length = np.linalg.norm(RS)

        # calculate dot products for NN and NE
        nn_dot = np.dot(NN, RS)
        ne_dot = np.dot(NE, RS)

        # calculate ctheta and cphi
        ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length if rs_length != 0 else 0
        cphi = math.sqrt(1 - (R * ctheta / (R + hiono))**2)
        print(cphi)

        # Calculate VTEC
        vtec = stec_value * cphi
        output_data.append((stec_time, vtec))

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w') as output_file:
        for stec_time, vtec in output_data:
            output_file.write(f"{stec_time} {vtec}\n")

    print(f"Results saved to {output_file_path}")

def main():
    """
    Main function to run the VTEC calculation process.
    """
    stec_file = input("PATH to STEC file: ")
    sat_number = input("SELECT satellite number: ")
    input_obs = extract_sat_data_from_stec(sat_number, stec_file)

    input_nav = input("Enter the .txt file name for satellite data: ")
    input_pos = input("Enter the relative path to the position file (default: ../data/00R015.24.pos): ")
    target_date = input("Enter the target date (YYYY MM DD): ")

    output_calvtec = "../data/vtec/vtec_test.txt"
    calculate_vtec(input_nav, input_obs, input_pos, output_calvtec, target_date)

if __name__ == "__main__":
    main()





