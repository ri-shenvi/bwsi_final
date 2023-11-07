from matplotlib import pyplot as plt
import numpy as np
from lib.bundle import get_all_bundles, get_bundle, bundle_data
from backproj.use_bundle import backproj_bundle
from processor.data_reduction import reduce_data
from scipy.ndimage import label

def backprojection(bundle):
    # load it as a test
    #bundle = get_all_bundles()

    # bundle = reduce_data(bundle)

    scan_length = bundle["scan_length"]
    positions = bundle["positions"]
    scans = bundle["data"]
    scan_count = bundle["scan_count"]
    bin_start = bundle["bin_start"]
    bin_end = bundle["bin_end"]


    # reshape scans
    scans = np.array(scans).reshape((scan_count, scan_length))

    # flip scans vertically
    scans = np.flip(scans, axis=0)

    # reshape positions
    positions = np.array(positions).reshape((scan_count, 4))

    # cut out first 2 columns
    positions = positions[:, 0:3]

    # compute distance from 2.52 0.46 at every positions
    distances = np.linalg.norm(positions - [-1.14, 1, 0], axis=1)

    # set distances above 100 to 0
    distances[distances > 100] = 0

    # check for infs
    scans[np.isinf(scans)] = 0

    scans = np.power(2, scans)


    # convert to int list
    bundle["data"] = scans.astype(int).flatten().tolist()

    # imshow scans
    plt.imshow(scans, extent=[bin_start, bin_end, 0, scan_count], aspect="auto")
    plt.plot(distances, np.arange(scan_count), color="red")
    plt.show()


    data = backproj_bundle(bundle)

    # Create a binary heatmap (for demonstration purposes)
    threshold = 7600
    binary_heatmap = data["data"] > threshold

    # Label connected components (blobs) in the binary heatmap
    labeled_array, num_features = label(binary_heatmap)

    # Find blob coordinates
    blob_coordinates = []
    for label_value in range(1, num_features + 1):
        y_coords, x_coords = np.where(labeled_array == label_value)
        blob_coordinates.append((x_coords, y_coords))

    plt.imshow(data["data"], cmap="jet")

    for x_coords, y_coords in blob_coordinates:
        plt.plot(x_coords, y_coords, 'ko', markersize=5, alpha=0.5)  # Red circles for blobs

    num_ticks = 6  # Number of desired ticks
    tick_locations = np.linspace(0, 1000, num_ticks)
    x_tick_labels = np.round(np.linspace(-5, 5, num_ticks), decimals=2)
    y_tick_labels = np.round(np.linspace(5, -5, num_ticks), decimals=2)
    plt.xticks(tick_locations, x_tick_labels)
    plt.yticks(tick_locations, y_tick_labels)

    # plot the scan positions
    # print(positions)
    # plt.plot(positions[:, 0], positions[:, 1],
    #         marker="o", markersize=2, color="black")

    plt.colorbar()
    plt.show()

print(backprojection(get_bundle('/Users/thaarun/t2radar/bundles/bndl-2023-08-03_09-27-12.pkl')))