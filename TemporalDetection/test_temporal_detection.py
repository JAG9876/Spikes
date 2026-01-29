import pytest
import scipy.io.wavfile as wavfile
import temporal_detection as td

@pytest.mark.parametrize("wavfile1, wavfile2, full_expected_offset, algorithm", [
        # < 1 second
        ('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.ARGMAX),
        # 7 minutes
        ('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.CORRELATION),
        # < 1 second
        ('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.SCI_PI_CORRELATION)
    ])
def test_get_offset(wavfile1, wavfile2, full_expected_offset, algorithm: td.Algorithm):
    wave1 = wavfile.read(wavfile1)
    sample_rate2, wave2 = wavfile.read(wavfile2)
    wave2_length = wave2.shape[0]
    err = check_window(wave1, wave2, 0, wave2_length, sample_rate2, full_expected_offset, algorithm)
    assert err == None

@pytest.mark.parametrize("wavfile1, wavfile2, full_expected_offset, algorithm", [
        ('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.SCI_PI_CORRELATION),
        #('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMonoHPF.wav', 1.953, td.Algorithm.SCI_PI_CORRELATION),
        #('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.CORRELATION)
    ])
def test_get_offset_speed(wavfile1, wavfile2, full_expected_offset, algorithm: td.Algorithm):
    errors = []
    count_total = 0

    wave1 = wavfile.read(wavfile1)
    sample_rate2, wave2 = wavfile.read(wavfile2)
    wave2_length = wave2.shape[0]

    # Cut from the start of wave2
    for i in range(0, 10):
        start = int(wave2_length * i / 10)
        end = wave2_length
        expected_offset = full_expected_offset + start / sample_rate2

        err = check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1

    # Cut from the end of wave2
    for i in range(10, 0, -1):
        start = 0
        end = int(wave2_length * i / 10)
        expected_offset = full_expected_offset

        err = check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1
    
    # Pan wave2 with a 1/10th window
    for i in range(0,10):
        start = int(wave2_length * i / 10)
        end = int(start + wave2_length / 10)
        expected_offset = full_expected_offset + start / sample_rate2

        err = check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1

    err_count = len(errors)
    err_percentage = err_count / count_total
    assert err_percentage < 0.1, f"Errors: {err_percentage:,.2%} ({err_count}/{count_total})"


@pytest.mark.parametrize("wavfile1, wavfile2, full_expected_offset, algorithm", [
        ('test_files\\audio\\OneClapPianoMobile.wav', 'test_files\\audio\\OneClapStuebordPCMono.wav', 1.953, td.Algorithm.CORRELATION)
    ])
def test_get_offset_accuracy(wavfile1, wavfile2, full_expected_offset, algorithm: td.Algorithm):
    errors = []
    count_total = 0

    wave1 = wavfile.read(wavfile1)
    sample_rate2, wave2 = wavfile.read(wavfile2)
    wave2_length = wave2.shape[0]

    # Cut from the start of wave2
    for i in range(0, 10):
        start = int(wave2_length * i / 10)
        end = wave2_length
        expected_offset = full_expected_offset + start / sample_rate2

        err = check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1

    # Cut from the end of wave2
    for i in range(10, 0, -1):
        start = 0
        end = int(wave2_length * i / 10)
        expected_offset = full_expected_offset

        err = check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1

    # Pan wave2 with a 1/10th window
    for i in range(0,10):
        start = int(wave2_length * i / 10)
        end = int(start + wave2_length / 10)
        expected_offset = full_expected_offset + start / sample_rate2

        err = check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm)

        if err != None:
            errors.append(err)
        count_total += 1

    err_count = len(errors)
    err_percentage = err_count / count_total
    assert err_percentage < 0.1, f"Errors: {err_percentage:,.2%} ({err_count}/{count_total})"

def check_window(wave1, wave2, start, end, sample_rate2, expected_offset, algorithm = td.Algorithm.ARGMAX):
    wave3 = wave2[start:end]

    offset_in_seconds = td.get_offset(wave1, (sample_rate2, wave3), algorithm)

    if offset_in_seconds != pytest.approx(expected_offset, rel=0.01):
        start_time = start / sample_rate2
        end_time = end / sample_rate2
        return f"Wavfile2 window ({start_time:,.3f},{end_time:,.3f}). Expected offset is {expected_offset:,.3f}, but actual was {offset_in_seconds:,.3f}"

    return None

if __name__ == '__main__':
    pytest.main
