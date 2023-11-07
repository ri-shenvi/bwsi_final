# Motion Capture Data Processing Functions Documentation

This document provides an overview and description of the three functions included in the provided Python script. These functions are designed to process motion capture data and align it with radar timestamps for further analysis and synchronization.

## interpolate_mocap_frames (mocap_data: np.ndarray, radar_timestamps: np.ndarray, time_delta=0) -> np.ndarray:

### Description: 
This function takes motion capture data and radar timestamps as inputs and interpolates the motion capture data to match the timestamps of the radar scans. The interpolation is performed based on the timestamps' proximity and time_delta. If a corresponding motion capture frame is not found for a radar frame (mocap time must be greater than or equal to radar time for specific), a default position is appended to the interpolated data. This function ensures that the motion capture data is aligned with the radar timestamps for further processing and analysis.

### Parameters
- mocap_data (np.ndarray): Motion capture data as a NumPy array containing timestamps and corresponding data points.

- radar_timestamps (np.ndarray): Radar timestamps as a NumPy array.

- time_delta (float, optional): Time delta to add to the radar timestamps (default: 0).

### Returns
- np.ndarray: Interpolated motion capture data with timestamps removed.

## def find_start_end(mocap_data: np.ndarray) -> (int, int):
This function determines the start and end points for slicing the motion capture data. It computes the velocity in each direction, smooths the velocity values using a convolution filter, and calculates the average velocity over the first and last 350 frames. The start and end points are determined by finding the first and last frames where the velocity exceeds 1.5 times the average.

### Parameters
- mocap_data (np.ndarray): Motion capture data as a NumPy array containing timestamps and corresponding data points.

### Returns
- start (int): The index representing the start point for slicing the motion capture data.
- end (int): The index representing the end point for slicing the motion capture data.
Description


## normalize_scans(mocap_data: np.ndarray, scan_data: dict) -> np.ndarray:
This function normalizes the motion capture data to match the radar timestamps.

### Parameters
- mocap_data (np.ndarray): Motion capture data as a NumPy array containing timestamps and corresponding data points.
- scan_data (dict): Radar scan data as a dictionary containing radar timestamps and scan measurements.

### Returns
- np.ndarray: Interpolated motion capture data with timestamps removed.

### Description
This function normalizes the motion capture data to match the timestamps of the radar scans. It calls the find_start_end function to determine the appropriate range for slicing the motion capture data. It then extracts the radar timestamps from scan_data, computes the time delta between the motion capture data and radar timestamps, and converts the radar timestamps to seconds. The function uses interpolate_mocap_frames to interpolate the motion capture data based on the radar timestamps and time delta. The result is a synchronized and aligned motion capture data array without timestamps, suitable for further processing and analysis.
