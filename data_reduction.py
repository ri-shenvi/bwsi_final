import lib.bundle as bd
import numpy as np
import math


def reduce_data(bundle: dict) -> dict:
    """Reduces data to migitage repetition of scan values in order to create more clear back-projection

      Args:
        bundle (dictionary): bundle of mocap data and scan data
      Returns:
        bundle (dictionary): new bundle of mocap data and scan data with removed data
    """

    # Setting the configurations and creation of the bins
    # bin_dimensions: number of bins  |  bin_limit: number of similar position values allowed in each bin
    bin_dimension = 80
    bins = np.zeros((bin_dimension, bin_dimension, bin_dimension))
    bin_limit = 1

    # Retrieving scan and position data in a neat 2D array, creating new arrays that will consist of kept data
    scan_data = np.array(bundle["data"]).reshape(
        bundle["scan_count"], bundle["scan_length"])
    position_data = np.array(bundle["positions"]).reshape(
        int(len(bundle["positions"]) / 4), 4)
    position_data_new = []
    scan_data_new = []

    # Looping through position and scan data indexes, since they have the same length
    for i in range(len(position_data) - 1):
        # Calculating the indexes (block, row, column) of the specific bin for theta, x, and y
        theta_block_bin_index = int(
            position_data[i][3] * bin_dimension / (2 * math.pi))
        x_row_bin_index = int((position_data[i][0] + 5) * bin_dimension / 10)
        y_column_bin_index = int(
            (position_data[i][1] + 5) * bin_dimension / 10)

        # Checks whether bin limit has been reached, if not, adds the specific scan and position data at index to the new arrays
        # Also scan count will decrease and bin size will increase as a new bin value is added
        if bins[theta_block_bin_index][x_row_bin_index][y_column_bin_index] < bin_limit:
            position_data_new.append(position_data[i])
            scan_data_new.append(scan_data[i])
        else:
            bundle["scan_count"] -= 1
        bins[theta_block_bin_index][x_row_bin_index][y_column_bin_index] += 1

    # The new arrays are formatted weird, this formats them into nice 2d numpy arrays
    position_data_new = np.vstack(position_data_new)
    scan_data_new = np.vstack(scan_data_new)

    bundle["scan_count"] -= 1

    # replaces the values in the bundle dictionary with the new arrays
    bundle["positions"] = list(position_data_new.flatten())
    bundle["data"] = list(scan_data_new.flatten())
    return bundle
