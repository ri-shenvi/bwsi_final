import pickle
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib import colors
from scipy.ndimage import label

# atan2

def find_distance(x_pix, x_drone, y_pix, y_drone, z_pix, z_drone):
    return np.sqrt(np.power(x_pix - x_drone, 2) + np.power(y_pix - y_drone, 2) + np.power(z_pix - z_drone, 2))

def find_steps_index(distance, bins_start, bins_interval):
    return int((distance - bins_start) / bins_interval - 1)

def find_m_from_origin_of_pixel(pixel_x, pixel_y):
    pixel_xy = []
    pixel_xy.append((pixel_x - 50) / 5)
    pixel_xy.append((0 - pixel_y + 50) / 5)
    return pixel_xy

def is_pixel_in_sight_2D_with_direction(x_drone, y_drone, x_pix, y_pix, x_direction_deg):
    # Calculate the angle (in degrees) between the drone and the pixel
    angle_deg = 180 / math.pi * math.atan2(y_pix - y_drone, x_pix - x_drone)

    # Normalize the pixel angle to [0, 360)
    angle_deg = (angle_deg + 360) % 360

    if (x_direction_deg > 67.5 and x_direction_deg < 135):
        x_direction_deg = (450 - x_direction_deg) % 360
        if ((x_direction_deg + 112.5 + 360) % 360 >= (angle_deg + 450) % 360 
            and (x_direction_deg + 67.5 + 360) % 360 <= (angle_deg + 450) % 360):
            return True
        else: return False

    x_direction_deg = (450 - x_direction_deg) % 360
    if angle_deg <= x_direction_deg + 22.5 and angle_deg >= (x_direction_deg + 337.5) % 360:
        return True
    else: return False


def pickle_reader(filePath):
    # Read data from the pickle file
    with (open(filePath, "rb")) as openfile:
        data = pickle.load(openfile)

    # Extract scan data, platform position, and range bins from the loaded data
    scan_data = np.abs(np.real(data["scan_data"]))
    platform_pos = data["platform_pos"]
    range_bins = data["range_bins"]

    # Calculate the start, end, and interval of the range bins
    bins_start = range_bins[0]
    bins_end = range_bins[len(range_bins) - 1]
    bins_interval = (bins_end - bins_start) / len(range_bins)

    # Initialize a grid to store amplitude and hits data
    grid_amp = np.zeros((100, 100))
    grid_hits = np.zeros((100, 100))

    # Process each position array in the platform_pos data
    for position_arr_index in range(len(platform_pos)):
        print("Scan completed: " + str(position_arr_index))
        # Process each pixel row and pixel in the grid
        for pixel_row_index in range(100):
            for pixel_index in range(100):
                # Convert pixel indices to meters from origin (0,0)
                m_from_origin_xy = find_m_from_origin_of_pixel(pixel_index, pixel_row_index)

                # Calculate the distance between the pixel and the platform position
                distance = find_distance(m_from_origin_xy[0], platform_pos[position_arr_index][0], 
                                         m_from_origin_xy[1], platform_pos[position_arr_index][1], 
                                         0, platform_pos[position_arr_index][2])

                # Calculate the index of the range bin that corresponds to the distance
                steps_index = find_steps_index(distance, bins_start, bins_interval)

                # Update the grid with scan data if the steps index is within the scan data range
                if steps_index < len(scan_data[position_arr_index]):
                    grid_amp[pixel_row_index][pixel_index] += scan_data[position_arr_index][steps_index]

                # Update the grid hits count
                grid_hits[pixel_row_index][pixel_index] += 1

    # Calculate the average amplitude and take the logarithm (log10) of the result
    grid_amp = grid_amp / grid_hits
    grid_amp = np.log10(grid_amp)

    # Threshold the grid_amp to create a binary heatmap
    threshold = 3.4  # Adjust this value as needed
    binary_heatmap = grid_amp > threshold

    # Label connected components (blobs) in the binary heatmap
    labeled_array, num_features = label(binary_heatmap)

    # Find blob coordinates
    blob_coordinates = []
    for label_value in range(1, num_features + 1):
        y_coords, x_coords = np.where(labeled_array == label_value)
        blob_coordinates.append((x_coords, y_coords))

    # Convert the list of tuples to a more usable format (e.g., NumPy array)
    blob_coordinates_array = np.array(blob_coordinates)

    # Print or process the blob coordinates as needed
    for index, (x_coords, y_coords) in enumerate(blob_coordinates_array):
        print(f"Blob {index + 1} coordinates:")
        for x, y in zip(x_coords, y_coords):
            print(f"X: {x / 5}, Y: {y / 5}")
        print("-" * 20)

    # Plot the back-projected image with detected blobs
    plt.figure(figsize=(8, 6))  # Adjust the figure size as needed

    # Plot the back-projected image using the calculated grid data
    colors_list = ['#FF5733', '#FFC300']
    cmap = colors.ListedColormap(colors_list)

    max = np.amax(grid_amp)
    min = np.amin(grid_amp)
    plt.pcolor(grid_amp, vmin=min, vmax=max)
    plt.clim(0, max)
    plt.colorbar()

    # Plot the blobs
    for x_coords, y_coords in blob_coordinates:
        plt.plot(x_coords, y_coords, 'ro', markersize=10)  # Red circles for blobs

    plt.title("Back-Projected Image (dB)")
    plt.xlabel("X Range (m)")
    plt.ylabel("Y Range (m)")

    """num_ticks = 6  # Number of desired ticks
    tick_locations = np.linspace(0, 100, num_ticks)
    tick_labels = np.round(np.linspace(0, 20, num_ticks), decimals=2)
    plt.xticks(tick_locations, tick_labels)
    plt.yticks(tick_locations, tick_labels)"""

    # Display the plot
    plt.show()

# Call the pickle_reader function with the specified file path
pickle_reader("/Users/rishithprathi/Downloads/t2radar/data/5_point_scatter.pkl")

"""for x1 in range(-10,10):
    for y1 in range(-10,10):
        for x in range(-10,10):
            for y in range(-10,10):
                for direction in range(-180, 180,10):
                    print(is_pixel_in_sight_2D_with_direction(x1,y1,x,y,direction))"""
