"""Distributed merge sort.

* Threading doesn't speed up anything, because of the GIL.
* Process doesn't share memory by default, so use multiprocessing.Array
* We could potentially do better by splitting up the initial input into more
  parts and sorting each part in a thread and then doing a K-way merge

Sources:
* https://csprimer.com/watch/multi-sort/
* https://leetcode.com/problems/sort-an-array/
"""
import numpy as np
import time
import multiprocessing

def merge_sort(arr, level=0):
	if len(arr) == 1:
		return

	mid = len(arr) // 2
	left = arr[:mid]
	right = arr[mid:]

	if level == 0:
		left = multiprocessing.Array('i', left)
		p_left = multiprocessing.Process(target=merge_sort, args=(left, level+1))
		p_left.start()
		# Continue sorting right in the parent process to avoid extra overhead of another process
		merge_sort(right, level+1) 
		p_left.join()
	else:
		merge_sort(left, level+1)
		merge_sort(right, level+1)

	i = j = k = 0
	while i < len(left) and j < len(right):
		if left[i] < right[j]:
			arr[k] = left[i]
			i += 1
			k += 1
		else:
			arr[k] = right[j]
			j += 1
			k += 1

	while i < len(left):
		arr[k] = left[i]
		i += 1
		k += 1

	while j < len(right):
		arr[k] = right[j]
		j += 1
		k += 1

if __name__ == "__main__":
	np.random.seed(0)
	arr = np.random.randint(low=0, high=32767, size=2**20)
	start_time = time.time()
	merge_sort(arr)
	elapsed = time.time() - start_time
	for i in range(len(arr)-1):
		assert arr[i] <= arr[i+1]
	print(elapsed)