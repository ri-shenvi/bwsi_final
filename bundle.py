import numpy as np
import lib.read_csv as mocap
from lib.file_utils import read_data_file
from processor.normalize_scans import normalize_scans
from lib.image_utils import get_radar_start_time
import pickle
import lib.filter_utils as filters


def bundle_data(pickle_path: str, csv_path: str, filter_strength=8, filter_boost_thresh=2) -> str:
    pkl = read_data_file(pickle_path)

    pkl = get_radar_start_time(pkl)

    motion_capture_file_path = csv_path
    motion_capture_data = mocap.read_csv(
        motion_capture_file_path, "FS2mocap")

    # motion capture data
    # Replace with the actual file path

    # Matching motion capture data to scan times
    positions = normalize_scans(motion_capture_data, pkl)

    # number of timeframes
    scan_count = pkl["data"].shape[0]

    # Number of scans within a certain time
    scan_length = pkl["data"].shape[1]

    filtered_data = filters.apply_filter(pkl, strength=filter_strength,
                                         boost_thresh=filter_boost_thresh)

    # flatten data
    data = filtered_data["data"].flatten()

    data = [int(x) for x in data]

    positions = positions.flatten()
    positions = [float(x) for x in positions]

    bin_start = pkl["start"]
    bin_end = pkl["end"]
    bin_size = 0.009159475944479724

    # combine data and positions
    combined = np.hstack((positions, data))

    # convert to an object
    bundle = {
        "scan_count": scan_count,
        "scan_length": scan_length,
        "bin_start": bin_start,
        "bin_end": bin_end,
        "bin_size": bin_size,
        "data": combined
    }

    # write to a pickle file
    name = pickle_path.split("/")[-1].split(".")[0]
    pickle.dump(bundle, open(f"bundles/bndl-{name}.pkl", "wb"))

    return f"bundles/{name}.pkl"


def get_bundle(path: str) -> dict:
    """Load a bundle from a pickle file.

    Args:
        path (str): The path to the pickle file.

    Returns:
        dict: The bundle.
    """

    bundle = pickle.load(open(path, "rb"))

    data = bundle["data"]
    scan_count = bundle["scan_count"]
    scan_length = bundle["scan_length"]
    bin_start = bundle["bin_start"]
    bin_end = bundle["bin_end"]
    bin_size = bundle["bin_size"]

    # positions is the first 4 columns
    positions = data[:scan_count*4]
    positions = np.array(positions).reshape((scan_count, 4))

    # data is the rest
    data = data[scan_count*4:]
    data = np.array(data).reshape((scan_count, scan_length))

    # convert all entries to integers
    data = np.array(data, dtype=int)

    # convert to regular list
    data = data.flatten()
    data = data.tolist()

    # same to positions
    positions = positions.flatten()
    positions = positions.tolist()

    return {
        "data": data,
        "positions": positions,
        "scan_count": scan_count,
        "scan_length": scan_length,
        "bin_start": bin_start,
        "bin_end": bin_end,
        "bin_size": bin_size
    }


def merge_bundles(bundle1: dict, bundle2: dict) -> dict:

    # check if bins are compatible
    if bundle1["bin_start"] != bundle2["bin_start"] or bundle1["bin_end"] != bundle2["bin_end"] or bundle1["bin_size"] != bundle2["bin_size"]:
        raise ValueError("Bundles have incompatible bins")

    # merge data & positions
    data = bundle1["data"] + bundle2["data"]
    positions = bundle1["positions"] + bundle2["positions"]

    # merge scan_count & scan_length
    scan_count = bundle1["scan_count"] + bundle2["scan_count"]
    scan_length = bundle1["scan_length"]

    # export
    return {
        "data": data,
        "positions": positions,
        "scan_count": scan_count,
        "scan_length": scan_length,
        "bin_start": bundle1["bin_start"],
        "bin_end": bundle1["bin_end"],
        "bin_size": bundle1["bin_size"]
    }


def get_all_bundles() -> dict:
    """Get all bundles from the data folder.

    Returns:
        dict: A dictionary of all bundles.
    """
    from os import listdir
    from os.path import isfile, join

    # get all files in the bundles folder
    filenames = [f for f in listdir("bundles") if isfile(join("bundles", f))]

    # get all bundles
    bundles = []
    for filename in filenames:
        bundles.append(get_bundle(join("bundles", filename)))

    # merge all bundles
    bundle = bundles[0]

    for i in range(1, len(bundles)):
        bundle = merge_bundles(bundle, bundles[i])

    return bundle
