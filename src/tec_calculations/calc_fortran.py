#calc_fortran (tec_earthquake/src/calculations/calc_fortran.py)
import os
import subprocess
import datetime
from tec_calculations.vtec_calculator import calculate_vtec


def date_to_day_of_year(year, month, day):
    """Convert date to day of the year."""
    date = datetime.datetime(year, month=month, day=day)
    return date.strftime("%j")

def ensure_directory_exists(path):
    """Ensure the directory exists; create it if not."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def run_rdeph(nav_file, output_rdeph):
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(__file__)
    
    # 'fortran'ディレクトリのパスを解決
    fortran_dir = os.path.join(script_dir, "../fortran")
    
    # nav_file と output_rdeph の絶対パスを取得
    nav_file_abs = os.path.abspath(os.path.join("/home/blue/tec_earthquake/data/nav", nav_file))
    output_rdeph_abs = os.path.abspath(os.path.join("/home/blue/tec_earthquake/data/rdeph", output_rdeph))

    # コマンドを正しいパスで実行
    command = f"cd {fortran_dir} && ./rdeph < {nav_file_abs} > {output_rdeph_abs}"
    
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        raise

def run_rdrnx(obs_file, output_rdrnx):
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(__file__)
    
    # 'fortran'ディレクトリのパスを解決
    fortran_dir = os.path.join(script_dir, "../fortran")
    
    # nav_file と output_rdeph の絶対パスを取得
    obs_file_abs = os.path.abspath(os.path.join("/home/blue/tec_earthquake/data/obs", obs_file))
    output_rdrnx_abs = os.path.abspath(os.path.join("/home/blue/tec_earthquake/data/rdrnx", output_rdrnx))

    # コマンドを正しいパスで実行
    command = f"cd {fortran_dir} && ./rdrnx < {obs_file_abs} > {output_rdrnx_abs}"
    
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        raise

def call_fortran(year, month, day, i, location):
    """Call Fortran programs (rdeph and rdrnx) for the given location."""
    day_of_year = date_to_day_of_year(year, month, day)
    print(f"Processing No.{i:2d} data for location {location}")

    # File paths
    nav_file = f"{location}{day_of_year}0.{str(year)[-2:]}n"
    obs_file = f"{location}{day_of_year}0.{str(year)[-2:]}o"
    output_rdeph = f"rdeph_output_{i}.txt"
    output_rdrnx = f"rdrnx_output_{i}.txt"

    # Run Fortran programs
    run_rdeph(nav_file, output_rdeph)
    run_rdrnx(obs_file, output_rdrnx)


if __name__ == "__main__":
    # Set date for processing
    year, month, day = 2011, 3, 11

    # Read list.txt for location names
    list_file = os.path.abspath("../../data/list.txt")
    if not os.path.exists(list_file):
        raise FileNotFoundError(f"List file not found: {list_file}")
    
    with open(list_file, 'r') as file:
        locations = [line.split()[1] for line in file.readlines()]

    for i, location in enumerate(locations):
        call_fortran(year, month, day, i, location)

        # Prepare file paths for VTEC calculation
        input_nav = f"../data/rdeph/rdeph_output_{i}.txt"  # Generated satellite data
        input_obs = f"../data/rdrnx/rdrnx_output_{i}.txt"  # Generated STEC data
        output_calcvtec = f"../data/vtec/vtec_{i}.txt"  # VTEC result output
        obs_file = f"../data/obs/{location}{date_to_day_of_year(year, month, day)}0.{str(year)[-2:]}o"

        # Ensure VTEC output directory exists
        ensure_directory_exists(output_calcvtec)

        # Call VTEC calculation
        print(f"Start calculating VTEC for No.{i}")
        calculate_vtec(input_nav, input_obs, output_calcvtec, obs_file)
        print(f"VTEC calculation completed for No.{i}")

