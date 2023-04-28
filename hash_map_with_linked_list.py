"""Design a hash map with linked list.

Sources:
* https://leetcode.com/problems/design-hashmap/

See also:
* hash_table.py
"""

class Node:

	def __init__(self):
		self.key = None
		self.value = None
		self.next = None


class MyHashMap:

	def __init__(self):
		self.capacity = 10
		self.data = [None for _ in range(self.capacity)]

	def _hash(self, key):
		return key % self.capacity

	def put(self, key: int, value: int) -> None:
		new_node = Node()
		new_node.key = key
		new_node.value = value

		i = self._hash(key)
		node = self.data[i]

		if not node:
			self.data[i] = new_node
			return

		prev = None
		while node:
			if node.key == key:
				node.value = value
				return
			prev = node
			node = node.next

		prev.next = new_node

	def get(self, key: int) -> int:
		i = self._hash(key)
		node = self.data[i]
		while node:
			if node.key == key:
				return node.value
			node = node.next
		return -1

	def remove(self, key: int) -> None:
		i = self._hash(key)
		node = self.data[i]

		if not node:
			return

		prev = None
		while node:
			if node.key == key:
				if prev:
					prev.next = node.next
				else:
					self.data[i] = node.next
				return
			prev = node
			node = node.next
