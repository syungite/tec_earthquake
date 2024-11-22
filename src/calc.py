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

def time_to_str(seconds):
    """Convert seconds to a time string (HH:MM:SS)."""
    return str(datetime.timedelta(seconds=seconds))

def main():
    vtec_dir = "../data/vtec"  # Directory containing vtec_i.txt files

    M = 30
    N = 30
    t_begin, t_end = 4.35 * 3600, 6.8 * 3600  # Convert to seconds
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
        print(f"{j} {len(time0)} {len(vtec0)} {time0[0]}")
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
                print(f"{time_to_str(t)} {j}")
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

    # Plotting graph
    if len(c_t) > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        c_t = np.array(c_t)
        # Convert seconds to time string (HH:MM:SS) for x-axis labels
        time_labels = [time_to_str(t) for t in c_t[:, 0]]

        # Set background color to a lighter gray
        ax.set_facecolor('#F0F0F0')  # Set the background color to an even lighter gray
        fig.patch.set_facecolor('#F0F0F0')  # Set the entire figure's background to the lighter gray

        # Plotting data points (scatter plot)
        ax.scatter(time_labels, c_t[:, 1], s=10, color='r', zorder=5)  # Increase zorder to put points above the lines
        ax.set_title('Anomaly Values Over Time')
        ax.set_xlabel('Time (HH:MM:SS)')
        ax.set_ylabel('C(t)')
        ax.set_ylim(-5, 25)
        ax.grid(True, color='white', linestyle='-', linewidth=0.5, zorder=3)
        #print(time_labels)
        # Set x-axis major ticks every 30 minutes
        ax.set_xticks(time_labels[18::60])  # Show every second time point for 30-minute intervals

        # Add vertical lines every 15 minutes (every 30 time points)
        for i in range(0, len(c_t)-18, 30):  # Every 30 time points, which corresponds to 15 minutes
            ax.axvline(time_labels[i+18], color='white', linestyle='-', alpha=0.5, zorder=2)

        # Convert 5:46:00 to seconds and add vertical line at that point
        target_time_seconds = 5 * 3600 + 46 * 60  # Convert 5:46:00 to total seconds
        target_time_str = time_to_str(target_time_seconds)  # Convert back to HH:MM:SS for plotting

        # Add the vertical line at 5:46:00 (in seconds)
        ax.axvline(target_time_str, color='black', linestyle='-', alpha=0.8, zorder=1)  # Black line at 5:46:00

        # Adjust the layout to prevent overlap
        plt.tight_layout()

        # Save and display the plot
        plt.savefig("../data/anomaly_plot.png", dpi=300)  # High-quality image
        plt.show()
    else:
        print("No valid data to plot.")


if __name__ == "__main__":
    main()
