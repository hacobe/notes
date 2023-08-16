"""Educational implementation of a buddy memory allocator.

We initialize the BuddyMemoryManager with a `capacity`, which is the total
amount of memory under management. We require that the `capacity` is a power
of 2.

We initialize a tree with a root node. We associate the root node with
the interval [0, `capacity`) and mark it as unreserved.

The malloc method takes as input a `size`, i.e., the amount of free space
to reserve. If the request can be accommodated, then it returns the
start of the interval that it has reserved for the request.
Otherwise, it returns -1.

At a high level, a call to the malloc method keeps splitting intervals
in half until it finds a free interval that matches the smallest power of
2 greater than or equal to the requested size.

In more detail:
1. Find the smallest power of 2 that is greater than or equal to `size`.
   Call this quantity the `target_length`.
2. Set the current node to the root node.
3. If the `target_length` is greater than the length of the interval
   associated with the current node, then return -1, because the request
   cannot be accommodated.
4. If the `target_length` is equal to the length of the interval, the
   current node is a leaf node and is not reserved, then mark the current
   node as reserved and return the start of the interval associated with it.
   (When we mark the current node as reserved, we also update the ancestors
   of the node so that if the children of a node are reserved then that
   node is also marked as reserved)
5. If the `target_length` is less than the length of the interval and the
   current node is not reserved, then go to the left child of the current
   node. If the left child does not exist, then first "split" the current
   node (i.e., create an unreserved left child associated with the left half
   of the current node's interval and an unreserved right child associated
   with the right half), then set the current node to the left child and
   go back to (3).
6. Otherwise, the node is reserved or the node is not reserved but is a parent
   with a descendant that is reserved. In either of these cases, set the current
   node to the next node in a breadth-first ordering of the nodes and go back
   to (3). If no next node exists, then create it.

The free method takes as input a `start`, i.e., the start of a previously
reserved interval to free. If it successfully frees the interval, it returns
True. Otherwise, it returns False.

At a high-level, a call to the free method first frees the specified interval.
If the interval adjacent to the newly freed interval is also free, then
it joins the 2 intervals into a single, free interval. If the interval adjacent
to that single, free interval is also free, then it joins those 2 intervals
and so on until it reaches an adjacent interval that is not free or the root.

In more detail:
1. Set the current node to the root node.
2. If the current node is a leaf and is reserved, then it must be the interval
   that starts with the given `start` (otherwise, the given `start` is invalid
   and we return False)

   a) If the current node is the root or the sibling of the current node is
      reserved or the sibling of the current node is a parent (i.e., one of
      its descendants is reserved), then mark the current node as unreserved,
      remove its descendants and return True.
      (When we mark the current node as unreserved, we also update the
      ancestors of the node so that if any children of a node are unreserved
      then that node is also marked as unreserved)

   b) Otherwise, set the current node to its parent and go to (a).

   In this way, if a parent's children will both be unreserved after we mark
   the current node unreserved, then we "coalesce", i.e., join the intervals
   associated with the children, and go up a level.
3. Otherwise, if `start` is less than the midpoint of the interval associated
   with the current node, set the current node to its left child node and go
   to (2). If `start` is greater than or equal to the midpoint of the interval,
   set the current node to its right child node and go to (2).

Notes:

The implementation below is inspired by cloudwu's implementation
(see "Sources" below) though it uses a node class with pointers instead of an
array to represent the binary tree. It also generally sacrifices efficiency for
readability. It does not exploit some of the bit manipulation tricks that are often
used in implementations of buddy memory allocation. For example: "The address of a
block's 'buddy' is equal to the bitwise exclusive OR (XOR) of the block's address
and the block's size" (Wikipedia). It also uses a minimum interval size of 1 though:
"Typically the lower limit would be small enough to minimize the average wasted space
per allocation, but large enough to avoid excessive overhead" (Wikipedia).

From cloudwu's blog post (according to Google Translate):
"Under the standard algorithm, the time complexity of allocation and release is O(log N),
 and N will not be particularly large. The advantage of the algorithm is that the fragmentation
 rate is very small."

Run tests:

pytest buddy_memory_manager.py

See also:

* memory_manager.py

Sources:

* https://github.com/cloudwu/buddy
* https://web.archive.org/web/20230803151249/https://blog.codingnow.com/2011/12/buddy_memory_allocation.html
* Wikipedia (https://web.archive.org/web/20230813151519/https://en.wikipedia.org/wiki/Buddy_memory_allocation)
* A Fast Storage Allocator, Kenneth Knowlton (https://dl.acm.org/doi/pdf/10.1145/365628.365655)
"""


def _is_pow_of_2(x):
	return (x & (x-1)) == 0


def _next_pow_of_2(x):
	return 1 if x == 0 else 1 << (x-1).bit_length()


class Node:
	
	def __init__(self, index, start, length, parent):
		self.index = index
		self.start = start
		self.length = length
		self.parent = parent
		self.left = None
		self.right = None
		self._is_reserved = False

	def reserve(self):
		self._is_reserved = True

	def unreserve(self):
		self._is_reserved = False

	@property
	def is_leaf(self):
		return (not self.left) and (not self.right)

	@property
	def is_parent(self):
		return self.left or self.right

	@property
	def sibling(self):
		if not self.parent:
			return

		if self.parent.left == self:
			return self.parent.right

		return self.parent.left

	@property
	def is_reserved(self):
		return self._is_reserved

	def __str__(self, prefix=""):
		start = self.start
		length = self.length
		if self.is_leaf and (not self.is_reserved):
			return prefix + f"({start}:{length})"
		elif self.is_leaf and self.is_reserved:
			return prefix + f"[{start}:{length}]"
		elif self.is_parent and (not self.is_reserved):
			string = "("
			string += self.left.__str__(prefix)
			string += self.right.__str__(prefix)
			string += ")"
			return string
		elif self.is_parent and self.is_reserved:
			string = "{"
			string += self.left.__str__(prefix)
			string += self.right.__str__(prefix)
			string += "}"
			return string


class BuddyMemoryManager:

	def __init__(self, capacity):
		if not isinstance(capacity, int):
			raise ValueError("capacity must be an integer")
		if not (capacity > 0):
			raise ValueError("capacity must be > 0")
		if not _is_pow_of_2(capacity):
			raise ValueError("capacity must be a power of 2")
		
		self._root = Node(
			index=0,
			start=0,
			length=capacity,
			parent=None)
		max_num_nodes = (1 << capacity.bit_length()) - 1
		self._nodes = [None] * max_num_nodes

	def _split(self, node):
		node.left = Node(
			index=(2 * (node.index + 1)) - 1,
			parent=node,
			start=node.start,
			length=node.length // 2)
		self._nodes[node.left.index] = node.left

		node.right = Node(
			index=2 * (node.index + 1),
			parent=node,
			start=node.start + node.length // 2,
			length=node.length // 2)
		self._nodes[node.right.index] = node.right

	def malloc(self, size):
		target_length = _next_pow_of_2(size)

		node = self._root
		while node:
			if target_length > node.length:
				return -1
			elif target_length == node.length and node.is_leaf and (not node.is_reserved):
				node.reserve()

				curr = node
				while curr:
					if curr.sibling and curr.sibling.is_reserved:
						curr = curr.parent
						curr.reserve()
					else:
						break

				return node.start
			elif target_length < node.length and (not node.is_reserved):
				if node.is_leaf:
					self._split(node)
				node = node.left
			else:
				a = (target_length <= node.length and node.is_reserved) 
				# If a node is a parent, then one of its children is reserved
				# even if the node itself is not reserved.
				b = (target_length == node.length and node.is_parent and (not node.is_reserved))
				assert a or b
				next_index = node.index + 1
				if next_index >= len(self._nodes):
					return -1

				"""
				If the next node does not exist, we have to create it.

				Consider the following tree:

						 0:1024
						/      \
				  [0:512]  512:512
                      /       \
                [512:256]   768:256
                           /       \
                        768:128    896:128
                        /      \    
                   [768:64]  832:64   
                             /     \
                        [832:32] 864:32 

            Or in string form:

            ([0:512]([512:256](([768:64]([832:32](864:32)))(896:128))))

            If we call malloc(64), then we'll end up at node 832:64,
            but that node is a parent, so it cannot be reserved. We want
            to go to the next node, but the next node does not exist.
				"""
				i = next_index
				while i >= 0:
					node = self._nodes[i]

					if node:
						while node.index < next_index:
							if node.is_leaf:
								self._split(node)
							node = node.left
						break
					else:
						# parent
						i = ((i + 1) // 2) - 1

				assert node.index == next_index

		return -1

	def free(self, start):
		node = self._root
		while node:
			if node.is_leaf and node.is_reserved:
				if start != node.start:
					return False

				# Coalescing.

				curr = node
				while curr:
					if (not curr.sibling) or curr.sibling.is_parent or curr.sibling.is_reserved:
						# We cut off access to descendants.
						# Python handles the garbage collection.
						curr.left = None
						curr.right = None

						while curr and curr.is_reserved:
							curr.unreserve()
							curr = curr.parent

						break
					curr = curr.parent

				return True
			else:
				if start < node.start + node.length // 2:
					node = node.left
				else:
					node = node.right
		return False

	def size(self, start):
		node = self._root
		while node:
			if node.is_leaf and node.is_reserved:
				if start != node.start:
					return -1
				return node.length
			else:
				assert node.is_parent or node.is_reserved
				if start < node.start + node.length // 2:
					node = node.left
				else:
					node = node.right
		return -1

	def __str__(self):
		return self._root.__str__()


########
# Tests
########


import pytest
import random


def _max_size(buddy):
	def traverse(node, nodes):
		if not node:
			return

		nodes.append(node)

		traverse(node.left, nodes)
		traverse(node.right, nodes)

	nodes = []
	traverse(buddy._root, nodes)

	max_size = 0
	for node in nodes:
		if node.is_reserved:
			continue
		max_size = max(max_size, node.length)

	return max_size


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

