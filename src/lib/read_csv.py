import pandas
import numpy as np


def read_csv(filepath: str, object_name: str) -> np.ndarray:
    """Reads the provided csv file.

    Args:
        filepath (str): Full path to csv file.
        object_name (str): Name of object to read from csv file.

    Returns:
        numpy array with time and object info

    """

    # read in csv
    df = pandas.read_csv(filepath, header=[2, 4, 5])

    # extracts time info
    times = df["Name"].to_numpy()
    if (object_name == "time"):
        return times

    info = df[object_name].to_numpy()

    # removes unnecessary columns
    info = np.delete(info, [7], axis=1)

    rotX = info[:, 1]
    rotY = info[:, 2]
    rotZ = info[:, 3]
    rotW = info[:, 4]

    # converts quaternion to yaw
    yaw = np.arctan2(2 * (rotY * rotZ + rotW * rotX), rotW *
                     rotW - rotX * rotX - rotY * rotY + rotZ * rotZ)

    # make sure yaw is between 0 and 2pi
    yaw[yaw < 0] += 2 * np.pi

    # delete first four columns and add yaw values as last column
    info = np.delete(info, [0, 1, 2, 3], axis=1)
    info = np.hstack((info, np.reshape(yaw, (yaw.shape[0], 1))))

    # FIXME: Swaps y and z coordinates. May need to delete if not needed
    info[:, [2, 1]] = info[:, [1, 2]]

    info = np.hstack((times, info))

    # remove any rows with NaN values
    info = info[~np.isnan(info).any(axis=1)]

    return info


def slice_csv(rawdata: np.ndarray, start_frame: int, end_frame: int) -> np.ndarray:
    """Slices the provided csv file.

    Args:
        rawdata (np.ndarray): Full data from csv file.
        start_frame (int): Starting frame to slice.
        end_frame (int): Ending frame to slice.

    Returns:
        numpy array with time and object info
    """
    return rawdata[start_frame:end_frame, :]
