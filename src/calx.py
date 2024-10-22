import os
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from CalVTEC import calculate_vtec



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

    # Loop over locations and process each one
    for i, location in enumerate(locations, 0):
        print(f"Processing No.{i} data")
        nav_file = f"../data/nav/{location}0700.11n"  # Adjust path as needed
        obs_file = f"../data/obs/{location}0700.11o"
        output_rdeph = f"../data/rdeph/rdeph_output_{i}.txt"
        output_rdrnx = f"../data/rdrnx/rdrnx_output_{i}.txt"

        # Run the Fortran program (rdeph.f) for each location
        run_rdeph(nav_file,output_rdeph)
        run_rdrnx(obs_file, output_rdrnx)
        print("end frotran")

        # Call CalVTEC.py to calculate VTEC for each location
        input_nav = f"../data/rdeph/rdeph_output_{i}.txt"  # Generated satellite data
        input_obs = f"../data/rdrnx/rdrnx_output_{i}.txt"  # Generated STEC data
        input_pos = f"../data/pos/{location}.11.pos"  # pos editing
        output_calvtec = f"../data/vtec/vtec_{i}.txt"  # VTEC result output
        target_data = "2011 03 11"
        print("Start calculating vtec")
        calculate_vtec(input_nav, input_obs,input_pos, output_calvtec, target_data)


if __name__ == "__main__":
    main()
