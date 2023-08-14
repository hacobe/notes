"""Implementation of malloc and free.

We maintain a "free list", where each entry is a [start, end) range
of addresses that are free.

We also maintain a "size map", which maps from a start address to
the size of the range reserved (not free) starting at that address.

When we call malloc, we search the free list for a range that is
large enough to accommodate the request. If we find a range that
exactly matches the request, then we remove the range from the 
free list. If we find a range that is larger than the request,
then we "split" that range into 2 parts by adjusting the start index
of the range. The first part serves as the new reserved space and
the second part remains on the free list. In both cases,
we update the size map and return the start address. Otherwise,
the request cannot be accommodated and we return -1.

When we call free, we look up the given start address in the size map.
If it is not there, we return False. If it is there, we use the
size associated with the address to create a new range [start, start + size)
and add it to the free list. We then "coalesce" the free list to merge
adjacent ranges of free space. Finally, we remove the start address from
the size map and return True.

Adapted from ostep3-malloc.py when:
* policy: FIRST
* returnPolicy: INSERT-BACK

Run tests:

pytest memory_manager.py

Sources:
* https://github.com/chyyuu/os_tutorial_lab/blob/master/ostep/ostep3-malloc.py
* https://github.com/chyyuu/os_tutorial_lab/blob/master/ostep/ostep3-malloc.md
* https://pages.cs.wisc.edu/~remzi/OSTEP/vm-freespace.pdf
"""
class MemoryManager:

	def __init__(self, capacity):
		self.free_list = [[0, capacity]]
		self.start_to_size = {}

	def malloc(self, size):
		# Find the first free span with sufficient space.
		j = -1
		for i in range(len(self.free_list)):
			start, end = self.free_list[i]
			if end - start >= size:
				j = i
				break

		# Insufficient space.
		if j == -1:
			return -1

		start, end = self.free_list[j]
		if end - start == size:
			self.free_list.pop(j)
		else:
			self.free_list[j][0] = start + size

		self.start_to_size[start] = size

		return start

	def free(self, start):
		if start not in self.start_to_size:
			return False

		size = self.start_to_size[start]

		# Inefficient and unrealistic coalescing.
		self.free_list.append([start, start + size])
		self.free_list.sort()
		free_list = [self.free_list[0]]
		for i in range(1, len(self.free_list)):
			if self.free_list[i][0] == free_list[-1][1]:
				# If the start of the i-th span in the free
				# list is equal to end, then extend
				# (start, end) span.
				free_list[-1][1] = self.free_list[i][1]
			else:
				# Otherwise, add the (start, end) span to the
				# free list.
				free_list.append(self.free_list[i])
		self.free_list = free_list

		del self.start_to_size[start]

		return True

########
# Tests
########


import copy
import pytest
import random


def _max_size(memory_manager):
	max_size = 0
	for i in range(len(memory_manager.free_list)):
		start, end = memory_manager.free_list[i]
		size = end - start
		max_size = max(size, max_size)
	return max_size


@pytest.fixture
def memory_manager():
	return MemoryManager(1000)


def test_init(memory_manager):
	assert memory_manager.free_list == [[0, 1000]]


def test_malloc_ok(memory_manager):
	# Reserve [0, 100)
	start0 = memory_manager.malloc(100)
	assert start0 == 0
	assert memory_manager.free_list == [[100, 1000]]


def test_malloc_fail(memory_manager):
	init_free_list = copy.copy(memory_manager.free_list)
	# Try to reserve [0, 10000)
	start0 = memory_manager.malloc(10000)
	assert start0 == -1
	# Nothing changes.
	assert memory_manager.free_list == init_free_list


def test_free_ok(memory_manager):
	start0 = memory_manager.malloc(100)
	assert memory_manager.free(start0)
	assert memory_manager.free_list == [[0, 1000]]


def test_free_fail(memory_manager):
	# Reserve [0, 100)
	start0 = memory_manager.malloc(100)
	# Invalid address.
	assert not memory_manager.free(start0 + 1)
	# Reserved space starting at `start0` remain
	# reserved. 
	assert memory_manager.free_list == [[100, 1000]]	


def test_multiple_malloc(memory_manager):
	# Reserve [0, 100)
	start0 = memory_manager.malloc(100)
	# Reserve [100, 400)
	start1 = memory_manager.malloc(300)
	assert start1 == 100
	assert memory_manager.free_list == [[400, 1000]]


def test_fragmentation(memory_manager):
	# Like test_multiple_malloc except
	# that we free the first reserved
	# block and then request a large block.

	# Reserve [0, 100)
	start0 = memory_manager.malloc(100)
	# Reserve [100, 400)
	start1 = memory_manager.malloc(300)
	# Free [0, 100)
	assert memory_manager.free(start0)
	# By freeing [0, 100), we add it back into the free list.
	assert memory_manager.free_list == [[0, 100], [400, 1000]]
	start2 = memory_manager.malloc(650)
	# We have enough free space across the ranges, but
	# not in any single range.
	assert start2 == -1


def test_coalesce(memory_manager):
	# Like test_multiple_malloc except
	# that we free the first reserved
	# block and then the second reserved
	# block.

	# Reserve [0, 100)
	start0 = memory_manager.malloc(100)
	assert start0 == 0
	# Reserve [100, 400)
	start1 = memory_manager.malloc(300)
	assert start1 == 100
	# Free [0, 100)
	assert memory_manager.free(start0)
	assert memory_manager.free_list == [[0, 100], [400, 1000]]
	# Free [100, 400)
	# We get [[0, 100], [100, 400], [400, 1000]] in the free list
	# and then the ranges are coalesced into [[0, 1000]].
	assert memory_manager.free(start1)
	assert memory_manager.free_list == [[0, 1000]]


def test_fuzz(memory_manager):
	"""Fuzz test.

	Initialize an empty list of start addresses (`starts`).
	
	Start looping. The outer loop is through biases
	(explained shortly) and the inner loop is through
	the number of operations performed.

	If the `starts` list is empty, then malloc a random size
	between 1 and the maximum size available (inclusive).

	Append the start address returned from malloc to the
	the `starts` list.

	If the `starts` list is not empty, then flip a biased coin
	to either malloc or free a randomly select start address.
	The bias is determined by the outer loop.

	At the end of the looping, shuffle the remaining starts
	and free the space associated with them one at a time.
	"""
	random.seed(0)
	starts = []
	for thd in [0.25, 0.5, 0.75]:
		for _ in range(10000):
			r = random.random()
			max_size = _max_size(memory_manager)
			if (max_size > 0) and ((not starts) or (r <= thd)):
				# Sample an index in [1, max_size] inclusive.
				size = random.randint(1, max_size)
				start = memory_manager.malloc(size)
				starts.append(start)
			else:
				# Sample an index in [0, len(starts) - 1] inclusive.
				i = random.randint(0, len(starts) - 1)
				start = starts.pop(i)
				memory_manager.free(start)

	random.shuffle(starts)
	while starts:
		start = starts.pop()
		memory_manager.free(start)

	assert memory_manager.free_list == [[0, 1000]]
