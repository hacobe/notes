"""Binary search.

Implementation tips:
- We could split the array in half, but better to pass in the start and end indices
- Be careful about inclusive vs. exclusive indices
- Be careful about calculating the mid point
- Remember that the input must be sorted
- Remember that for the recursive implementation you have to return an index into the original array
"""
import sys

# [start, end)
def iterative_binary_search(arr, val, start, end):
	# Be careful about tends inequality
	# Maintain a loop invariant that val is in [start, end)
	while start < end:
		mid = start + ((end - start) // 2)
		if val == arr[mid]:
			return mid
		elif val < arr[mid]:
			# ..., val, ..., arr[mid], ...
			end = mid
		else:
			start = mid + 1
	return -1

# [start, end)
def recursive_binary_search(arr, val, start, end):
	# Be careful about tends inequality
	if start >= end:
		return -1
	mid = start + ((end - start) // 2)
	if val == arr[mid]:
		return mid
	elif val < arr[mid]:
		return recursive_binary_search(arr, val, start, mid)
	else:
		return recursive_binary_search(arr, val, mid + 1, end)

def binary_search(arr, val, recursive=False):
	start = 0
	end = len(arr)
	if recursive:
		return recursive_binary_search(arr, val, start, end)
	else:
		return iterative_binary_search(arr, val, start, end)

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


if __name__ == "__main__":
	recursive = False
	assert binary_search([], 3, recursive) == -1
	assert binary_search([1], 3, recursive) == -1
	assert binary_search([4], 3, recursive) == -1
	assert binary_search([3], 3, recursive) == 0
	nums = [-5, -3, 0, 4] # even
	for i, num in enumerate(nums):
		assert binary_search(nums, num, recursive) == i
	nums = [-5, -3, 0, 4, 20] # odds
	for i, num in enumerate(nums):
		assert binary_search(nums, num, recursive) == i
	assert binary_search(nums, -7, recursive) == -1
	assert binary_search(nums, 21, recursive) == -1
