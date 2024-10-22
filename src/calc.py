import numpy as np
import matplotlib.pyplot as plt
import os

def load_vtec_data(file_path):
    """Load VTEC data from the given file."""
    data = np.loadtxt(file_path)
    return data[:, 0], data[:, 1]  # Return time and VTEC values

def fit_polynomial(time, vtec, degree=7):
    """Fit a polynomial of given degree to the time and VTEC data."""
    coeffs = np.polyfit(time, vtec, degree)  
    return np.poly1d(coeffs)  # Return the polynomial function


def main():
    vtec_dir = "../data/vtec"  # Directory containing vtec_i.txt files

    xi_dict = {}
    for i in range(51):  # Loop over vtec_i.txt files (0 <= i <= 50)
        vtec_file = os.path.join(vtec_dir, f"vtec_{i}.txt")
        output_graph = f"../data/graph/difference_graph_{i}.png" 
        output_anomaly_graph = f"../data/anomaly/anomaly_{i}.png" # Output graph file path
        
        if os.path.exists(vtec_file):
            print(f"Processing {vtec_file}")
            
            # Load the VTEC data
            time, vtec = load_vtec_data(vtec_file)
            
            # Use the time range 3.50 ~ 5.50 for polynomial approximation
            mask_approx = (time >= 3.50) & (time <= 5.50)
            time_approx = time[mask_approx]
            vtec_approx = vtec[mask_approx]
            
            # Fit a 7th degree polynomial
            poly = np.polynomial.polynomial.polyfit(time_approx, vtec_approx, 7)
            
            # Use the time range 5.50 ~ 5.75 to compute the difference
            mask_compare = (time >= 5.50) & (time <= 5.75)
            time_compare = time[mask_compare]
            vtec_actual = vtec[mask_compare]
            vtec_approx_compare =  np.polynomial.polynomial.polyval(time_compare, poly)
            anomaly = vtec_actual-vtec_approx_compare

            xi = []
            with open(output_anomaly_graph.replace(".png", ".txt"), 'w') as anomaly_file:
                for t, a in zip(time_compare, anomaly):
                    anomaly_file.write(f"{t} {a}\n")
                    xi.append((t,a))

            xi_dict[f"x{i}"] = xi


if __name__ == "__main__":
    main()

