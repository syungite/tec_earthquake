# vtec_calculator.py
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from GetSatData import get_satellite_data
from getpos import extract_coordinates_from_obs
from satpos import satpos

# Constants
R = 6300  # Earth's radius in kilometers
hiono = 300  # Ionosphere height in kilometers

def calculate_vector(a, b, c, lat, lon):
    rlat = math.radians(lat)
    rlon = math.radians(lon)

    NN = np.array([-math.sin(rlat) * math.cos(rlon), -math.sin(rlat) * math.sin(rlon), math.cos(rlat)])
    NE = np.array([-math.sin(rlon), math.cos(rlon), 0])
    OR = np.array([a, b, c])
    
    return NN, NE, OR

def extract_sat_data_from_stec(sat_number, stec_file):
    obs_data = []
    with open(stec_file, 'r', encoding='utf-8') as file:
        extracting = False 
        for line in file:
            cleaned_line = line.strip()

            if cleaned_line.startswith(f"> sat#{sat_number}"):
                extracting = True
            elif cleaned_line.startswith("> sat#"):
                extracting = False

            if extracting and not cleaned_line.startswith("> sat#"):
                parts = cleaned_line.split()
                if len(parts) == 2:
                    try:
                        time = float(parts[0])
                        stec = float(parts[1])
                        obs_data.append((time, stec))
                    except ValueError:
                        continue
    return obs_data

def calculate_vtec(input_nav, input_obs, output_file_path, obs_file):
    x, y, z, lat, lon = extract_coordinates_from_obs(obs_file)
    NN, NE, OR = calculate_vector(x, y, z, lat, lon)
    print(OR)

    # get the position of satellite(sat_num)
    sat_number = 26
    satellite_data = get_satellite_data(input_nav, sat_number)
    if satellite_data is None:
        print(f"No data found for satellite number {sat_number}.")
        return
    
    obs_data = extract_sat_data_from_stec(sat_number, input_obs)
    output_data = []
    cphi_data = []
    sat_data_dict = {time: (x, y, z) for time, x, y, z in satellite_data}
    # if input_obs == "../data/rdrnx/rdrnx_output_0.txt":
    #     satpos(sat_data_dict, obs_data, OR, NN, NE)
    for stec_time, stec_value in obs_data:
        if stec_time not in sat_data_dict:
            print(f"No satellite position data for time {stec_time}, skipping.")
            continue

        x_sat, y_sat, z_sat = sat_data_dict[stec_time]
        OS = np.array([x_sat, y_sat, z_sat])
        RS = OS - OR
        rs_length = np.linalg.norm(RS, ord = 2)

        nn_dot = np.dot(NN, RS)
        ne_dot = np.dot(NE, RS)
        ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length 
        #if(ctheta <= math.cos(math.radians(15))):
        cphi = math.sqrt(1 - (R * ctheta / (R + hiono))**2)

        vtec = stec_value * cphi
        cphi_data.append((stec_time, ctheta))
        output_data.append((stec_time, vtec))

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w') as output_file:
        for stec_time, vtec in output_data:
            output_file.write(f"{stec_time} {vtec}\n")

    print(f"Results saved to {output_file_path}")

def main():
    stec_file = input("PATH to STEC file: ")
    sat_number = input("SELECT satellite number: ")
    input_obs = extract_sat_data_from_stec(sat_number, stec_file)

    input_nav = input("Enter the .txt file name for satellite data: ")
    input_pos = input("Enter the relative path to the position file (default: ../data/00R015.24.pos): ")
    target_date = input("Enter the target date (YYYY MM DD): ")

    output_calcvtec = "../data/vtec/vtec_test.txt"
    calculate_vtec(input_nav, input_obs, input_pos, output_calcvtec, target_date)

if __name__ == "__main__":
    main()






