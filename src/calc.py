import numpy as np
import matplotlib.pyplot as plt
import os

def load_vtec_data(file_path):
    """Load VTEC data from the given file, with time >= 2.00 constraint."""
    if not os.path.exists(file_path):
        print(f"File {file_path} not found, skipping.")
        return np.array([]), np.array([]), np.array([])  # Return empty arrays if file doesn't exist

    try:
        data = np.loadtxt(file_path)
        time = data[:, 0]
        vtec = data[:, 1]

        # Time >= 2.00の範囲でフィルタリング
        mask = (time >= 2.00) & (time <= 7.50)
        time_filtered = time[mask]
        vtec_filtered = vtec[mask]

        # 差分を計算
        delta_t_filtered = np.diff(time_filtered, prepend=time_filtered[0])

        return time_filtered, vtec_filtered, delta_t_filtered
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return np.array([]), np.array([]), np.array([])  # Return empty arrays in case of error


def cal_anomaly(time, vtec, t):
    """Calculate the anomaly between actual VTEC and polynomial approximation."""
    # Use the time range for polynomial approximation
    mask_approx = (time >= 2.00 + t) & (time <= 4.00 + t)
    time_approx = time[mask_approx]
    vtec_approx = vtec[mask_approx]

    if len(time_approx) == 0 or len(vtec_approx) == 0:
        print(f"Skipping polynomial fit for t={t} due to insufficient data")
        return np.array([])

    # Fit a 7th degree polynomial
    poly = np.polyfit(time_approx, vtec_approx, 7)

    # Use the time range to compute the difference
    mask_compare = (time >= 4.00 + t) & (time <= 4.25 + t)
    time_compare = time[mask_compare]
    vtec_actual = vtec[mask_compare]
    vtec_approx_compare = np.polyval(poly, time_compare)

    # Calculate anomaly, ensuring both arrays have the same length
    min_length = min(len(vtec_actual), len(vtec_approx_compare))
    if min_length == 0:
        print(f"No valid comparison data for t={t}")
        return np.array([])

    anomaly = (vtec_actual[:min_length] - vtec_approx_compare[:min_length])
    anomaly -= np.mean(anomaly)
    return anomaly


def main():
    vtec_dir = "../data/vtec"  # Directory containing vtec_i.txt files

    v0_file = os.path.join(vtec_dir, "vtec_0.txt")
    time0, vtec0, delta_t = load_vtec_data(v0_file)

    if len(time0) == 0 or len(vtec0) == 0:
        print("No valid data in vtec_0.txt, exiting.")
        return

    time0_max = np.amax(time0)
    mask_delta = delta_t <= (time0_max - 2.00)
    delta_use = delta_t[mask_delta]
    l = len(delta_use)

    M = 30
    N = 50
    t = 0
    c_t = []

    for i in range(l):
        t += delta_use[i]
        if t + 4.25 >= 6.0:
            continue

        c = 0
        n = 1e10
        valid_data = True  # A flag to track if we got enough data across all j
        for j in range(1, 31):  # vtec_i.txt files (1 <= j <= 30)
            vtec_file = os.path.join(vtec_dir, f"vtec_{j}.txt")

            # Load the VTEC data
            time, vtec, delta = load_vtec_data(vtec_file)
            if len(time) == 0 or len(vtec) == 0:
                valid_data = False  # If any file lacks sufficient data, skip this i
                break

            anomaly_0 = cal_anomaly(time0, vtec0, t)
            anomaly_j = cal_anomaly(time, vtec, t)

            if len(anomaly_0) == 0 or len(anomaly_j) == 0:
                valid_data = False  # Insufficient data for comparison, skip this i
                break

            # Ensure both anomalies are the same length
            min_length = min(len(anomaly_0), len(anomaly_j))
            n = min(n, min_length)
            for k in range(min_length):
                c += anomaly_0[k] * anomaly_j[k]

        if not valid_data:
            print(f"Skipping t={t} due to insufficient data across some files.")
            continue  # Skip this iteration of i if any j failed

        c = c / (M * n)
        c_t.append((4.25 + t, c))

    # plotting graph
    if len(c_t) > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        c_t = np.array(c_t)
        ax.scatter(c_t[:, 0], c_t[:, 1], s=15, color='r')
        ax.set_title('Anomaly Values Over Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('C(t)')
        ax.grid(True)
        plt.tight_layout()
        plt.savefig("../data/anomaly_plot.png")
        plt.show()
    else:
        print("No valid data to plot.")


if __name__ == "__main__":
    main()



