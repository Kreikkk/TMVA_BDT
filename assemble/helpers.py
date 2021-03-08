import numpy as np


def normalized_hist_to_array(hist, nbins, include_error=True):
	arr = []
	if include_error:
		for index in range(1, nbins+1):
			arr.append(hist.GetBinContent(index) + hist.GetBinErrorUp(index))
	else:
		for index in range(1, nbins+1):
			arr.append(hist.GetBinContent(index))

	sum_of_weights = hist.GetSumOfWeights()

	return np.array(arr)/sum_of_weights


def get_hist_max(hist, nbins, include_error=True):
	arr = normalized_hist_to_array(hist, nbins, include_error)
	return np.max(arr)