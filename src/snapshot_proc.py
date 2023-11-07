import matplotlib.pyplot as plt
from backproj.wrapper import BackProj
from lib.file_utils import read_data_file
import numpy as np
from scipy.ndimage import label
import math
import pickle

with open("data/send_to_team_2.pkl", "rb") as f:
    data = pickle.load(f)

threshold = 4800
binary_heatmap = data > threshold

labeled_array, num_features = label(binary_heatmap)

blob_coordinates = []
for label_values in range(1, num_features + 1):
    y_coords, x_coords = np.where(labeled_array == label_values)
    blob_coordinates.append([x_coords, y_coords])

# Reduce clusters with multiple coordinates to just one coordinate
for i in range(len(blob_coordinates)):
    if len(blob_coordinates[i]) > 1:
        blob_coordinates = [[x[:1], y[:1]] for x, y in blob_coordinates]

# Only keeps distinct coordinates through bin method
# Assumes first value is a distinct value
distinct_values = [blob_coordinates[0]]
for i in range(1, len(blob_coordinates)):
    distance_between_coords = []
    count = 0
    for val in distinct_values:
        # Calculating distance between current coord and all distinct values
        distance = math.sqrt(math.pow(val[0][0] - blob_coordinates[i][0][0], 2) +
                             math.pow(val[1][0] - blob_coordinates[i][1][0], 2))
        distance_between_coords.append(distance)
    for dist in distance_between_coords:
        # Checking if the current coord is a new distinct value by checking how close it is to distinct values
        if dist > 200:
            count += 1
    # If the distance between current coord and distinct values is completely new, adds to distinct values
    if count == len(distinct_values):
        distinct_values.append(blob_coordinates[i])

for index, (x_coords, y_coords) in enumerate(distinct_values):
    print(f"Blob {index + 1} coordinates:")
    for x, y in zip(x_coords, y_coords):
        print(f"X: {x * 0.028 - 2}, Y: {y * 0.028 - 2}")
    print("-" * 20)

# Plot the back-projected image with detected blobs
plt.figure(figsize=(8, 6))  # Adjust the figure size as needed

# flip data on x-axis to match the orientation of the radar
data = np.flipud(data)

plt.imshow(data, cmap="jet", extent=[-2, 12, -2, 12])

dim_x = data.shape[0]
dim_y = data.shape[1]

pix_x = 14.0 / dim_x
pix_y = 14.0/dim_y


# Plot the blobs
for x_coords, y_coords in blob_coordinates:
    plt.plot(x_coords * pix_x - 2, y_coords *
             pix_y - 2, "ko", markersize=6, alpha=0.8)

"""num_ticks = 9
tick_locations = np.linspace(0,500, num_ticks)
x_ticks_labels = np.round(np.linspace(-15, 15, num_ticks), decimals = 2)
y_ticks_labels = np.round(np.linspace(15, -15, num_ticks), decimals = 2)
plt.xticks(tick_locations, x_ticks_labels)
plt.yticks(tick_locations, y_ticks_labels)

plt.title("Back-Projected Image (dB)")
plt.xlabel("X Range (m)")
plt.ylabel("Y Range (m)")"""

plt.colorbar()
plt.show()
