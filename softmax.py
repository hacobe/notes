"""Implementations of softmax and log softmax.

Notes:
* Supports NumPy 0-rank and 1-rank arrays
  Does not support lists (subtracting max throws an error)
* Be careful about types, shapes and lists vs. arrays
* The tests for stable_log_softmax are the same as the tests for stable_softmax,
  except we take the log of the outputs, except for the last test, because log(0) = -inf.
* The axis versions of the function just add the axis and keepdims args to max and sum.

Sources:
* Goodfellow, Deep learning, Section 4.1
* https://github.com/scipy/scipy/blob/main/scipy/special/_logsumexp.py
* https://github.com/scipy/scipy/blob/main/scipy/special/tests/test_logsumexp.py#L143
* https://github.com/scipy/scipy/blob/main/scipy/special/tests/test_log_softmax.py
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np


def naive_softmax(x):
	e_x = np.exp(x)
	return e_x / e_x.sum()


def stable_softmax(x):
	# caching the values is faster than
	# re-computing despite the copies required.
	# use ndarray.[max/sum], because it's slightly faster
	# (there is no ndarray.exp)
	# https://stackoverflow.com/questions/48942424/numpy-sum-vs-ndarray-sum
	z = x - x.max()
	e_z = np.exp(z)
	return e_z / e_z.sum()


def stable_log_softmax(x):
	z = x - x.max()
	logsumexp = np.log(np.exp(z).sum())
	return z - logsumexp


def stable_softmax_with_axis(x, axis):
	z = x - x.max(axis=axis, keepdims=True)
	e_z = np.exp(z)
	return e_z / e_z.sum(axis=axis, keepdims=True)


def stable_log_softmax_with_axis(x, axis):
	z = x - x.max(axis=axis, keepdims=True)
	logsumexp = np.log(np.exp(z).sum(axis=axis, keepdims=True))
	return z - logsumexp


def stable_softmax_with_temperature(x, t):
	xt = x / t
	z = xt - xt.max()
	e_z = np.exp(z)
	return e_z / e_z.sum()


if __name__ == "__main__":
	assert np.exp(-1e3) == 0
	assert np.exp(1e3) == np.inf

	################################
	# underflow and overflow issues
	################################

	# underflow
	# 0/0 = NaN
	assert np.isnan(naive_softmax(np.array([-1e3, -1e3]))).all()

	# overflow
	# inf/inf = NaN
	assert np.isnan(naive_softmax(np.array([1e3, 1e3]))).all()

	# handling some cases of underflow and overflow
	np.testing.assert_almost_equal(stable_softmax(np.array([-1e3, -1e3])), [0.5, 0.5])
	np.testing.assert_almost_equal(stable_softmax(np.array([1e3, 1e3])), [0.5, 0.5])

	# still stable_softmax can underflow
	# can result in -inf if the output is passed to a softmax
	# np.exp(1 - 1e3) / (np.exp(1 - 1e3) + np.exp(1e3 - 1e3))
	# 0 / (0 + 1)
	np.testing.assert_almost_equal(stable_softmax(np.array([1, 1e3])), [0., 1.])
	assert (np.log(stable_softmax(np.array([1, 1e3]))) == np.array([-np.inf, 0.])).all()

	# if you know that you'll pass the output to a log, then use stable_log_softmax
	np.testing.assert_almost_equal(stable_log_softmax(np.array([1, 1e3])), [-999., 0.])

	################################
	# unit tests for stable_softmax
	################################

	# 1 entry
	np.testing.assert_almost_equal(stable_softmax(np.array([4])), [1.])

	# all zeroes
	np.testing.assert_almost_equal(stable_softmax(np.array([0, 0, 0, 0])), [1./4] * 4)

	# all same
	np.testing.assert_almost_equal(stable_softmax(np.array([2, 2, 2])), [1./3] * 3)

	# one-hot input
	expected = [1/(1 + np.e), np.e / (1 + np.e)]
	np.testing.assert_almost_equal(stable_softmax(np.array([0, 1])), expected)

	# negative one-hot input
	np.testing.assert_almost_equal(stable_softmax(np.array([0, -1])), expected[::-1])

	# complex example
	x = np.arange(3)
	d = np.exp(0) + np.exp(1) + np.exp(2)
	expected = [np.exp(0)/d, np.exp(1)/d, np.exp(2)/d]
	np.testing.assert_almost_equal(stable_softmax(x), expected)

	# translation invariance for complex example
	np.testing.assert_almost_equal(stable_softmax(x + 100), expected)

	# avoid underflow
	np.testing.assert_almost_equal(stable_softmax(np.array([-1e3, -1e3])), [0.5, 0.5])

	# avoid overflow
	np.testing.assert_almost_equal(stable_softmax(np.array([1e3, 1e3])), [0.5, 0.5])

	# underflow
	np.testing.assert_almost_equal(stable_softmax(np.array([1, 1e3])), [0., 1.])

	####################################
	# unit tests for stable_log_softmax
	####################################

	# 1 entry
	np.testing.assert_almost_equal(stable_log_softmax(np.array([4])), [0.])

	# all zeroes
	np.testing.assert_almost_equal(stable_log_softmax(np.array([0, 0, 0, 0])), [np.log(1./4)] * 4)

	# all same
	np.testing.assert_almost_equal(stable_log_softmax(np.array([2, 2, 2])), [np.log(1./3)] * 3)

	# one-hot input
	expected = [np.log(1/(1 + np.e)), np.log(np.e / (1 + np.e))]
	np.testing.assert_almost_equal(stable_log_softmax(np.array([0, 1])), expected)

	# negative one-hot input
	np.testing.assert_almost_equal(stable_log_softmax(np.array([0, -1])), expected[::-1])

	# complex example
	x = np.arange(3)
	d = np.exp(0) + np.exp(1) + np.exp(2)
	expected = [np.log(np.exp(0)/d), np.log(np.exp(1)/d), np.log(np.exp(2)/d)]
	np.testing.assert_almost_equal(stable_log_softmax(x), expected)

	# translation invariance for complex example
	np.testing.assert_almost_equal(stable_log_softmax(x + 100), expected)

	# avoid underflow
	np.testing.assert_almost_equal(stable_log_softmax(np.array([-1e3, -1e3])), [np.log(0.5)] * 2)

	# avoid overflow
	np.testing.assert_almost_equal(stable_log_softmax(np.array([1e3, 1e3])), [np.log(0.5)] * 2)

	# underflow 
	np.testing.assert_almost_equal(stable_log_softmax(np.array([1, 1e3])), [-999, 0])

	#################################################
	# unit tests for stable_softmax_with_temperature
	#################################################

	np.testing.assert_almost_equal(
		stable_softmax_with_temperature(np.array([0, 1]), 1),
		np.array([1/(1+np.e), np.e/(1+np.e)]))

	np.testing.assert_almost_equal(
		stable_softmax_with_temperature(np.array([0, 1]), 1e3),
		np.array([0.5, 0.5]), decimal=3)

	np.testing.assert_almost_equal(
		stable_softmax_with_temperature(np.array([0, 1]), 1e-3),
		np.array([0., 1.]), decimal=3)

	##########################################
	# unit tests for stable_softmax_with_axis
	##########################################

	x = np.array([[1e3, 0], [1e3, 0]])

	np.testing.assert_almost_equal(
		stable_softmax_with_axis(x, axis=0),
		np.array([[.5, .5], [.5, .5]]))

	np.testing.assert_almost_equal(
		stable_softmax_with_axis(x, axis=1),
		np.array([[1, 0], [1, 0]]))

	##############################################
	# unit tests for stable_log_softmax_with_axis
	##############################################

	x = np.array([[1e3, 0], [1e3, 0]])

	np.testing.assert_almost_equal(
		stable_log_softmax_with_axis(x, axis=0),
		np.log(np.array([[.5, .5], [.5, .5]])))

	np.testing.assert_almost_equal(
		stable_log_softmax_with_axis(x, axis=1),
		np.array([[0, -1000], [0, -1000]]))