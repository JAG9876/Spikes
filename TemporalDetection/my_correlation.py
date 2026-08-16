import numpy as np


def overlap_correlation(a: np.ndarray, b: np.ndarray) -> np.ndarray:
	"""Compute correlation values by iterating all possible overlaps.

	Parameters
	----------
	a : np.ndarray
		First 1D array.
	b : np.ndarray
		Second 1D array.

	Returns
	-------
	np.ndarray
		Correlation values for lags from ``-(len(b)-1)`` to ``len(a)-1``.
	"""
	a = np.asarray(a).ravel()
	b = np.asarray(b).ravel()

	n = a.size
	m = b.size

	if n == 0 or m == 0:
		return np.array([], dtype=np.result_type(a.dtype, b.dtype, np.float64))

	out_dtype = np.result_type(a.dtype, b.dtype, np.float64)
	corr = np.zeros(n + m - 1, dtype=out_dtype)

	k = 0
	for lag in range(-(m - 1), n):
		total = 0.0
		for i in range(n):
			j = i - lag
			if 0 <= j < m:
				total += a[i] * b[j]
		corr[k] = total
		k += 1

	return corr

def overlap_correlation2(a: np.ndarray, b: np.ndarray) -> np.ndarray:
	a = np.asarray(a).ravel()
	b = np.asarray(b).ravel()

	n = a.size
	m = b.size

	if n == 0 or m == 0:
		return np.array([], dtype=np.result_type(a.dtype, b.dtype, np.float64))

	out_dtype = np.result_type(a.dtype, b.dtype, np.float64)
	corr = np.zeros(n + m - 1, dtype=out_dtype)

	for i in range(m - n):
		#if i % 100 == 0:
		#print('Run# = ', i)
		total = 0.0
		for j in range(n):
			total += b[i+j] * a[j]
		corr[i] = total

	return corr

def overlap_correlation3(a: np.ndarray, b: np.ndarray) -> np.ndarray:
	a2 = a.astype(dtype=np.float32)
	b2 = b.astype(dtype=np.float32)

	# normalize to +-1
	a_data = np.clip(a2 / 32767.0, -1.0, 1.0)
	b_data = np.clip(b2 / 32767.0, -1.0, 1.0)

	a_len = len(a_data)
	b_len = len(b_data)

	out = np.zeros(b_len, dtype = np.float32)

	for i in range(0, b_len - a_len):
		my_sum = 0
		for j in range(0, a_len):
			my_sum += b_data[i+j] * a_data[j]
		out[i] = my_sum

	return out