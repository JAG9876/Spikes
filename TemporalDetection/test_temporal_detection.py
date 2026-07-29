import pytest
import scipy.io.wavfile as wavfile
import temporal_detection as td
import time
import os
import numpy as np
from scipy.signal.windows import hamming as _hamming
import scipy.signal as sps

file_offset = 1.953 * 48000

def hamming(signal, sym=True, dtype=np.float64, normalize=False):
    x = np.asarray(signal, dtype=dtype)
    w = _hamming(x.shape[0], sym=sym)
    if normalize and w.max() > 0:
        w = w / w.max()
    return x * w

base = os.path.join("test_files", "audio")

mobile_audio = os.path.join(base, "OneClapPianoMobile.wav")
pc_audio = os.path.join(base, "OneClapStuebordPCMono.wav")
spike_audio = os.path.join(base, "single_pulse_10s_48k_mono16.wav")
sine_and_spike_audio = os.path.join(base, "single_sine_and_pulse_10s_48k_mono16.wav")
sine_audio = os.path.join(base, "single_sine_10s_48k_mono16.wav")

@pytest.mark.parametrize("wavfile1, wavfile2, full_expected_offset, algorithm", [
        # < 1 second
        (mobile_audio, pc_audio, 1.953, td.Algorithm.ARGMAX),
        # 7 minutes
        (mobile_audio, pc_audio, 1.953, td.Algorithm.CORRELATION),
        # < 1 second
        (mobile_audio, pc_audio, 1.953, td.Algorithm.SCI_PI_CORRELATION),
        # ? seconds
        (mobile_audio, pc_audio, 1.953, td.Algorithm.AMP_CORRELATION),
        # ? seconds
        (mobile_audio, pc_audio, 1.953, td.Algorithm.GCCPHAT)
    ])
def test_get_offset(wavfile1, wavfile2, full_expected_offset, algorithm: td.Algorithm):
    wave1 = wavfile.read(wavfile1)

    sample_rate2, wave2 = wavfile.read(wavfile2)
    wave2_length = wave2.shape[0]
    err = check_window(wave1, wave2, 0, wave2_length, sample_rate2, full_expected_offset * 48000, full_expected_offset, algorithm)
    assert err == None

@pytest.mark.parametrize("wavfile1, wavfile2, full_expected_offset, algorithm", [
        #('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.CORRELATION),
        # 4 seconds, error = 47%
        (mobile_audio, pc_audio, 1.953, td.Algorithm.SCI_PI_CORRELATION),
        # 24 seconds, error = 60%
        (mobile_audio, pc_audio, 1.953, td.Algorithm.AMP_CORRELATION),
        # 3 minutes, error = 63%
        (mobile_audio, pc_audio, 1.953, td.Algorithm.AMP_DIFF),
        # 28 seconds, error = 60%
        (mobile_audio, pc_audio, 1.953, td.Algorithm.GCCPHAT),
        (mobile_audio, mobile_audio, 0.0, td.Algorithm.GCCPHAT),
        (sine_audio, sine_audio, 0.0, td.Algorithm.GCCPHAT)
    ])
def test_get_offset_accuracy_and_speed(wavfile1, wavfile2, full_expected_offset, algorithm: td.Algorithm):
    errors = []
    count_total = 0

    wave1 = wavfile.read(wavfile1)
    # sample_rate2, wave2 = wavfile.read(wavfile2)
    # wave2_length = wave2.shape[0]

    s_rate2, w2 = wavfile.read(wavfile2)
    w_length = w2.shape[0]

    sample_rate2 = s_rate2
    
    #wave2 = td.band_reject(sample_rate2, w2, 5, 5)
    
    #sos = sps.butter(2, 15, btype="highpass", fs=sample_rate2, output="sos")    
    #wave2 = sps.sosfilt(sos, w2.astype(np.float64))

    wave2 = w2
    
    wave2_length = wave2.shape[0]

    start_time = time.perf_counter()

    # Cut from the start of wave2
    #'''
    for i in range(0, 10):
        start = int(wave2_length * i / 10)
        end = wave2_length
        expected_offset = full_expected_offset + start / sample_rate2

        err = check_window(wave1, wave2, start, end, sample_rate2, full_expected_offset * 48000, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1
        print(f"i={i}")
        #input("Press Enter to continue")

    # Cut from the end of wave2
    for i in range(10, 0, -1):
        start = 0
        end = int(wave2_length * i / 10)
        expected_offset = full_expected_offset

        err = check_window(wave1, wave2, start, end, sample_rate2, full_expected_offset * 48000, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1
    #'''
    
    # Pan wave2 with a 1/NUM_SECTION'th window
    NUM_SECTION = 10
    for i in range(0,NUM_SECTION):
        start = int(wave2_length * i / NUM_SECTION)
        end = int(start + wave2_length / NUM_SECTION)
        expected_offset = full_expected_offset + start / sample_rate2

        err = check_window(wave1, wave2, start, end, sample_rate2, full_expected_offset * 48000, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1
    #'''

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    err_count = len(errors)
    err_percentage = err_count / count_total

    assert err_percentage < 0.1, f"Errors: {err_percentage:,.2%} ({err_count}/{count_total}). Execution time: {execution_time:.4f} seconds"

runCount = 0

def check_window(wave1, wave2, start, end, sample_rate2, file_offset, expected_offset, algorithm = td.Algorithm.ARGMAX):
    global runCount
    runCount += 1

    my_td = td.TemporalDetection(wave2, start, end, file_offset, expected_offset, runCount)

    _wave3 = wave2[start:end]
    #td.get_offset(wave1, (sample_rate2, _wave3), algorithm)

    wave3 = _wave3
    #wave3 = hamming(_wave3)

    offset_in_seconds = my_td.get_offset(wave1, (sample_rate2, wave3), algorithm)

    #if offset_in_seconds != pytest.approx(expected_offset, rel=0.01):
    if offset_in_seconds != pytest.approx(expected_offset, rel=0.05):
        start_time = start / sample_rate2
        end_time = end / sample_rate2
        return f"Wavfile2 window ({start_time:,.3f},{end_time:,.3f}). Expected offset is {expected_offset:,.3f}, but actual was {offset_in_seconds:,.3f}"

    return None

if __name__ == '__main__':
    pytest.main
