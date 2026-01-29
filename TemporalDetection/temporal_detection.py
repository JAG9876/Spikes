import numpy as np
import scipy.signal as sps
from enum import Enum

class Algorithm(Enum):
    DEFAULT = 0
    ARGMAX = 1
    CORRELATION = 2
    SCI_PI_CORRELATION = 3

# Returns the generic time difference in seconds between two waveforms

def get_offset(wave1: tuple[int, np.ndarray], wave2: tuple[int, np.ndarray], algorithm: Algorithm):
    data1 = wave1[1]
    data2 = wave2[1]

    match algorithm:
        case Algorithm.ARGMAX:
            return algorithm_argmax(wave1[0], data1, wave2[0], data2)
        case Algorithm.CORRELATION:
            return algorithm_numpy_correlate(wave1[0], data1, wave2[0], data2)
        case Algorithm.SCI_PI_CORRELATION:
            return algorithm_scipy_correlate(wave1[0], data1, wave2[0], data2)
        case _:
            return None

# Finds max value of both waves and calculates the time difference
def algorithm_argmax(sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
    max1InSeconds = data1.argmax() / sample_freq1
    max2InSeconds = data2.argmax() / sample_freq2

    return max1InSeconds - max2InSeconds

def algorithm_numpy_correlate(sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
    correlation = np.correlate(data1.astype(np.int64), data2.astype(np.int64), "full")
    max_index = correlation.argmax()

    return (max_index - data2.shape[0]) / sample_freq2

def algorithm_scipy_correlate(sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
    correlation = sps.correlate(data1.astype(np.int64), data2.astype(np.int64), 'full')
    max_index = correlation.argmax()

    return (max_index - data2.shape[0]) / sample_freq2

# Other:
# - vectorized approach
# 
# average zero crossing frequency
    #sign_changes1 = np.diff(np.sign(data1))
    #zcf1 = np.count_nonzero(sign_changes1) / data1.shape[0]
