import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from vtec_calculator import calculate_vtec
from ftp import date_to_day_of_year


def run_rdeph(nav_file, output_rdeph):
    # Call the Fortran executable (rdeph) with the .11n
    command = f"./rdeph < {nav_file} > {output_rdeph}"
    subprocess.run(command, shell=True,check = True)

def run_rdrnx(obs_file, output_rdrnx):
    # Call the Fortran executable (rdrnx) with the .11o
    command = f"./rdrnx < {obs_file} > {output_rdrnx}"
    subprocess.run(command, shell=True, check = True)

def main():
    # Read list.txt for location names
    with open('../data/list.txt', 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]
    target_data = "2011 03 11"
    year, month, day = int(target_data[0:4]), int(target_data[5:7]),int(target_data[8:10])
    day_of_year = date_to_day_of_year(year, month, day)
    
    # Loop over locations and process each one
    for i, location in enumerate(locations, 0):

        print(f"Processing No.{i} data")
        print(location)
        nav_file = f"../data/nav/{location}{day_of_year}0.{str(year)[-2:]}n"  # Adjust path as needed
        obs_file = f"../data/obs/{location}{day_of_year}0.{str(year)[-2:]}o"
        output_rdeph = f"../data/rdeph/rdeph_output_{i}.txt"
        output_rdrnx = f"../data/rdrnx/rdrnx_output_{i}.txt"

        # Run the Fortran program (rdeph.f) for each location
        run_rdeph(nav_file,output_rdeph)
        run_rdrnx(obs_file, output_rdrnx)
        print("end frotran")

        # Call vtec_calculator.py to calculate VTEC for each location
        input_nav = f"../data/rdeph/rdeph_output_{i}.txt"  # Generated satellite data
        input_obs = f"../data/rdrnx/rdrnx_output_{i}.txt"  # Generated STEC data
        input_pos = f"../data/pos/{location}.{target_data[2:4]}.pos"  # pos editing
        output_calcvtec = f"../data/vtec/vtec_{i}.txt"  # VTEC result output
        print("Start calculating vtec")
        calculate_vtec(input_nav, input_obs, output_calcvtec, obs_file)


if __name__ == "__main__":
    main()
