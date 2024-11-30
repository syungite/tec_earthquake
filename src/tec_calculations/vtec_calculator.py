# vtec_calculator.py
import re
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from tec_calculations.extract_sat_coordinates import get_satellite_data
from tec_calculations.extract_obs_coordinates import extract_coordinates_from_obs
# from tec_calculations.extract_satdata import extract_sat_data_from_stec 

# Constants
R = 6300  # Earth's radius in kilometers
hiono = 300  # Ionosphere height in kilometers

def extract_sat_data_from_stec(stec_file, sat_number):
    obs_data = []
    with open(stec_file, 'r', encoding='utf-8') as file:
        extracting = False 
        for line in file:
            cleaned_line = line.strip()
            pattern = re.compile(rf"> sat#\s*{sat_number}")

            if pattern.match(cleaned_line):
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

def calculate_vtec(input_satpos, input_stec, output_file_path, obs_file, sat_number):
    NN, NE, OR = extract_coordinates_from_obs(obs_file)

    satellite_pos = get_satellite_data(input_satpos, sat_number)
    if satellite_pos is None:
        print(f"No data found for satellite number {sat_number}.")
        return
    obs_data = extract_sat_data_from_stec(input_stec, sat_number)

    output_data = []
    sat_pos_dict = {time: (x, y, z) for time, x, y, z in satellite_pos}

    for stec_time, stec_value in obs_data:
        if stec_time not in sat_pos_dict:
            print(f"No satellite position data for time {stec_time}, skipping.")
            continue

        x_sat, y_sat, z_sat = sat_pos_dict[stec_time]
        OS = np.array([x_sat, y_sat, z_sat])
        RS = OS - OR
        rs_length = np.linalg.norm(RS, ord = 2)

        nn_dot = np.dot(NN, RS)
        ne_dot = np.dot(NE, RS)
        ctheta = math.sqrt(nn_dot**2 + ne_dot**2) / rs_length 
        cphi = math.sqrt(1 - (R * ctheta / (R + hiono))**2)

        vtec = stec_value * cphi
        output_data.append((stec_time, vtec))

    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    with open(output_file_path, 'w') as output_file:
        for stec_time, vtec in output_data:
            output_file.write(f"{stec_time} {vtec}\n")

    print(f"Results saved to {output_file_path}")



def main():
    stec_file = input("PATH to STEC file: ")
    sat_number = input("SELECT satellite number: ")
    input_stec = extract_sat_data_from_stec(sat_number, stec_file)

    input_satpos = input("Enter the .txt file name for satellite data: ")
    input_pos = input("Enter the relative path to the position file (default: ../data/00R015.24.pos): ")
    target_date = input("Enter the target date (YYYY MM DD): ")

    ref_time = 0
    output_calcvtec = "../data/vtec/vtec_test.txt"
    calculate_vtec(input_satpos, input_stec, input_pos, output_calcvtec, target_date, ref_time)

if __name__ == "__main__":
    main()






