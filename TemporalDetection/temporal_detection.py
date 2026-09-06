import numpy as np
import scipy.signal as sps
import sounddevice as sd
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from scipy import fft

class Algorithm(Enum):
    DEFAULT = 0
    ARGMAX = 1
    CORRELATION = 2
    SCI_PI_CORRELATION = 3
    AMP_CORRELATION = 4
    AMP_DIFF = 5
    GCCPHAT = 6
    FFT = 7

# Runs a band-reject filter on data and returns a new np.ndarray result
def band_reject(sample_freq: int, data: np.ndarray, reject_freq, bandwidth_hz):
    if sample_freq <= 0:
        raise ValueError("sample_freq must be > 0")
    if reject_freq <= 0:
        raise ValueError("reject_freq must be > 0")
    if bandwidth_hz <= 0:
        raise ValueError("bandwidth_hz must be > 0")

    nyquist = sample_freq / 2
    if reject_freq >= nyquist:
        raise ValueError("reject_freq must be below Nyquist frequency")

    q_factor = reject_freq / bandwidth_hz
    if q_factor <= 0:
        raise ValueError("Derived Q factor must be > 0")

    b, a = sps.iirnotch(reject_freq, q_factor, fs=sample_freq)

    signal = np.asarray(data, dtype=np.float64)
    if signal.size == 0:
        return signal

    min_len_for_filtfilt = 3 * max(len(a), len(b))
    if signal.shape[0] <= min_len_for_filtfilt:
        return sps.lfilter(b, a, signal, axis=0)

    return sps.filtfilt(b, a, signal, axis=0)


class TemporalDetection():
    def __init__(self, pl_wave, pl_start, pl_end, pl_actual_offs, pl_expected_offset, pl_count):
        self.pl_wave = pl_wave
        self.pl_start = pl_start
        self.pl_end = pl_end
        self.pl_actual_offs = pl_actual_offs
        self.pl_exp_offs = pl_expected_offset
        self.pl_count = pl_count
        self.sample_rate = None

    # Returns the generic time difference in seconds between two waveforms

    def get_offset(self, wave1: tuple[int, np.ndarray], wave2: tuple[int, np.ndarray], algorithm: Algorithm):
        data1 = wave1[1]
        data2 = wave2[1]
        sample_rate1 = wave1[0]
        sample_rate2 = wave2[0]

        params = (sample_rate1, data1, sample_rate2, data2)

        match algorithm:
            case Algorithm.ARGMAX:
                return algorithm_argmax(*params)
            case Algorithm.CORRELATION:
                return self.algorithm_numpy_correlate(*params)
            case Algorithm.SCI_PI_CORRELATION:
                return self.algorithm_scipy_correlate(*params)
            case Algorithm.AMP_CORRELATION:
                return algorithm_amp_correlate(*params)
            case Algorithm.AMP_DIFF:
                return algorithm_amp_diff(*params)
            case Algorithm.GCCPHAT:
                return self.algorithm_gccphat(*params)
            case Algorithm.FFT:
                return self.algorithm_fft(*params)
            case _:
                return None

    def on_button1_click(self, event):
        segment = self.pl_wave[self.pl_start:self.pl_end]
        sd.play(segment, self.sample_rate)
    
    def plot_it(self, data1, corr, picked_index, *extra_arguments):
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8,9), sharex=True, gridspec_kw={'height_ratios': [1,1,8]})
        plt.subplots_adjust(bottom=0.2)

        ax1.axvspan(self.pl_start, self.pl_end, color='tab:orange', alpha=0.25, zorder=0)
        ax1.set_ylim(-10000, 10000)
        ax1.plot(self.pl_wave, zorder=1) # self.pl_start self.pl_end

        start = self.pl_start + self.pl_actual_offs
        end = self.pl_end + self.pl_actual_offs
        ax2.axvspan(start, end, color='tab:orange', alpha=0.25, zorder=0)
        ax2.plot(data1)
        #ax2.plot(np.asarray(data1, dtype=np.float64) * 2.0)

        # Zoom in y-axis-wise (double)
        ymin, ymax = ax2.get_ylim()
        center = (ymin + ymax) / 2
        half = (ymax - ymin) / 4
        #ax2.set_ylim(center - half, center + half)
        ax2.set_ylim(-10000, 10000)

        ax3.plot(corr)
        if picked_index is not None and 0 <= picked_index < len(corr):
            ax3.plot(picked_index, corr[picked_index], marker='o', color='red', markersize=7, zorder=3)

        xmax = len(corr) - 1
        ax3.set_xlim(0,xmax)

        ax_button1 = plt.axes([0.2, 0.05, 0.1, 0.05])
        btn1 = Button(ax_button1, 'Play audio 1')
        btn1.on_clicked(self.on_button1_click)

        ax_button2 = plt.axes([0.4, 0.05, 0.1, 0.05])
        btn2 = Button(ax_button2, 'Play audio 2')
        def on_button2_click(event):
            segment = data1[start:end]
            sd.play(segment, self.sample_rate)
        btn2.on_clicked(on_button2_click)

        should_i_draw = len(extra_arguments) > 0
        if should_i_draw:
            # 2nd order "butterworth" lowpass filter at 500hz applied to correlation signal (corr)
            #sos = sps.butter(N=2, Wn=500, btype="low", fs=48000, output="sos")
            #my_signal = sps.sosfiltfilt(sos=sos, x=corr)

            #my_signal = np.multiply(np.diff(corr, n=1), 2.5)

            # RMS rolling average of corr
            avg_window_size = 48000
            rollinrollinrollin = np.square(corr / 1e10)
            avg_window = np.ones(avg_window_size) / avg_window_size
            moving_average = np.convolve(rollinrollinrollin, avg_window, mode="valid")
            moving_average = np.sqrt(moving_average)

            decimation_scale = 40
            #decimated = sps.decimate(corr, decimation_scale) # 40x decimation (scales down samplerate by 40x)
            decimated = sps.decimate(moving_average, decimation_scale) # 40x decimation (scales down samplerate by 40x)
            my_signal = np.zeros(len(corr) // decimation_scale)

            #window_size = (end - start) // decimation_scale
            window_size = 1500 # stupid
            for j in range(window_size // 2, len(my_signal) - window_size // 2):
                i = j - window_size // 2

                window = sps.windows.hamming(window_size // 2)
                left_side           = window * decimated[i:i + window_size // 2]
                right_side_reversed = window * decimated[i + window_size // 2:i + window_size][::-1]

                #sum = np.sum(np.abs(left_side - right_side_reversed))
                #symmetricness = 1e+20 / max(0.00000001, sum)
                rms_error = np.sqrt(np.mean((left_side - right_side_reversed) ** 2))
                symmetricness = 1e+18 / max(0.0000001, rms_error)
                my_signal[j] = symmetricness

            #my_signal = np.repeat(my_signal, decimation_scale) # scale back up to normal samplerate
            my_signal = np.repeat(decimated, decimation_scale) * 1e10
            #shortest = min(len(my_signal), len(corr))
            #my_signal[:shortest] *= corr[:shortest]
            #my_signal /= 10
            
            plt.plot(my_signal)

        plt.title(f"{self.pl_count}  {self.pl_exp_offs:.3f}")
        plt.tight_layout()
        plt.show()

    def algorithm_numpy_correlate(self, sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
        self.sample_rate = sample_freq2
        correlation = np.correlate(data1.astype(np.int64), data2.astype(np.int64), "full")
        max_index = correlation.argmax()
        self.plot_it(data1, correlation, max_index)

        return (max_index - data2.shape[0]) / sample_freq2

    def algorithm_scipy_correlate(self, sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
        self.sample_rate = sample_freq2
        correlation = sps.correlate(data1.astype(np.int64), data2.astype(np.int64), 'full')
        #correlation = sps.correlate(data1.astype(np.int64), data2.astype(np.int64), 'full', 'direct')
        #correlation = sps.correlate(data1.astype(np.int64), data2.astype(np.int64), 'same', 'direct')
        #correlation = sps.correlate(data1.astype(np.int64), data2.astype(np.int64), 'valid', 'direct')

        '''
        Pick the n highest peaks (highest positives and lowest negatives)
        For each peak:
            peakValue = the peak value
            rms_range = pick the range x milliseconds before and after the peak
            rms_value = rms_range.sum(x => x*x)
            peak_score = peakValue / rms_value
        '''
        peak_indices = self.get_peak_indices(correlation, 10_000, 5)
        max_index = peak_indices[0]

        #max_index = self.get_best_peak_index(peak_indices, correlation)

        #self.plot_it(data1, correlation, max_index, "PLEASE ENABLE LOWPASS FILTER PLOT")
        self.plot_it(data1, correlation, max_index)

        '''
        # For each of the 5 highest peaks, pick +-30.000 samples on each side and correlate against its own reverse.
        best_score_value = 0
        center_index = 30_000
        for i in range(5):
            index_mid = peak_indices[i]
            index_start = index_mid - center_index
            index_end = index_mid + center_index

            #window = sps.windows.hamming(2*center_index)

            # Find symmetry
            #corr = window * correlation[index_start:index_end]
            corr = correlation[index_start:index_end] / 1e9
            corr_reversed = corr[::-1]
            symmetry_correlation = np.abs(sps.correlate(corr, corr_reversed, mode='full', method='fft'))
            #symmetry_correlation = sps.correlate(corr, corr_reversed, mode='full', method='fft')
            #amplitude, _ = sps.envelope(symmetry_correlation, n_out=100)
            sos = sps.butter(N=2, Wn=10, btype="lowpass", fs=120_000, output="sos")
            amplitude = sps.sosfiltfilt(sos, symmetry_correlation, padtype=None)

            # Normalize the amplitude values to maximum 1, minimum 0 and find with a number how similar it is to a standard distribution curve that is centered in the middle of the array
            amplitude_min = amplitude.min()
            amplitude_max = amplitude.max()
            normalized_amplitude = (amplitude - amplitude_min) / (amplitude_max - amplitude_min)

            x = np.arange(len(normalized_amplitude))
            mean = (len(normalized_amplitude) - 1) / 2
            sigma = np.sqrt(np.sum(normalized_amplitude * (x - mean) ** 2) / np.sum(normalized_amplitude))
            #sigma *= 0.5 # Makes the gaussion curve more narrow
            gaussian = np.exp(-0.5 * ((x - mean) / sigma) ** 2)

            gaussian_similarity = 1 - np.mean(np.abs(normalized_amplitude - gaussian))
            if gaussian_similarity > best_score_value:
                best_score_value = gaussian_similarity
                max_index = index_mid

            # compare the two aggregated values - the more equal, the more symmetry
            self.plot_it(data1, symmetry_correlation, max_index)
            remember = self.pl_exp_offs
            self.pl_exp_offs = gaussian_similarity
            #self.plot_it(data1, amplitude, max_index)
            self.plot_it(data1, normalized_amplitude, max_index)
            self.plot_it(data1, gaussian, max_index)
            self.pl_exp_offs = remember
        '''

        # max_index = correlation.argmax()

        return (max_index - data2.shape[0]) / sample_freq2

    def get_best_peak_index(self, peak_indices, correlation):
        best_score = 0
        best_peak_index = -1

        for peak_index in peak_indices:
            peak_value = correlation[peak_index]

            rms_range = 10_000
            start_index = max(0, peak_index - rms_range)
            end_index = min(len(correlation)-1, peak_index + rms_range)
            rms = np.sqrt(np.mean(np.square(correlation[start_index:end_index])))

            score = peak_value / rms

            if score > best_score:
                best_score = score
                best_peak_index = peak_index

        return best_peak_index

    '''
    Returns list of indices (up to max_peaks_returned items)
    '''
    def get_peak_indices(self, correlation: np.ndarray, distance_between_peaks, max_peaks_returned):
        peak_indices, props = sps.find_peaks(correlation, distance=distance_between_peaks, height=-np.inf)
        sort_indices = np.argsort(props["peak_heights"])[::-1]
        sorted_peak_indices = peak_indices[sort_indices]

        num_peaks = min(len(sorted_peak_indices), max_peaks_returned)
        return sorted_peak_indices[:num_peaks]


    # Finds the offset between data1 and data2 based on the gccphat algorithm
    def algorithm_gccphat(self, sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
        self.sample_rate = sample_freq2
        if data1.size == 0 or data2.size == 0:
            return 0

        # Convert potential multi-channel input to mono and normalize dtype.
        ref = np.asarray(data1, dtype=np.float64)
        sig = np.asarray(data2, dtype=np.float64)
        if ref.ndim > 1:
            ref = ref.mean(axis=1)
        if sig.ndim > 1:
            sig = sig.mean(axis=1)

        fs = sample_freq1
        if sample_freq1 != sample_freq2:
            target_len = int(round(sig.shape[0] * sample_freq1 / sample_freq2))
            if target_len <= 0:
                return 0
            sig = sps.resample(sig, target_len)

        ref_len = ref.shape[0]
        sig_len = sig.shape[0]
        fft_len = ref_len + sig_len - 1

        ref_fft = np.fft.rfft(ref, n=fft_len)
        sig_fft = np.fft.rfft(sig, n=fft_len)
        cross_spectrum = ref_fft * np.conj(sig_fft)

        magnitude = np.abs(cross_spectrum)
        magnitude[magnitude < 1e-15] = 1e-15
        correlation = np.fft.irfft(cross_spectrum / magnitude, n=fft_len)

        # Reorder to match integer lag range [-(len(sig)-1), len(ref)-1].
        correlation = np.concatenate((correlation[-(sig_len - 1):], correlation[:ref_len]))
        lags = np.arange(-(sig_len - 1), ref_len)
        lag = lags[np.argmax(np.abs(correlation))]

        picked_index = int(np.where(lags == lag)[0][0])
        self.plot_it(data1, correlation, picked_index)
        '''
        #if (runCount in [8,17,27]):
        if (True):
            plt.title(f"{runCount}  {exp_offs:.3f} - {(lag / fs):.3f}")
            plt.plot(data1)
            plt.plot(correlation, scaley=True)
            #plt.show(block=False)
            plt.show()
        runCount += 1
        '''
        return lag / fs

    def algorithm_fft(self, sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
        # This algorithm requires both samplerates to be identical.
        # If they aren't, one of the audio clips needs oversampling/downsampling to match
        assert(sample_freq1 == sample_freq2)
        audio_1 = data1
        audio_2 = data2
        samplerate = sample_freq1

        # Parameters for STFT
        nperseg = 512
        noverlap = nperseg // 2
        
        # Compute STFT
        f, t1, Sxx1 = sps.spectrogram(audio_1, samplerate, nperseg=nperseg, noverlap=noverlap)
        f, t2, Sxx2 = sps.spectrogram(audio_2, samplerate, nperseg=nperseg, noverlap=noverlap)
        
        # Normalize each frame to unit norm (makes it amplitude-invariant)
        Sxx1 = Sxx1 / np.sqrt(np.sum(Sxx1**2, axis=0, keepdims=True) + 1e-10)
        Sxx2 = Sxx2 / np.sqrt(np.sum(Sxx2**2, axis=0, keepdims=True) + 1e-10)
        
        # Use log-magnitude for better perceptual matching (humans perceive log-amplitude)
        Sxx1 = np.log1p(Sxx1)
        Sxx2 = np.log1p(Sxx2)
        
        # Re-normalize after log
        Sxx1 = Sxx1 / np.sqrt(np.sum(Sxx1**2, axis=0, keepdims=True) + 1e-10)
        Sxx2 = Sxx2 / np.sqrt(np.sum(Sxx2**2, axis=0, keepdims=True) + 1e-10)
        
        # Slide Sxx2 across Sxx1 and compute correlation
        num_frames_1 = Sxx1.shape[1]
        num_frames_2 = Sxx2.shape[1]
        num_positions = num_frames_1 - num_frames_2 + 1
        
        spectral_correlation = np.zeros(num_positions)
        
        for i in range(num_positions):
            window_1 = Sxx1[:, i:i+num_frames_2]
            spectral_correlation[i] = np.sum(window_1 * Sxx2)
        
        # Find peak
        frame_offset = np.argmax(spectral_correlation)
        offset_seconds = t1[frame_offset]
        offset_samples = int(offset_seconds * samplerate)
        
        # Pad to expected length
        expected_len = len(audio_1) - len(audio_2) + 1
        repeat_factor = expected_len // len(spectral_correlation) + 1
        spectral_correlation_padded = np.repeat(spectral_correlation, repeat_factor)[:expected_len]
        assert(expected_len == len(spectral_correlation_padded))

        # plottable correlation: spectral_correlation_padded
        return offset_samples / samplerate

# Finds max value of both waves and calculates the time difference
def algorithm_argmax(sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
    max1InSeconds = data1.argmax() / sample_freq1
    max2InSeconds = data2.argmax() / sample_freq2

    return max1InSeconds - max2InSeconds

# Creates shorter volume envelopes and correlates between them
def algorithm_amp_correlate(sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
    batch_size = 200
    amplitudes1 = get_amplitude_abs_max(data1, batch_size)
    amplitudes2 = get_amplitude_abs_max(data2, batch_size)

    correlation = sps.correlate(amplitudes1.astype(np.int64), amplitudes2.astype(np.int64), 'full')
    max_index = correlation.argmax()

    return (max_index - len(amplitudes2)) * batch_size / sample_freq2

def algorithm_amp_diff(sample_freq1: int, data1: np.ndarray, sample_freq2: int, data2: np.ndarray):
    batch_size = 200
    amplitudes1 = get_amplitude_abs_max(data1, batch_size)
    amplitudes2 = get_amplitude_abs_max(data2, batch_size)

    diffs = get_diffs(amplitudes1, amplitudes2)
    min_index = diffs.argmin()

    result = min_index * batch_size / sample_freq2

    return result

def get_diffs(arr1: np.ndarray, arr2: np.ndarray):
    diffs = []
    result_size = len(arr1) - len(arr2)
    if (result_size >= 0):
        r1 = arr1
        r2 = arr2
    else:
        r1 = arr2
        r2 = arr1
    for i in range(0, result_size):
        single_diff = 0
        for j in range(0, len(r2)):
            single_diff += np.int32(abs(r1[i + j] - r2[j]))
            if (single_diff > 32000):
                a = single_diff
        diffs.append(single_diff)
    return np.array(diffs)

# Other:
# - vectorized approach
# 
# average zero crossing frequency
    #sign_changes1 = np.diff(np.sign(data1))
    #zcf1 = np.count_nonzero(sign_changes1) / data1.shape[0]

# Feature methods
"""
def get_amplitude(audio: np.ndarray, window_size: int):
    amplitude = []
    for i in range(0, len(audio) - (window_size - 1)):
        audio_window = audio[i:(i + window_size)]
        max_value = max(audio_window)
        if (max_value < 0):
            max_value = - min(audio_window)
        amplitude.append(max_value)
    return amplitude
"""

def get_amplitude_max(audio: np.ndarray, batch_size: int):
    amplitude = []
    batch_count = int(len(audio) / batch_size)
    for i in range(0, batch_count):
        start = i * batch_size
        audio_window = audio[start:(start + batch_size)]
        max_value = max(audio_window)
        if (max_value < 0):
            max_value = -min(audio_window)
        amplitude.append(max_value)
    return amplitude

def get_amplitude_abs_max(audio: np.ndarray, batch_size: int):
    amplitude = []
    batch_count = int(len(audio) / batch_size)
    for i in range(0, batch_count):
        start = i * batch_size
        audio_window = audio[start:(start + batch_size)]
        max_value = np.max(np.abs(audio_window))
        amplitude.append(max_value)
        np.append(amplitude, max_value)
    amplitude2 = np.array(amplitude)
    return amplitude2
