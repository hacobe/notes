"""Find k-th largest value in a rank-2 array.

Strategies:
* sorting
* partition (np.partition or torch.topk)
* heap (doesn't work out of the box for arrays)

Sources:
* https://leetcode.com/problems/kth-largest-element-in-an-array/solution/
* https://stackoverflow.com/questions/33181350/quickest-way-to-find-the-nth-largest-value-in-a-numpy-matrix
* https://stackoverflow.com/questions/33623184/fastest-method-of-getting-k-smallest-numbers-in-unsorted-list-of-size-n-in-pytho
* https://leetcode.com/problems/kth-largest-element-in-an-array/discuss/1019513/Python-QuickSelect-average-O(n)-explained
"""
import numpy as np
import torch

def find_kth_largest_torch(arr, k):
	v, _ = torch.topk(torch.tensor(arr), k)
	v_last = np.array(v[:, [-1]].tolist())
	return v_last


def find_kth_largest_sort(arr, k):
	# O(n log n) on average
	return np.sort(arr, axis=1)[:, -k].reshape((-1, 1))


def find_kth_largest_partition(arr, k):
	# O(n) on average
	return np.partition(arr, kth=-k, axis=1)[:, -k].reshape((-1, 1))


if __name__ == "__main__":
	np.random.seed(0)
	arr = np.random.randn(4, 5)
	k = 2

	arr2 = np.array([[ 1.76405235, 0.40015721, 0.97873798, 2.2408932, 1.86755799],
		[-0.97727788, 0.95008842, -0.15135721, -0.10321885, 0.4105985 ],
		[0.14404357, 1.45427351, 0.76103773, 0.12167502, 0.44386323],
		[ 0.33367433,  1.49407907, -0.20515826,  0.3130677 , -0.85409574]])
	np.testing.assert_almost_equal(arr, arr2)

	expected = np.array([1.86755799, 0.4105985, 0.76103773, 0.33367433]).reshape((-1, 1))

	arr_k_torch = find_kth_largest_torch(arr, k)
	np.testing.assert_almost_equal(arr_k_torch, expected)

	arr_k_sort = find_kth_largest_sort(arr, k)
	np.testing.assert_almost_equal(arr_k_sort, expected)

	arr_k_partition = find_kth_largest_partition(arr, k)
	np.testing.assert_almost_equal(arr_k_partition, expected)