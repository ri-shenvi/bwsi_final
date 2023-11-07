import numpy as np
import lib.filter_utils as filters

def get_radar_start_time(radar_data: dict, correlation_threshold: float, reduce_dimentions_by = 3):
    """Analyses radar data to capture the time of the first movement
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
        Returns:
            the time at which motion is detected for the first time
    """

    #we need to reduce dimentions only on the last filter
    rd = reduce_dimentions_by
    radar_data["data"] = radar_data["data"][rd:(-1*rd), rd:(-1*rd)]
    radar_data["time"] = radar_data["time"][rd:(-1*rd)]

    #need to apply filters for better estimates

    # 50, 10 worked well
    bucketized_data = filters.bucketize_radar_data(radar_data, first_bucket_threshold=50, bucket_size=15)
 
    corr = get_correlations(bucketized_data)
    
    corr = corr[1:]
    radar_data["data"] = (radar_data["data"])[1:,:]
    radar_data["time"] = (radar_data["time"])[1:]

    # apply moving window filter
    moving_window_size = 20
    corr = running_mean(np.array(corr), moving_window_size)

    #calc the avg of first 30 corr values
    initial_threshold = np.sum(corr[:30]) / 30
    #sets a threshold for 20% below the avg of the first 10 corr values
    movement_threshold = initial_threshold * correlation_threshold

    #corr = np.nan_to_num(corr).tolist()
    corr = np.nan_to_num(corr)

    # finds the first instance of a correlation below 
    idx=1
    #idx = next((x[0] for x in enumerate(corr) if x[1] < movement_threshold))

    skip_at_start = True
    for i in range(len(corr)):
        if skip_at_start and corr[i] < movement_threshold:
            continue
        if skip_at_start and corr[i] >= movement_threshold:
            skip_at_start = False
        
        if corr[i] < movement_threshold:
            idx = i
            break

    # uncomment those 2 lines after movement time detection analysis and verification is completed
    #radar_data["data"] = radar_data["data"][idx:-1]
    #radar_data["time"] = radar_data["time"][idx:-1]

    radar_data["corr_coefs"] = corr

    move_time = np.ones(radar_data["time"].shape)
    move_time[:idx-1] = 0

    radar_data["move_time"] = move_time

    return radar_data


def get_correlations(radar_data: dict):
    """Calculates correlation coeficients between every two consecutive rows 
        Args: 
            radar_data - dictionary with keys: 
                data (numpy array), time (list), start (float), end (float); 
                where data is a numpy 2D array.
        Returns:
            an 1D array containing max correlation value per each row 
    """
    data = radar_data["data"]

    max_corr_vals = []
    for i in range(1, len(data)):
        # calculates similarity shifting to the left
        calc_similarity_L = statistical_correlation(data[i-1], data[i])
        # calculates similarity shifting to the right
        calc_similarity_R = statistical_correlation(data[i], data[i-1])
        # picking the max value from the above correlation coefs.
        # max_corr_val_array.append(max(max(calc_similarity_R),max(calc_similarity_L)))

        max_corr = max(max(calc_similarity_R), max(calc_similarity_L))
        max_corr_vals.append(max_corr)
    max_corr_vals.append(max_corr_vals[-1])
    return np.array(max_corr_vals)


def statistical_correlation(x: np.ndarray, y: np.ndarray, n=8):
    """Calculates statistical correlation between given two arrays, shifting a second array left by n elements
    https://stackoverflow.com/questions/643699/how-can-i-use-numpy-correlate-to-do-autocorrelation
    Args: 
            x,y - 1D arrays to compare, have to be of same length
        Returns:
            correlation results in 1D array, where values are in [0,1], 1 meaning arrays are identical.
    """
    return np.array([np.corrcoef(x, y)[0, 1]]+[np.corrcoef(x[:-i], y[i:])[0, 1] \
                                               for i in range(1, n)])


def running_mean(x: np.array, window_size: int) -> np.ndarray:
    """Calculates statistical correlation between given two arrays, shifting a second array left by n elements
    Args: 
            x - 1D arrays to apply moving avg
            N - running avg window size
        Returns:
            1D np array with averaged data.
    """
       
    kernel_size = window_size
    kernel = np.ones(kernel_size) / kernel_size
    result =  np.convolve(x, kernel, mode='valid')

    #need to ensure we return an array of same length
    x_shape = x.shape[0]
    r_shape = result.shape[0]
    #compensate for any lost values due to moving window avg
    result = np.append(result, np.zeros(x_shape - r_shape))

    return result
