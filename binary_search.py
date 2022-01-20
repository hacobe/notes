"""Binary search.

Implementation tips:
- We could split the array in half, but better to pass in the low and high indices
- Be careful about inclusive vs. exclusive indices
- Be careful about calculating the mid point
- Remember that the input must be sorted
"""

import sys

# [lo, hi)
def iterative_binary_search(arr, val, lo, hi):
	# Be careful about this inequality
	while lo < hi:
		mid = lo + ((hi - lo) // 2)
		if val == arr[mid]:
			return mid
		elif val < arr[mid]:
			hi = mid
		else:
			lo = mid + 1
	return -1

# [lo, hi)
def recursive_binary_search(arr, val, lo, hi):
	# Be careful about this inequality
	if lo >= hi:
		return -1
	mid = lo + ((hi - lo) // 2)
	if val == arr[mid]:
		return mid
	elif val < arr[mid]:
		return recursive_binary_search(arr, val, lo, mid)
	else:
		return recursive_binary_search(arr, val, mid + 1, hi)

def binary_search(arr, val, recursive=False):
	lo = 0
	hi = len(arr)
	if recursive:
		return recursive_binary_search(arr, val, lo, hi)
	else:
		return iterative_binary_search(arr, val, lo, hi)

# Test both recursive=True and recursive=False with:
# https://practice.geeksforgeeks.org/problems/who-will-win/0
def main(stdin, recursive=False):
	T = int(stdin.readline())
	for t in range(T):
		N, K = [int(x) for x in stdin.readline().split()]
		arr = [int(x) for x in stdin.readline().split()]
		idx = binary_search(arr, K, recursive)
		if idx != -1:
			print(1)
		else:
			print(-1)
