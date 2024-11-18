import numpy as np
import matplotlib.pyplot as plt
import os

def load_vtec_data(file_path, t_begin, t_end):
    """Load VTEC data from the given file, with time >= 2.00 constraint."""
    if not os.path.exists(file_path):
        print(f"File {file_path} not found, skipping.")
        return np.array([]), np.array([]), np.array([])  # Return empty arrays if file doesn't exist

    try:
        data = np.loadtxt(file_path)
        time = data[:, 0]
        vtec = data[:, 1]

        # filtering the time 
        mask = (time >= t_begin - 2.25) & (time <= t_end)
        time_filtered = time[mask]
        vtec_filtered = vtec[mask]

        # calculate the diffusion
        delta_t_filtered = np.diff(time_filtered, prepend=time_filtered[0])

        return time_filtered, vtec_filtered, delta_t_filtered
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return np.array([]), np.array([]), np.array([])  # Return empty arrays in case of error

def cal_anomaly(time, vtec, t):
    """Calculate the anomaly between actual VTEC and polynomial approximation."""
    # Set the time range for polynomial approximation
    mask_approx = (time >= t - 2.249) & (time < t - 0.25)
    time_approx = time[mask_approx]
    vtec_approx = vtec[mask_approx]

    if len(time_approx) < 2 or len(vtec_approx) < 2:
        print(f"Skipping polynomial fit for t={t} due to insufficient data")
        return np.array([])

    # Fit a polynomial
    res = np.polynomial.Polynomial.fit(time_approx, vtec_approx, 7)

    # Use the time range to compute the difference
    mask_compare = (time >= t - 0.25) & (time < t)
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



def main():
    vtec_dir = "../data/vtec"  # Directory containing vtec_i.txt files

    M = 30
    N = 30
    t, t_begin, t_end = 0, 14.85, 16.6
    t += t_begin

    v0_file = os.path.join(vtec_dir, "vtec_0.txt")
    time0, vtec0, delta_t = load_vtec_data(v0_file, t_begin, t_end)
    l = len(delta_t)

    c_t = []

    for i in range(l):
        t += delta_t[i]
        if t >= t_end:
            continue
        c = 0
        n = 0
        non_valid_data = False  
        for j in range(1, M+1): 
            vtec_file = os.path.join(vtec_dir, f"vtec_{j}.txt")

            # Load the VTEC data
            time, vtec, delta = load_vtec_data(vtec_file, t_begin, t_end)

            anomaly_0 = cal_anomaly(time0, vtec0, t)
            anomaly_j = cal_anomaly(time, vtec, t)

            # Ensure both anomalies are the same length (all data are fully exist)
            min_length = min(len(anomaly_0), len(anomaly_j))
            n = max(n, min_length)
            for k in range(N):
                try:
                    c += anomaly_0[k] * anomaly_j[k]
                except IndexError:
                    c += 0 

        if(non_valid_data):
            print(f"{t}: nonvalid")
            continue

        c = c / (M * N)
        c_t.append((t, c))

    # plotting graph
    if len(c_t) > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        c_t = np.array(c_t)
        ax.scatter(c_t[:, 0], c_t[:, 1], s=15, color='r')
        ax.set_title('Anomaly Values Over Time')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('C(t)')
        ax.set_ylim(-5, 40)
        ax.grid(True)
        plt.tight_layout()
        plt.savefig("../data/anomaly_plot.png")
        plt.show()
    else:
        print("No valid data to plot.")


if __name__ == "__main__":
    main()



