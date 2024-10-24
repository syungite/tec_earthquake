# CalVTEC.py
import os
import math
import numpy as np
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

def extract_sat_data_from_stec(sat_number, stec_file):
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
                        stec = value * (f1 * f2)**2 /((f1**2 - f2**2)*40.308)*100  # Calculate STEC
                        data.append((time, stec))  
                    except ValueError:
                        continue

    return data

def find_nearest_time_blocks(ut_time, input_obs):
    """
    Find STEC data within a time window centered around ctheta_time.
    """
    block_size = 0.05  # Time block size of 0.05 hours (3 minutes)
    half_block = block_size / 2  # Time block will extend 1.5 minutes before and after 
    nearest_stec = []
    
    for stec_time, stec_value in input_obs:
        if abs(stec_time - ut_time) <= half_block:  # Check within the half-block range
            nearest_stec.append((stec_time, stec_value))
    
    return nearest_stec


def calculate_vtec(input_nav, input_obs ,input_pos, output_file_path, target_date):

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

    for sat_num, data in satellite_data.items():
        if sat_num != sat_number:
            continue
        for ut_time, x_sat, y_sat, z_sat in data:
            RS = np.array([x_sat, y_sat, z_sat]) - OR
            rs_length = np.linalg.norm(RS)

            # calculate dot products for NN and NE
            nn_dot = np.dot(NN, RS)  
            ne_dot = np.dot(NE, RS) 

             # calculate ctheta and cphi
            ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length if rs_length != 0 else 0
            cphi = math.sqrt(1-(R*ctheta/(R+hiono))**2)

            # STECデータのうち、cthetaの時間に対応するデータを取得
            relevant_stec = find_nearest_time_blocks(ut_time, obs_data)

             # Store the results for output
            for stec_time, stec_value in relevant_stec:
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





