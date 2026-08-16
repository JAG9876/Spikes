import pytest
import scipy.io.wavfile as wavfile
import numpy as np
import matplotlib.pyplot as plt
import time
import my_correlation as mc

@pytest.mark.parametrize("wavfile1, wavfile2", [
        ('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav')
    ])
def test_overlap_correlation(wavfile1, wavfile2):
    sample_rate1, wave1 = wavfile.read(wavfile1)
    sample_rate2, wave2 = wavfile.read(wavfile2)

    #start1 = 547054
    #end1 = wave1.shape[0]
    start1 = 130000
    end1 = 170000
    #start2 = 0 
    #end2 = wave2.shape[0]
    start2 = 70000 
    end2 = 80000

    array1 = wave1[start1:end1]
    array2 = wave2[start2:end2]
    #array3 = np.zeros(1000, dtype=np.ndarray)
    #array4 = np.full(1000, 3, dtype=np.ndarray)
    ## Two full sine waves across 1000 samples, range [-1000, 1000]
    #t = np.linspace(0, 4 * np.pi, 1000, endpoint=False)
    #array5 = 1000 * np.sin(t)

    start_time = time.perf_counter()
    #correlation = mc.overlap_correlation2(array1, array2)
    #correlation2 = mc.overlap_correlation2(array2, array1)
    correlation3 = mc.overlap_correlation3(array2, array1)
    elapsed_time = time.perf_counter() - start_time
    print(f"overlap_correlation took {elapsed_time:.6f} seconds")

    #plt.plot(array1)
    #plt.show()
    #plt.plot(array5)
    #plt.show()
    #plt.plot(correlation)
    #plt.plot(correlation2)
    plt.plot(correlation3)
    plt.show()
