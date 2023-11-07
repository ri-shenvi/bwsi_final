# Interpolation of Motion Capture Data
Interpolation of motion capture data is a technique used to estimate values for missing data points within a dataset. In the context of the provided script, interpolation is used to match motion capture data to radar scan times, enabling a more accurate alignment of the two datasets.

# The Problem
Motion capture data and radar scan data may not be recorded at the exact same timestamps. This misalignment can lead to inaccuracies when comparing or analyzing the two datasets. To address this issue, we need to find a way to associate each motion capture data point with the corresponding radar scan time.

# The Solution
To align the motion capture data with radar scan times, an interpolation approach is used. The normalize_scans function, located in the processor.normalize_scans module, is responsible for this interpolation process.

The interpolation process involves the following steps:

- Data Preparation: The motion capture data is read from the provided CSV file using the custom mocap.read_csv function from the lib.read_csv module.

- Synchronization with Radar Scan Times: The script uses the get_radar_start_time function from lib.image_utils to obtain the radar's start time.

- Interpolation: The normalize_scans function then performs interpolation to match motion capture data to radar scan times. It estimates the motion capture data values at the timestamps of radar scans.

# Interpolation Technique

## Implementation Details
The interpolation process is implemented in the following function:
- processor.normalize_scans(motion_capture_data: np.    array, radar_data: dict) -> np.array
This function takes two parameters:

- motion_capture_data (np.array): The motion capture data as a NumPy array obtained from the CSV file.

- radar_data (dict): A dictionary containing radar scan data, including timestamps and scan measurements.
The function performs the interpolation to associate each motion capture data point with the corresponding radar scan time. The result is an array with the interpolated motion capture data synchronized with radar scan times.

Conclusion
 By using interpolation, the script ensures that the two datasets are synchronized, enabling meaningful comparisons and analyses between them. 