import numpy as np
from backproj.wrapper import BackProj


def backproj_bundle(bundle: dict) -> dict:
    """ Back project a bundle.

    Args:
        bundle (dict): The bundle.

    Returns:
        dict: The back projection. Keys:
            - data (list): The back projected pixels.
            - top_x (float): The top x coordinate.
            - top_y (float): The top y coordinate.
            - width (float): The width of the back projection.
            - height (float): The height of the back projection.
            - pix_m (float): The number of pixels per m.

    """

    scan_count = bundle["scan_count"]
    scan_length = bundle["scan_length"]
    bin_start = bundle["bin_start"]
    bin_end = bundle["bin_end"]
    bin_size = bundle["bin_size"]

    scans = bundle["data"]
    positions = bundle["positions"]

    # convert scans to ints
    scans = np.array(scans, dtype=int)

    # flatten and convert to list
    scans = scans.flatten()
    scans = scans.tolist()

    # create a back projection object
    bp = BackProj(scans, positions, scan_count, scan_length,
                  bin_start, bin_end, bin_size)

    # get the back projection
    back_projection = bp.getRegion(-5, -5, 0, 10, 10, 100)

    return {
        "data": back_projection,
        "top_x": -5,
        "top_y": -5,
        "width": 10,
        "height": 10,
        "pix_m": 100
    }
