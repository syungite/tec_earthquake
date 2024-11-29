import numpy as np
import matplotlib.pyplot as plt
import datetime

def time_to_str(seconds):
    """Convert seconds to a time string (HH:MM:SS)."""
    return str(datetime.timedelta(seconds=seconds))

def anomaly_plotting(c_t, plotting_path):
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

        # # Convert 5:46:00 to seconds and add vertical line at that point
        # target_time_seconds = 5 * 3600 + 46 * 60  # Convert 5:46:00 to total seconds
        # target_time_str = time_to_str(target_time_seconds)  # Convert back to HH:MM:SS for plotting

        # # Add the vertical line at 5:46:00 (in seconds)
        # ax.axvline(target_time_str, color='black', linestyle='-', alpha=0.8, zorder=1)  # Black line at 5:46:00

        # Adjust the layout to prevent overlap
        plt.tight_layout()
        # Save and display the plot
        plt.savefig(plotting_path, dpi=300)  # High-quality image
        plt.show()
    else:
        print("No valid data to plot.")    