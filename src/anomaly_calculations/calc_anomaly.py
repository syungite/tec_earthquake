import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
import os
import datetime

def load_vtec_data(file_path, t_begin, t_end):
    """Load VTEC data from the given file, with constraint."""
    try:
        data = np.loadtxt(file_path)
        time = data[:, 0]  # Time in seconds
        vtec = data[:, 1]

        # Filtering the time
        mask = (time >= t_begin - 8100) & (time <= t_end)
        time_filtered = time[mask]
        vtec_filtered = vtec[mask]

        return time_filtered, vtec_filtered

    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return np.array([]), np.array([])

def cal_anomaly(time, vtec, t):
    """Calculate the anomaly between actual VTEC and polynomial approximation."""
    # Set the time range for polynomial approximation
    mask_approx = (time >= t - 8100) & (time < t - 900)
    time_approx = time[mask_approx]
    vtec_approx = vtec[mask_approx]

    if len(time_approx) < 2 or len(vtec_approx) < 2:
        print(f"Skipping polynomial fit for t={t} due to insufficient data")
        return np.array([])

    # Polynomial fitting
    res = np.polynomial.Polynomial.fit(time_approx, vtec_approx, 7)

    # Use the time range to compute the difference
    mask_compare = (time >= t - 900) & (time < t)
    time_compare = time[mask_compare]
    vtec_actual = vtec[mask_compare]

    if len(time_compare) == 0 or len(vtec_actual) == 0:
        print(f"No valid comparison data for t={t}")
        return np.array([])

    # Calculate the polynomial approximation
    vtec_compare = res(time_compare)

    # Calculate anomaly
    anomaly = vtec_actual - vtec_compare

    return anomaly



def calc_anomally_and_plot(start_time, end_time):
    vtec_dir = "../data/vtec"  # Directory containing vtec_i.txt files

    M = 30
    N = 30
    t_begin, t_end = start_time * 3600, end_time * 3600  # Convert to seconds
    t = t_begin
    v0_file = os.path.join(vtec_dir, "vtec_0_output.txt")
    time0, vtec0 = load_vtec_data(v0_file, t_begin, t_end)
    mask = (time0 >= t_begin) & (time0 < t_end)
    time_delta = time0[mask]
    l = len(time_delta)
    for j in range(0, M + 1): 
        vtec_file = os.path.join(vtec_dir, f"vtec_{j}_output.txt")

        # Load the VTEC data
        time0, vtec0 = load_vtec_data(v0_file, t_begin, t_end)
    c_t = []

    for i in range(l):
        c = 0

        for j in range(1, M + 1): 
            vtec_file = os.path.join(vtec_dir, f"vtec_{j}_output.txt")

            # Load the VTEC data
            time0, vtec0 = load_vtec_data(v0_file, t_begin, t_end)
            time, vtec = load_vtec_data(vtec_file, t_begin, t_end)
            only_in_time0 = set(time0) - set(time)
            only_in_time = set(time) - set(time0)
            if(len(only_in_time) > 0 or len(only_in_time0) > 0):
                print("Only in time0:", only_in_time0)
                print("Only in time:", only_in_time)

            anomaly_0 = cal_anomaly(time0, vtec0, t)
            anomaly_j = cal_anomaly(time0, vtec, t)
            # Every length of anomaly_j is 30 (At 2011/3/11)
            for k in range(30):
                try:
                    c += anomaly_0[k] * anomaly_j[k]
                except IndexError:
                    c += 0 

        c = c / (M * N)
        #print(f"{time_to_str(t)} {c}")
        c_t.append((t, c))
        t += 30
    return c_t
    


if __name__ == "__main__":
    calc_anomally_and_plot()
