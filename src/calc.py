import numpy as np
import matplotlib.pyplot as plt
import os

def load_vtec_data(file_path):
    """Load VTEC data from the given file, with time >= 2.00 constraint."""
    data = np.loadtxt(file_path)
    time = data[:, 0]
    vtec = data[:, 1]

    # Time >= 2.00の範囲でフィルタリング
    mask = (time >= 2.00) & (time <= 8.50)
    time_filtered = time[mask]
    vtec_filtered = vtec[mask]
    
    # 差分を計算
    delta_t_filtered = np.diff(time_filtered, prepend=time_filtered[0])
    
    return time_filtered, vtec_filtered, delta_t_filtered


def fit_polynomial(time, vtec, degree=7):
    """Fit a polynomial of given degree to the time and VTEC data."""
    coeffs = np.polyfit(time, vtec, degree)  
    return np.poly1d(coeffs)  # Return the polynomial function

def cal_anomaly(time, vtec, t):
    # Use the time range for polynomial approximation
    mask_approx = (time >= 2.00 + t) & (time <= 4.00 + t)
    time_approx = time[mask_approx]
    vtec_approx = vtec[mask_approx]
    
    # Fit a 7th degree polynomial
    if len(time_approx) == 0 or len(vtec_approx) == 0:
        print(f"Skipping polynomial fit for t={t} due to insufficient data")
        return np.array([])
    
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
    
    anomaly = vtec_actual[:min_length] - vtec_approx_compare[:min_length]   
    return anomaly

def main():
    vtec_dir = "../data/vtec"  # Directory containing vtec_i.txt files

    v0_file = os.path.join(vtec_dir, f"vtec_0.txt")
    time0, vtec0, delta_t = load_vtec_data(v0_file)

    time0_max = np.amax(time0)
    mask_delta = delta_t <= (time0_max - 2.00)
    delta_use = delta_t[mask_delta]
    l = len(delta_use)

    M = 30
    N = 30
    t = 0
    c_t = []

    for i in range(l):
        t += delta_use[i]  
        if t + 4.25 >= 6.0: continue
        c = 0
        if i >= len(delta_use):
            continue 

        for j in range(1, 31):  # vtec_i.txt files (0 <= j <= 50)
            vtec_file = os.path.join(vtec_dir, f"vtec_{j}.txt")
                
            # Load the VTEC data
            time, vtec, delta = load_vtec_data(vtec_file)
            anomaly_0 = cal_anomaly(time0, vtec0, t)
            anomaly_j = cal_anomaly(time, vtec, t)

            if len(anomaly_0) == 0 or len(anomaly_j) == 0:
                print(f"Skipping due to insufficient anomaly data for t={t}")
                continue

            # Ensure both anomalies are the same length
            min_length = min(len(anomaly_0), len(anomaly_j))
            for k in range(min_length):
                c += anomaly_0[k] * anomaly_j[k]

        c = c / (M * N * 100)
        c_t.append((4.25 + t, c))

    # plotting graph
    if len(c_t) > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        c_t = np.array(c_t)
        ax.scatter(c_t[:, 0], c_t[:, 1], s= 15 , color='r')
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


