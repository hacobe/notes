"""Educational implementation of a buddy memory allocator.

We initialize the BuddyMemoryManager with a `size`, which is the total
amount of memory under management. We require that the `size` is a power
of 2.

The malloc method takes as input a `size`, i.e., the amount of free space
to reserve. If the request can be accommodated, then it returns the
start of the interval that it has reserved for the request.
Otherwise, it returns -1.

At a high level, a call to the malloc method keeps splitting intervals
in half until it finds a free interval that matches the smallest power of
2 greater than or equal to the requested size.

The free method takes as input a `start`, i.e., the start of a previously
reserved interval to free. If it successfully frees the interval, it returns
True. Otherwise, it returns False.

At a high-level, a call to the free method first frees the specified interval.
If the interval adjacent to the newly freed interval is also free, then
it joins the 2 intervals into a single, free interval. If the interval adjacent
to that single, free interval is also free, then it joins those 2 intervals
and so on until it reaches an adjacent interval that is not free or the root.

Notes:
* The implementation below is basically a translation of wuwenbin's implementation
  from C to Python with a few changes for readability.
  (h/t to cloudwu for pointing me to wuwenbin's implementation)
* The implementation makes use of some clever invariants (see comments in the code)
* The implementation uses a minimum interval size of 1 even though:
  "Typically the lower limit would be small enough to minimize the average wasted space
   per allocation, but large enough to avoid excessive overhead" (Wikipedia).
* test_cloudwu are the unit tests from cloudwu's implementation translated from
  C to Python.
* From cloudwu's blog post (according to Google Translate):
  "Under the standard algorithm, the time complexity of allocation and release
  is O(log N), and N will not be particularly large. The advantage of the algorithm
  is that the fragmentation rate is very small."
* Calculating node start and node size recursively is more intuitive
  than the bit manipulation tricks.

Run tests:

pytest buddy_memory_manager.py

See also:

* memory_manager.py

Sources:
* https://github.com/wuwenbin/buddy2
* https://web.archive.org/web/20230817144142/https://coolshell.cn/articles/10427.html

Additional sources:
* https://github.com/cloudwu/buddy
* https://web.archive.org/web/20230803151249/https://blog.codingnow.com/2011/12/buddy_memory_allocation.html
* Wikipedia (https://web.archive.org/web/20230813151519/https://en.wikipedia.org/wiki/Buddy_memory_allocation)
* A Fast Storage Allocator, Kenneth Knowlton (https://dl.acm.org/doi/pdf/10.1145/365628.365655)
"""


def _is_pow_of_2(x):
	return (x & (x - 1)) == 0


def _next_pow_of_2(x):
	return 1 if x == 0 else 1 << (x-1).bit_length()


def _left(i):
	return 2 * i + 1


def _right(i):
	return 2 * i + 2


def _parent(i):
	return (i + 1) // 2 - 1


class BuddyMemoryManager:

	def __init__(self, size):
		assert size >= 1
		assert isinstance(size, int)
		assert _is_pow_of_2(size)

		self._size = size

		# If `size` is 4, then we have [4, 2, 2, 1, 1, 1, 1],
		# which is 2 * `size` - 1 nodes.
		num_nodes = 2 * size - 1

		# Build `self._longest` such that `self._longest[i]`
		# is equal to the length of the longest free interval 
		# associated with a node in the subtree rooted at node `i`.
		# 
		# We want the root to have `node_size` equal to `size`.
		# Start at 2 * `size`, because we will divide by 2.
		node_size = 2 * size
		self._longest = [0 for _ in range(num_nodes)]
		for i in range(num_nodes):
			if _is_pow_of_2(i+1):
				# We move a level down the tree.
				node_size //= 2
			self._longest[i] = node_size

	def malloc(self, size):
		size = _next_pow_of_2(size)

		i = 0
		if size > self._longest[i]:
			return -1

		# Find a node with `node_size` equal to `size`.
		node_size = self._size
		node_start = 0
		while node_size != size:
			# Splitting.
			#
			# If there does not exist a reserved node in
			# the subtree, then going a level down in the
			# the tree amounts to splitting the current
			# node.

			# We know that `size` is less than `node_size`,
			# so we need to make `node_size` smaller.
			#
			# We also know that we have enough free space
			# somewhere, because `size` <= `self._longest[0]`.
			#
			# If the length of the longest interval in the
			# left subtree is longer, then we know we'll
			# have enough free space in the left subtree,
			# so we go left. Otherwise, we must have
			# enough free space in the right subtree, so
			# we go right.
			assert size < node_size
			if self._longest[_left(i)] >= size:
				i = _left(i)
			else:
				assert self._longest[_right(i)] >= size
				i = _right(i)
				node_start += node_size // 2
			node_size //= 2

		# We know that enough free space exists in the
		# tree and we traversed the tree always choosing
		# the subtree with enough free space.
		# When we find a node with `node_size` == `size`,
		# then it must be free, because if we went any
		# lower in the tree we wouldn't have enough free space.
		assert node_size == size
		assert self._longest[i] == size

		# Reserve the node.
		self._longest[i] = 0

		# Update the ancestors of the node.
		while i != 0:
			i = _parent(i)
			l = _left(i)
			r = _right(i)
			# Maintain the max-property.
			self._longest[i] = max(self._longest[l], self._longest[r])

		return node_start

	def free(self, start):
		if start < 0:
			return False

		# Find the node at the bottom of tree associated
		# with an interval that starts at `start`.
		#
		# For example, suppose that `self._size` = 4.
		#
		# i:        0  1  2  3  4  5  6
		# _longest: 4  2  2  1  1  1  1
		#
		# The leftmost node at the bottom of the tree starts
		# at index `self._size` - 1 = 3.
		#
		# Here is the tree along with the interval for each
		# node and the node index under the interval:
		#
		#             [0, 4)
		#               0
		#       /               \
		#     [0, 2)          [2, 4)
		#       1               2
		#    /      \       /       \
		# [0, 1)  [1, 2)  [2, 3)  [3, 4)
		#   3       4       5       6
		i = self._size - 1 + start

		if i >= len(self._longest):
			return False

		# If `start` is odd, then the `node_size` of the
		# reserved node must be 1, so self._longest[i] must
		# be 0 and we never enter the loop.
		#
		# If `start` is even, then the node must be a left
		# child, so going to the parent preserves the start.
		# 
		# It has to be the first node starting from the bottom
		# that is reserved, because otherwise the node wouldn't
		# have been able to be reserved.
		node_size = 1
		while self._longest[i] != 0:
			if i == 0:
				return False
			i = _parent(i)
			node_size *= 2

		# We first show that the formula below holds for the first node
		# on its level. We then show that the formula holds for subsequent
		# nodes on the same level by adding increments of node size to the
		# first node's start.
		#
		# Let f(i) be the node start of the i-th node.
		# Let g(i) be the node size of the i-th node.
		# Let l(i) be the 0-indexed level of the i-th node.
		# Let p(i) be the 0-indexed position of the i-th node on its level.
		#
		# We want to show that:
		# f(i) = (i + 1) * g(i) - g(0)
		#
		# If p(i) = 0, we know that f(i) = 0.
		#
		# We also have that:
		# * i = 2^l(i) - 1
		# * g(i) = g(0)/(2^l(i))
		#
		# Plugging these equalities in, we get:
		# (i + 1) * g(i) - g(0)
		# = (2^l(i) - 1 + 1) * (g(0)/(2^l(i))) - g(0)
		# = g(0) - g(0)
		# = 0
		#
		# If p(i) != 0, we know that:
		# * f(i) = f(i - p(i)) + g(i) * p(i)
		# * g(i - p(i)) = g(i)
		#
		# We also have that:
		# f(i - p(i)) + g(i) * p(i)
		# = (i - p(i) + 1) * g(i - p(i)) - g(0) + g(i) * p(i)
		# = (i - p(i) + 1) * g(i) - g(0) + g(i) * p(i)
		# = i * g(i) - p(i) * g(i) + g(i) - g(0) + g(i) * p(i)
		# = i * g(i) - g(0)
		node_start = (i + 1) * node_size - self._size

		if node_start != start:
			return False

		# Free the node.
		self._longest[i] = node_size

		# Update the ancestors of the node.
		while i != 0:
			i = _parent(i)
			l = _left(i)
			r = _right(i)
			node_size *= 2

			if self._longest[l] + self._longest[r] == node_size:
				# Coalescing.
				#
				# If the left and the right children of a node
				# are free, then free the node too.
				self._longest[i] = node_size
			else:
				# Maintain the max-property.
				self._longest[i] = max(self._longest[l], self._longest[r])

		return True

	def size(self, start):
		# Similar logic to `free`.
		if start < 0:
			return -1

		i = self._size - 1 + start
		if i >= len(self._longest):
			return -1

		node_size = 1
		while self._longest[i] != 0:
			if i == 0:
				return -1
			node_size *= 2
			i = _parent(i)
		return node_size

	def _str(self, i, node_start, node_size):
		longest = self._longest[i]

		# Leaf node.
		if longest == node_size:
			return f"({node_start}:{node_size})"

		# Leaf node.
		l = _left(i)
		if l >= len(self._longest):
			assert longest == 0
			return f"[{node_start}:{node_size}]"

		# Leaf node.
		r = _right(i)
		if longest == 0 and self._longest[l] != 0 and self._longest[r] != 0:
			return f"[{node_start}:{node_size}]"

		# Internal node.
		left_string = self._str(
			l, node_start=node_start, node_size=node_size // 2)
		right_string = self._str(
			r, node_start=node_start + node_size // 2, node_size=node_size // 2)

		if longest == 0:
			return "{" + left_string + right_string + "}"

		return "(" + left_string + right_string + ")"

	def __str__(self):
		return self._str(0, node_start=0, node_size=self._size)


########
# Tests
########


import pytest
import random


def _max_size(buddy):
	return max(buddy._longest)


@pytest.fixture
def buddy():
	return BuddyMemoryManager(1024)


def test_init(buddy):
	assert str(buddy) == "(0:1024)"


def test_malloc_ok(buddy):
	# Reserve [0, 512)
	start0 = buddy.malloc(512)
	assert start0 == 0
	assert str(buddy) == "([0:512](512:512))"


def test_malloc_fail(buddy):
	init_tree = str(buddy)
	# Try to reserve [0, 10000)
	start0 = buddy.malloc(10000)
	assert start0 == -1
	# Nothing changes.
	assert str(buddy) == init_tree


def test_free_ok(buddy):
	start0 = buddy.malloc(512)
	buddy.free(start0)
	assert str(buddy) == "(0:1024)"


def test_free_fail(buddy):
	# Reserve [0, 512)
	start0 = buddy.malloc(512)
	# Invalid address.
	assert not buddy.free(start0 + 1)
	# Reserved space starting at `start0` remain
	# reserved. 
	assert str(buddy) == "([0:512](512:512))"	


def test_multiple_malloc(buddy):
	# Reserve [0, 512)
	start0 = buddy.malloc(512)
	# Reserve [512, 640)
	start1 = buddy.malloc(120)
	assert start1 == 512
	assert str(buddy) == "([0:512](([512:128](640:128))(768:256)))"	


def test_fragmentation(buddy):
	# Like test_multiple_malloc except
	# that we free the first reserved
	# block and then request a large block.

	# Reserve [0, 512)
	start0 = buddy.malloc(512)
	# Reserve [512, 640)
	start1 = buddy.malloc(120)
	# Free [0, 512)
	assert buddy.free(start0)
	assert str(buddy) == "((0:512)(([512:128](640:128))(768:256)))"	
	start2 = buddy.malloc(520)
	# We have enough free space across the ranges, but
	# not in any single range.
	assert start2 == -1


def test_coalesce(buddy):
	# Like test_multiple_malloc except
	# that we free the first reserved
	# block and then the second reserved
	# block.

	# Reserve [0, 512)
	start0 = buddy.malloc(512)
	assert start0 == 0
	# Reserve [512, 640)
	start1 = buddy.malloc(120)
	assert start1 == 512
	# Free [0, 512)
	assert buddy.free(start0)
	assert str(buddy) == "((0:512)(([512:128](640:128))(768:256)))"
	# Free [512, 640)
	# We get the tree:
	# ((0:512)(((512:128)(640:128))(768:256))) and then the
	# intervals are coalesced into (0:1024).
	assert buddy.free(start1)
	assert str(buddy) == "(0:1024)"


def test_fuzz(buddy):
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
			max_size = _max_size(buddy)
			if (max_size> 0) and ((not starts) or (r <= thd)):
				# Sample an index in [1, max_size] inclusive.
				size = random.randint(1, max_size)
				start = buddy.malloc(size)
				starts.append(start)
			else:
				# Sample an index in [0, len(starts) - 1] inclusive.
				i = random.randint(0, len(starts) - 1)
				start = starts.pop(i)
				buddy.free(start)

	random.shuffle(starts)
	while starts:
		start = starts.pop()
		buddy.free(start)

	assert str(buddy) == "(0:1024)"


def test_cloudwu():
	b = BuddyMemoryManager(32)
	assert str(b) == "(0:32)"
	
	m1 = b.malloc(4)
	assert m1 == 0
	assert b.size(m1) == 4
	assert str(b) == "((([0:4](4:4))(8:8))(16:16))"
	
	m2 = b.malloc(9)
	assert m2 == 16
	assert b.size(m2) == 16
	assert str(b) == "((([0:4](4:4))(8:8))[16:16])"
	
	m3 = b.malloc(3)
	assert m3 == 4
	assert b.size(m3) == 4
	assert str(b) == "(({[0:4][4:4]}(8:8))[16:16])"

	m4 = b.malloc(7)
	assert m4 == 8
	assert b.size(m4) == 8
	assert str(b) == "{{{[0:4][4:4]}[8:8]}[16:16]}"

	assert b.free(m3)
	assert str(b) == "((([0:4](4:4))[8:8])[16:16])"

	assert b.free(m1)
	assert str(b) == "(((0:8)[8:8])[16:16])"

	assert b.free(m4)
	assert str(b) == "((0:16)[16:16])"

	assert b.free(m2)
	assert str(b) == "(0:32)"

	m5 = b.malloc(32)
	assert m5 == 0
	assert b.size(m5) == 32
	assert str(b) == "[0:32]"

	assert b.free(m5)
	assert str(b) == "(0:32)"

	m6 = b.malloc(0)
	assert m6 == 0
	assert b.size(m6) == 1
	assert str(b) == "((((([0:1](1:1))(2:2))(4:4))(8:8))(16:16))"

	assert b.free(m6)
	assert str(b) == "(0:32)"
