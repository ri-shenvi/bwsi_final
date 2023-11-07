import numpy as np
import matplotlib.pyplot as plt


def generate_heatmap(radar_data: dict, unit="m", show_start_time=False):
    """Generates a heatmap from the provided data file.

    Args:
        filePath (str): Full path to data file.
        unit (str): Unit of measurement for range axis. Defaults to meters.
    """
    data = radar_data["data"]
    times = radar_data["time"]
    start = radar_data["start"]
    end = radar_data["end"]
    filter_count = radar_data["filters_applied"]

    (rows, cols) = data.shape

    # get max in data
    max = np.amax(data)
    # get min in data
    min = np.amin(data)

    if show_start_time:
        plt.subplot(121)

     # flip data over x axis
    data = np.flip(data, 0)

    start_time = 0
    end_time = (times[-1]-times[0]) / 1000.0

    # plot the data in a heatmap using imshow
    plt.imshow(data, vmax=max, vmin=min, extent=[
               start, end, start_time, end_time], aspect="auto")

    # scale the color bar according to min and max
    plt.clim(0, max)

    plt.colorbar()

    plt.title("Range Time Intensity")
    plt.xlabel(f"Range ({unit})")
    plt.ylabel("Time Elapsed (s)")

    if show_start_time:

        plt.subplot(122)

        # num_ticks = 10  # Number of desired ticks
        # tick_locations = np.linspace(start, cols - 1, num_ticks)
        # tick_labels = np.round(np.linspace(
        #    0, (times[-1] - times[0]) / 1000.0, num_ticks), decimals=2)
        plt.title("Row similarity")
        plt.xlabel("Time")
        plt.ylabel("Correlation coef")
        # plt.xticks(tick_locations, end_time = (times[-1]-times[0]) / 1000.0)

        # create an array of times
        times = np.linspace(start_time, end_time, rows)

        # move_time vs times
        plt.plot(times, radar_data["move_time"], color='red')
        
        # corr_coefs vs times
        plt.plot(times, radar_data["corr_coefs"], color='blue')
    plt.show()
