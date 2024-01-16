"""Educational implementation of a linked listed memory allocator.

See also:
* memory_manager.py
* buddy_memory_manager.py
* ostep_free_space_management.md

Sources:
* https://codereview.stackexchange.com/questions/282967/doubly-linked-list-first-fit-free-list-malloc-free-in-python
"""
class Node:

	def __init__(self, start, end):
		self.start = start
		self.end = end
		self.prev = None
		self.next = None


class LinkedListMemoryManager:

	def __init__(self, capacity):
		self.capacity = capacity
		self.start_to_size = {}
		self.head = Node(0, capacity)

	def malloc(self, size):
		assert size > 0
		node = self.head
		while node:
			if node.end - node.start >= size:
				break
			node = node.next

		if not node:
			return -1

		start = node.start
		self.start_to_size[start] = size

		if node.end - node.start == size:
			# Remove the node from linked list.
			if node.prev:
				node.prev.next = node.next
			if node.next:
				node.next.prev = node.prev
			if self.head == node:
				self.head = node.next
		else:
			node.start += size

		return start

	def free(self, start):
		if start not in self.start_to_size:
			return False

		size = self.start_to_size[start]

		new_node = Node(start, start + size)

		# Find where in the linked list to add the new node.
		# We'll insert the new_node between prev and node.
		prev = None
		node = self.head
		while node and node.start < start:
			prev = node
			node = node.next

		# Add the new node to the linked list.
		if not self.head:
			self.head = new_node
		if prev:
			prev.next = new_node
			new_node.prev = prev
		if node:
			node.prev = new_node
			new_node.next = node
		if self.head == node:
			self.head = new_node

		# Coalesce new_node and new_node.next.
		if new_node.next and new_node.next.start == new_node.end:
			# Extend new_node.
			new_node.end += new_node.next.end - new_node.next.start
			# Remove a in (new_node <-> a <-> b)
			new_node.next = new_node.next.next
			if new_node.next:
				new_node.next.prev = new_node

		# Coalesce new_node.prev and new_node.
		if new_node.prev and new_node.prev.end == new_node.start:
			# Extend new_node.prev.
			new_node.prev.end += new_node.end - new_node.start
			# Remove a in (new_node.prev <-> a <-> b)
			new_node.prev.next = new_node.next
			if new_node.prev.next:
				new_node.prev.next.prev = new_node.prev

		del self.start_to_size[start]

		return True

	# Methods for testing.

	@property
	def free_list(self):
		result = []
		node = self.head
		while node:
			result.append([node.start, node.end])
			node = node.next
		return result
