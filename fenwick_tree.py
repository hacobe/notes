"""Fenwick Tree.

Also known as a Binary Indexed Tree.

A related data structure is Segment Tree, which is more complex to implement.
See also a discussion comparing the 2 data structures here:
https://stackoverflow.com/questions/64190332/fenwick-tree-vs-segment-tree

Motivation: "When compared with a flat array of numbers, the Fenwick tree achieves a
much better balance between two operations: element update and prefix sum calculation.
A flat array of n numbers can either store the elements or the prefix sums. In the
first case, computing prefix sums requires linear time; in the second case, updating
the array elements requires linear time (in both cases, the other operation can be
performed in constant time). Fenwick trees allow both operations to be performed in 
O(log n) time"
⁡(http://web.archive.org/web/20230131003155/https://en.wikipedia.org/wiki/Fenwick_tree)

Sources:
* http://web.archive.org/web/20230131153631/https://cp-algorithms.com/data_structures/fenwick.html
* http://web.archive.org/web/20230131002214/https://www.geeksforgeeks.org/binary-indexed-tree-or-fenwick-tree-2/
"""

class SlowAddFastPrefixSum:

	def __init__(self, arr):
		s = 0
		n = len(arr)
		self.data = [0] * n
		for i in range(n):
			s += arr[i]
			self.data[i] = s

	def add(self, i, amount):
		for j in range(i, len(self.data)):
			self.data[j] += amount

	def prefix_sum(self, end):
		return self.data[end-1]


class FastAddSlowPrefixSum:

	def __init__(self, arr):
		self.data = [x for x in arr]

	def add(self, i, amount):
		self.data[i] += amount

	def prefix_sum(self, end):
		s = 0
		for i in range(end):
			s += self.data[i]
		return s


def _last_set_bit(i):
	# Return the last set bit of i
	#
	# For example:
	#
	# 12  = 1100
	# -12 = Two's complement of 12
	#     = Invert binary representation of 12 and add 1
	#     = 0011 + 0001 (3 + 1)
	#     = 0100
	#
	#   1100 
	# & 0100
	# = 0100
	#
	# _last_set_bit(int("0b1100", 2)) = int("0b0100", 2)
	# i.e., _last_set_bit(12) = 4
	return i & (-i)


def _get_parent(i):
	return i - _last_set_bit(i)


def _get_next(i):
	return i + _last_set_bit(i)


class FenwickTree:

	def __init__(self, arr):
		n = len(arr)
		self.data = [0] * (n + 1)
		for i in range(n):
			self.add(i, arr[i])

	def add(self, i, delta):
		j = i + 1 # one-based index
		while j < len(self.data):
			self.data[j] += delta
			j = _get_next(j)

	def prefix_sum(self, end):
		s = 0
		j = end # one-based index
		while j > 0:
			s += self.data[j]
			j = _get_parent(j)
		return s


if __name__ == "__main__":
	arr = [2, 1, 1, 3, 2, 3, 4, 5, 6, 7, 8, 9]
	obj = SlowAddFastPrefixSum(arr)
	assert obj.prefix_sum(6) == 12
	obj.add(3, 5)
	assert obj.prefix_sum(6) == 17

	obj = FastAddSlowPrefixSum(arr)
	assert obj.prefix_sum(6) == 12
	obj.add(3, 5)
	assert obj.prefix_sum(6) == 17

	obj = FenwickTree(arr)
	assert obj.prefix_sum(6) == 12
	obj.add(3, 5)
	assert obj.prefix_sum(6) == 17

