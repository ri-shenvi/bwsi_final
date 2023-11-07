import numpy as np
import scipy as sp

KERNELS_3x3 = {
    # vals are standard in image processing
    "identity": np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]]),
    "edge_filter_1": np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]),
    "edge_filter_2": np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]]),
    "gausian": np.array([[1/16, 1/8, 1/16], [1/8, 1/4, 1/8], [1/16, 1/8, 1/16]])
}


KERNELS_5x5 = {
    # vals are standard in image processing
    "identity": np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]),
    "edge_filter_1": np.array([[-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, 12, -1, -1], [-1, -1, -1, -1, -1], [-1, -1, -1, -1, -1]]),
    "edge_filter_2": np.array([[0, 0,-1, 0, 0], [0, -1, -1, -1, 0], [-1, -1, 4, -1, -1], [0, -1, -1, -1, 0], [0, 0,-1, 0, 0]]),
    "gausian": np.array([[1, 4, 7, 4, 1], [4, 16, 26, 16, 4], [7, 26, 41, 26, 7], [4, 16, 26, 16, 4], [1, 4, 7, 4, 1]]) * (1/273)
}


def get_kernel(kernel_name: str) -> np.ndarray:
    """Returns 3x3 matrics coresponding to the provided filter name  
        Args: 
            kernel_name as string
        Returns:
            3x3 filter weights
    """
    if kernel_name in KERNELS_3x3:
        return KERNELS_3x3[kernel_name]
    else:
        return np.array([])

def get_5x5_kernel(kernel_name: str) -> np.ndarray:
    """Returns 5x5 matrics coresponding to the provided filter name  
        Args: 
            kernel_name as string
        Returns:
            3x3 filter weights
    """
    if kernel_name in KERNELS_5x5:
        return KERNELS_5x5[kernel_name]
    else:
        return np.array([])

def apply_filter(radar_data: dict, filter_name: str, filter_threshold=25, normalize=True) -> dict:
    """Applies chosen filter to radar data

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (numpy array), start (float), end (float); 
                where data is a numpy 2D array.
            filter_name - options available: edge_filter_1, edge_filter_2, gausian, identity
            filter_threshold - sets data to 0 for all values below it, applied after filter and normalization.
            normalize - true/false specifies if normalization should be applied to compensate filter adjustments
        Returns:
            filtered radar_data
    """
    data = radar_data["data"]
    time = np.array(radar_data["time"])

    # creates a 2D array of zeros that is the same size as the data array
    filtered = np.zeros(data.shape)

    filter_matrix = get_kernel(filter_name)

    # this uses numpy vectorization to calculate sum of 3x3
    # match cell and multiply with corresponding filter value (from kernels)
    # sliding 3x3 window is element-wise multiplied by filter matrix and all end results are summed up and stored in the center element of the sliding window
    # goes through original data, writes into an empty copy of the 2D array
    filtered[1:-1, 1:-1] = \
        (data[:-2, :-2] * filter_matrix[0, 0]) + \
        (data[:-2, 1:-1] * filter_matrix[0, 1]) + \
        (data[:-2, 2:] * filter_matrix[0, 2]) + \
        (data[1:-1, :-2] * filter_matrix[1, 0]) + \
        (data[1:-1, 1:-1] * filter_matrix[1, 1]) + \
        (data[1:-1, 2:] * filter_matrix[1, 2]) + \
        (data[2:, :-2] * filter_matrix[2, 0]) + \
        (data[2:, 1:-1] * filter_matrix[2, 1]) + \
        (data[2:, 2:] * filter_matrix[2, 2])

    # normalization step
    # filtering scrambles the value of cells depending on what filter is used meaning we don't get data that we can easily read
    # this ensures that the target's intensity is somewhat similar before and after filtering
    norm_coef = 1
    if normalize:
        # find maximum pixel intensity of original data
        original_max = np.amax(data)
        # find the maximum pixel intensity of filtered data
        max = np.amax(filtered)
        # find a coeficient that will restore the intensity of the data
        norm_coef = original_max / max

    output = radar_data
    # every element is multiplied by the normalized coeficient
    filtered = filtered * norm_coef

    # apply threashold to set values to 0 for all items below threshold
    filtered[filtered <= filter_threshold] = 0

    output["data"] = filtered
    output["time"] = time
    
    output["filters_applied"] += 1

    return output

def apply_5x5_filter(radar_data: dict, filter_name: str, filter_threshold=25, normalize=True) -> dict:
    """Applies a filter that uses a 5x5 kernel to radar data

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
            filter_name - options available: edge_filter_1, edge_filter_2, gausian, identity
            filter_threshold - sets data to 0 for all values below it, applied after filter and normalization.
            normalize - true/false specifies if normalization should be applied to compensate filter adjustments
        Returns:
            filtered radar_data
    """
    data = radar_data["data"]
    time = np.array(radar_data["time"])

    # creates a 2D array of zeros that is the same size as the data array
    filtered = np.zeros(data.shape)

    filter_matrix = get_5x5_kernel(filter_name)

    # this uses numpy vectorization to calculate sum of 5x5
    # match cell and multiply with corresponding filter value (from kernels)
    # sliding 5x5 window is element-wise multiplied by filter matrix and all end results are summed up and stored in the center element of the sliding window
    # goes through original data, writes into an empty copy of the 2D array
    filtered[2:-2, 2:-2] = \
        (data[:-4, :-4] * filter_matrix[0, 0]) + \
        (data[:-4, 1:-3] * filter_matrix[0, 1]) + \
        (data[:-4, 2:-2] * filter_matrix[0, 2]) + \
        (data[:-4, 3:-1] * filter_matrix[0, 3]) + \
        (data[:-4, 4:] * filter_matrix[0, 4]) + \
        \
        (data[1:-3, :-4] * filter_matrix[1, 0]) + \
        (data[1:-3, 1:-3] * filter_matrix[1, 1]) + \
        (data[1:-3, 2:-2] * filter_matrix[1, 2]) + \
        (data[1:-3, 3:-1] * filter_matrix[1, 3]) + \
        (data[1:-3, 4:] * filter_matrix[1, 4]) + \
        \
        (data[2:-2, :-4] * filter_matrix[2, 0]) + \
        (data[2:-2, 1:-3] * filter_matrix[2, 1]) + \
        (data[2:-2, 2:-2] * filter_matrix[2, 2]) + \
        (data[2:-2, 3:-1] * filter_matrix[2, 3]) + \
        (data[2:-2, 4:] * filter_matrix[2, 4]) + \
        \
        (data[3:-1, :-4] * filter_matrix[3, 0]) + \
        (data[3:-1, 1:-3] * filter_matrix[3, 1]) + \
        (data[3:-1, 2:-2] * filter_matrix[3, 2]) + \
        (data[3:-1, 3:-1] * filter_matrix[3, 3]) + \
        (data[3:-1, 4:] * filter_matrix[3, 4]) + \
        \
        (data[4:, :-4] * filter_matrix[4, 0]) + \
        (data[4:, 1:-3] * filter_matrix[4, 1]) + \
        (data[4:, 2:-2] * filter_matrix[4, 2]) + \
        (data[4:, 3:-1] * filter_matrix[4, 3]) + \
        (data[4:, 4:] * filter_matrix[4, 4]) 
    
    # normalization step
    # filtering scrambles the value of cells depending on what filter is used meaning we don't get data that we can easily read
    # this ensures that the target's intensity is somewhat similar before and after filtering
    norm_coef = 1
    if normalize:
        # find maximum pixel intensity of original data
        original_max = np.amax(data)
        # find the maximum pixel intensity of filtered data
        max = np.amax(filtered)
        # find a coeficient that will restore the intensity of the data
        norm_coef = original_max / max

    output = radar_data
    # every element is multiplied by the normalized coeficient
    filtered = filtered * norm_coef

    # apply threashold to set values to 0 for all items below threshold
    filtered[filtered <= filter_threshold] = 0

    #we need to reduce dimentions only on the last filter
    #output["data"] = filtered[2:-2, 2:-2]
    #output["time"] = time[2:-2]
    output["data"] = filtered
    output["time"] = time

    output["filters_applied"] += 1  

    return output

def apply_5x5_avg_filter(radar_data: dict, filter_threshold=25, normalize=True) -> dict:
    """Applies an aaverage filter that uses a 5x5 kernel

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
            filter_threshold - sets data to 0 for all values below it, applied after filter and normalization.
            normalize - true/false specifies if normalization should be applied to compensate filter adjustments
        Returns:
            filtered radar_data
    """
    data = radar_data["data"]
    time = np.array(radar_data["time"])

    
    # creates a 2D array of zeros that is the same size as the data array
    filtered = np.zeros(data.shape)

    # creates a 2D array of ones just to keep a multiplier matrix in formula
    filter_matrix = np.ones((5,5))

    # this uses numpy vectorization to calculate sum of 5x5
    # match cell and multiply with corresponding filter value (from kernels)
    # sliding 5x5 window is element-wise multiplied by filter matrix and all end results are summed up and stored in the center element of the sliding window
    # goes through original data, writes into an empty copy of the 2D array
    filtered[2:-2, 2:-2] = (\
        (data[:-4, :-4] * filter_matrix[0, 0]) + \
        (data[:-4, 1:-3] * filter_matrix[0, 1]) + \
        (data[:-4, 2:-2] * filter_matrix[0, 2]) + \
        (data[:-4, 3:-1] * filter_matrix[0, 3]) + \
        (data[:-4, 4:] * filter_matrix[0, 4]) + \
        \
        (data[1:-3, :-4] * filter_matrix[1, 0]) + \
        (data[1:-3, 1:-3] * filter_matrix[1, 1]) + \
        (data[1:-3, 2:-2] * filter_matrix[1, 2]) + \
        (data[1:-3, 3:-1] * filter_matrix[1, 3]) + \
        (data[1:-3, 4:] * filter_matrix[1, 4]) + \
        \
        (data[2:-2, :-4] * filter_matrix[2, 0]) + \
        (data[2:-2, 1:-3] * filter_matrix[2, 1]) + \
        (data[2:-2, 2:-2] * filter_matrix[2, 2]) + \
        (data[2:-2, 3:-1] * filter_matrix[2, 3]) + \
        (data[2:-2, 4:] * filter_matrix[2, 4]) + \
        \
        (data[3:-1, :-4] * filter_matrix[3, 0]) + \
        (data[3:-1, 1:-3] * filter_matrix[3, 1]) + \
        (data[3:-1, 2:-2] * filter_matrix[3, 2]) + \
        (data[3:-1, 3:-1] * filter_matrix[3, 3]) + \
        (data[3:-1, 4:] * filter_matrix[3, 4]) + \
        \
        (data[4:, :-4] * filter_matrix[4, 0]) + \
        (data[4:, 1:-3] * filter_matrix[4, 1]) + \
        (data[4:, 2:-2] * filter_matrix[4, 2]) + \
        (data[4:, 3:-1] * filter_matrix[4, 3]) + \
        (data[4:, 4:] * filter_matrix[4, 4])) / 25.0
    
    # normalization step
    # filtering scrambles the value of cells depending on what filter is used meaning we don't get data that we can easily read
    # this ensures that the target's intensity is somewhat similar before and after filtering
    norm_coef = 1
    if normalize:
        # find maximum pixel intensity of original data
        original_max = np.amax(data)
        # find the maximum pixel intensity of filtered data
        max = np.amax(filtered)
        # find a coeficient that will restore the intensity of the data
        norm_coef = original_max / max

    output = radar_data
    # every element is multiplied by the normalized coeficient
    filtered = filtered * norm_coef

    # apply threashold to set values to 0 for all items below threshold
    filtered[filtered <= filter_threshold] = 0

    output["data"] = filtered
    output["time"] = time
    
    output["filters_applied"] += 1  

    return output


def apply_log(radar_data: dict) -> dict:
    """ Applies log to radar data
        Args:
            radar_data - dictionary with keys:
                data (numpy array), time (list), start (float), end (float);

        Returns:
            radar_data with log applied
    """
    #radar_data["data"] =  20 * ma.log10(radar_data['data'])
    
    data = radar_data["data"]

    #fill nan values with 0s
    np.nan_to_num(data, copy=False, nan=0.0)

    # set minimum value to 1e-8 so that log funcion doesn't break
    data[data < 1e-8] = 1e-8
    
    #calculate log without any weights
    #data = np.log10(data)
    data = np.log2(data)

    data[data < 0] = 0

    #normalize data to range 0-1
    max_value = max([1.0, np.max(data)]) #we don't normalize if max value is < 1
    data = data / max_value

    #transform range [0..1] into [0..100]
    data = data * 100

     # set minimum value to 1e-8 as log funcion may create negative values again
    data[data < 1e-8] = 1e-8

    #radar_data["data"] = 20 * np.log10(np.array(radar_data["data"]))

    radar_data["data"] = data
    radar_data["filters_applied"] += 1  

    return radar_data


def denoise_filter(radar_data: dict, value_threshold=0, count_threshold=1) -> dict:
    """Eliminate random pixels. value_threshold is applied before aplying this filter
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            filter_name - options available: edge_filter_1, edge_filter_2
        Returns:
            denoised radar_data
    """
    data = radar_data["data"]

    # apply threashold to set values to 0 for all cells in 2D array below threshold
    data[data <= value_threshold] = 0

    # create a 3x3 matrix that goes over the entire array looking for
    # make a copy of original 2D array and translate it to 0's and 1's
    mask = np.copy(data)

    # sets all values greater than 0 to 1
    mask[mask > 0] = 1
    mask_counts = np.ones(data.shape)

    # The code below counts the num of pixels that have intensity
    # It determines this num because all values are set to 1 or 0 so if a pixels has any intensity, it will be set to 1
    # which can then be added up, and will tell how many pixels are in the 3x3 matrix
    mask_counts[1:-1, 1:-1] = (mask[:-2, :-2]) + \
        (mask[:-2, 1:-1]) + \
        (mask[:-2, 2:]) + \
        (mask[1:-1, :-2]) + \
        (mask[1:-1, 1:-1]) + \
        (mask[1:-1, 2:]) + \
        (mask[2:, :-2]) + \
        (mask[2:, 1:-1]) + \
        (mask[2:, 2:])

    # tells which pixels need extinguished
    mask_counts[mask_counts <= count_threshold] = 0

    # indicates which pixels can stay lit
    mask_counts[mask_counts > count_threshold] = 1

    filtered = data * mask_counts

    output = radar_data.copy()
    output["data"] = filtered
    output["filters_applied"] += 1  

    return output

def denoise_with_5x5_filter(radar_data: dict, value_threshold=0, count_threshold=1) -> dict:
    """Eliminate random  pixels using vewctorization 5x5 moving window. value_threshold is applied before aplying this filter
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            filter_name - options available: edge_filter_1, edge_filter_2
        Returns:
            denoised radar_data
    """
    data = radar_data["data"]

    # apply threashold to set values to 0 for all cells in 2D array below threshold
    data[data <= value_threshold] = 0

    # create a 3x3 matrix that goes over the entire array looking for
    # make a copy of original 2D array and translate it to 0's and 1's
    mask = np.copy(data)

    # sets all values greater than 0 to 1
    mask[mask > 0] = 1
    mask_counts = np.ones(data.shape)

    filter_matrix = np.ones((5,5))
    #filter_matrix[:,0] = 0
    #filter_matrix[:,-1] = 0

    # The code below counts the num of pixels that have intensity
    # It determines this num because all values are set to 1 or 0 so if a pixels has any intensity, it will be set to 1
    # which can then be added up, and will tell how many pixels are in the 3x3 matrix
    mask_counts[2:-2, 2:-2] = \
        (mask[:-4, :-4] * filter_matrix[0, 0]) + \
        (mask[:-4, 1:-3] * filter_matrix[0, 1]) + \
        (mask[:-4, 2:-2] * filter_matrix[0, 2]) + \
        (mask[:-4, 3:-1] * filter_matrix[0, 3]) + \
        (mask[:-4, 4:] * filter_matrix[0, 4]) + \
        \
        (mask[1:-3, :-4] * filter_matrix[1, 0]) + \
        (mask[1:-3, 1:-3] * filter_matrix[1, 1]) + \
        (mask[1:-3, 2:-2] * filter_matrix[1, 2]) + \
        (mask[1:-3, 3:-1] * filter_matrix[1, 3]) + \
        (mask[1:-3, 4:] * filter_matrix[1, 4]) + \
        \
        (mask[2:-2, :-4] * filter_matrix[2, 0]) + \
        (mask[2:-2, 1:-3] * filter_matrix[2, 1]) + \
        (mask[2:-2, 2:-2] * filter_matrix[2, 2]) + \
        (mask[2:-2, 3:-1] * filter_matrix[2, 3]) + \
        (mask[2:-2, 4:] * filter_matrix[2, 4]) + \
        \
        (mask[3:-1, :-4] * filter_matrix[3, 0]) + \
        (mask[3:-1, 1:-3] * filter_matrix[3, 1]) + \
        (mask[3:-1, 2:-2] * filter_matrix[3, 2]) + \
        (mask[3:-1, 3:-1] * filter_matrix[3, 3]) + \
        (mask[3:-1, 4:] * filter_matrix[3, 4]) + \
        \
        (mask[4:, :-4] * filter_matrix[4, 0]) + \
        (mask[4:, 1:-3] * filter_matrix[4, 1]) + \
        (mask[4:, 2:-2] * filter_matrix[4, 2]) + \
        (mask[4:, 3:-1] * filter_matrix[4, 3]) + \
        (mask[4:, 4:] * filter_matrix[4, 4])

     # tells which pixels need extinguished
    mask_counts[mask_counts <= count_threshold] = 0

    # indicates which pixels can stay lit
    mask_counts[mask_counts > count_threshold] = 1

    filtered = data * mask_counts

    output = radar_data.copy()
    output["data"] = filtered
    output["filters_applied"] += 1  

    return output

def count_pixel_stats(radar_data: dict, first_bucket_threshold: float, bucket_size: int) -> dict:
    """Method counts values in a 2D array bucketed by the provided size, starting with the provided first_bucket_threshold value

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            first_bucket_threshold - the value of the first bucket
            bucket_size - the size of the bucket
        Returns:
            a dictionary where key is a number, representing upper bucket limit and a value containing no of items in that bucket  
    """
    data = radar_data["data"]
    data_copy = np.copy(data)

    # remove inactive range values (can change)
    data_copy[:, range(200)] = 0

    # setting value for 1st bucket
    data_copy[data_copy <= first_bucket_threshold] = first_bucket_threshold

    data_copy = np.nan_to_num(data_copy)

    max_value = np.amax(data_copy)

    # creates value ranges(buckets) and sets all values within that bucket to the upper limit of its bucket
    for i in range(1, (((max_value - first_bucket_threshold) / bucket_size) + 2).astype(int)):
        lower_limit = first_bucket_threshold + (i - 1) * bucket_size
        upper_limit = first_bucket_threshold + i * bucket_size
        data_copy = np.where((data_copy > lower_limit) & (
            data_copy <= upper_limit), upper_limit, data_copy)

    # counts the number of unique values in the numpy array
    unique, counts = np.unique(data_copy, return_counts=True)
    return dict(zip(unique, counts))


# runs denoise_filter function until a pixel removal threshold is reached
# removing more pixels would result in disrupted target signal
def iterative_denoise(data: dict, value_threshold:float, count_threshold: int) -> dict:
    """Method runs denoise algorith multiple times until no more adjustments are detected
        Args: 
            data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            value_threshold: sets all values below it to 0, 
            count_threshold: used as a threshold to indicate whether to reset a center pixel to 0 or not when iterating through data
        Returns:
             denoised_data - dictionary  
    """
    stats = count_pixel_stats(
        data, first_bucket_threshold=value_threshold, bucket_size=10)

    zero_bucket_before = stats[value_threshold]
    denoised_data = data
    while True:
        denoised_data = denoise_filter(
            radar_data=denoised_data, value_threshold=value_threshold, count_threshold=count_threshold)
        stats_after = count_pixel_stats(
            denoised_data, first_bucket_threshold=value_threshold, bucket_size=5)
        zero_bucket_after = stats_after[value_threshold]
        delta = zero_bucket_after - zero_bucket_before
        zero_bucket_before = zero_bucket_after
        if delta <= 0:
            break

    return denoised_data

# runs denoise_filter function until a pixel removal threshold is reached
# removing more pixels would result in disrupted target signal
def iterative_5x5_denoise(data: dict, value_threshold:float, count_threshold: int) -> dict:
    """Method runs denoise algorith multiple times until no more adjustments are detected
        Args: 
            data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            value_threshold: sets all values below it to 0, 
            count_threshold: used as a threshold to indicate whether to reset a center pixel to 0 or not when iterating through data
        Returns:
             denoised_data - dictionary  
    """
    stats = count_pixel_stats(
        data, first_bucket_threshold=value_threshold, bucket_size=10)

    zero_bucket_before = stats[value_threshold]
    denoised_data = data
    while True:
        denoised_data = denoise_with_5x5_filter(
            radar_data=denoised_data, value_threshold=value_threshold, count_threshold=count_threshold)
        stats_after = count_pixel_stats(
            denoised_data, first_bucket_threshold=value_threshold, bucket_size=5)
        zero_bucket_after = stats_after[value_threshold]
        delta = zero_bucket_after - zero_bucket_before
        zero_bucket_before = zero_bucket_after
        if delta <= 0:
            break

    return denoised_data

def bucketize_radar_data(radar_data: dict, first_bucket_threshold, bucket_size):
    """Method adjusts data by assigning it to appropriate buckets. Buckets are created based on the provided size, 
       starting with the provided first_bucket_threshold value

        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
            first_bucket_threshold, 
            bucket_size
        Returns:
             radar_data - dictionary  
    """
    data = radar_data["data"]
    data_copy = np.copy(data)

    # setting value for 1st bucket
    data_copy[data_copy <= first_bucket_threshold] = first_bucket_threshold

    max_value = np.amax(data_copy)

    # creates value ranges(buckets) and sets all values within that bucket to the upper limit of its bucket
    for i in range(1, int(round((max_value - first_bucket_threshold) / bucket_size) + 2)):
        lower_limit = first_bucket_threshold + (i - 1) * bucket_size
        upper_limit = first_bucket_threshold + i * bucket_size
        data_copy = np.where((data_copy > lower_limit) & (
            data_copy <= upper_limit), upper_limit, data_copy)

    # apply threashold to set values to 0 for all cells in 2D array below threshold
    data_copy[data_copy <= (max_value - 2 * bucket_size)] = 1

    return {
        "data": data_copy,
        "time": radar_data["time"],
        "start": radar_data["start"],
        "end":  radar_data["end"]
    }

def remove_streaks(radar_data: dict) -> dict:
    """Method adjusts radar data by removing streaks, 
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
        Returns:
             radar_data - dictionary  
    """
    data = radar_data["data"]
    
    row,col = data.shape
    
    row_threshold = row * 0.55
    pixels_on = data.copy()
    pixels_on[pixels_on > 0] = 1
    row_counts = np.sum(pixels_on, axis=0)
    
    mask = np.ones(col)
    mask[row_counts >= row_threshold] = 0
    
    radar_data["data"] = data * mask
    radar_data["filters_applied"] += 2  

    return radar_data

def apply_scipy_gausian_filter(radar_data: dict, start_buffer: int = 50, streak_width: int = 200, strength: float = 8, boost_thresh: float = 2) -> dict:
    """ Applies a standard gausian filter from scipy to the radar data

    Args:
        radar_data (dict): The radar data
        start_buffer (int, optional): The number of rows to use for the noise floor. Defaults to 50.
        streak_width (int, optional): The number of columns to use for the noise floor. Defaults to 200.
        strength (int, optional): The strength of the boost. Defaults to 8. Higher is stronger.
        boost_thresh (int, optional): The threshold for the streak boost. Defaults to 2.

    Returns:
        dict: The filtered radar data
    """

    data = radar_data["data"]

    #apply a log2
    #data = np.log2(data)
    
    #compute some values
    del_thresh = strength + 3
    max_val = np.max(data)

    #gaussian filter
    data = sp.ndimage.gaussian_filter(data, sigma=1, radius=2)

    # create a mask to get rid of early streaks
    noise_floor = np.average(data[:start_buffer], axis=0)
    noise_floor[streak_width:] = 0
    data = data - noise_floor

    #we might have some signal in the first 200 columns
    #so boost anything above boost_thresh
    boost_val = max(max_val - 2, del_thresh + 1)
    data[:, :streak_width][data[:, :streak_width] > boost_thresh] = boost_val

    #set everything under del_thresh to 0
    data[data < del_thresh] = 0

    #return the filtered data
    radar_data["data"] = data
    radar_data["filters_applied"] += 2  

    return radar_data
