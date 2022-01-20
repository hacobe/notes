"""Implement Heap sort in place.

Sources:
* https://www.geeksforgeeks.org/heap-sort/
* https://www.geeksforgeeks.org/python-program-for-heap-sort/
"""

def _heapify(arr, n, i):
	# Heapify subtree with root at index `i`
	# This function assumes that the children
	# of the root have already been heapified.
	l = 2 * i + 1
  
	if l >= n:
		return

	r = l + 1

	if r >= n or arr[l] > arr[r]:
		max_child = l
	else:
		max_child = r

	if arr[i] > arr[max_child]:
		return

	arr[i], arr[max_child] = arr[max_child], arr[i]
	_heapify(arr, n, max_child)


def heap_sort_in_place(arr):
	n = len(arr)
	# Apply _heapify bottom-up.
	for i in range(n // 2 - 1, -1, -1):
		_heapify(arr, n, i)
	
	for i in range(n - 1, 0, -1):
		# Take the max value in the heap
		# and place it at position `i`.
		arr[i], arr[0] = arr[0], arr[i]
		# Heapify at root 0 up to position `i`.
		_heapify(arr, i, 0)


def test_heap_sort_in_place():
    arr = [1, 5, 3, -4, -10, 0]
    heap_sort_in_place(arr)
    assert arr == [-10, -4, 0, 1, 3, 5], arr


if __name__ == "__main__":
	test_heap_sort_in_place()