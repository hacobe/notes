"""
Sources:
* https://www.geeksforgeeks.org/linked-list-set-1-introduction/
* https://www.geeksforgeeks.org/linked-list-set-2-inserting-a-node/
* https://www.geeksforgeeks.org/linked-list-set-3-deleting-node/
"""

class Node:

	def __init__(self, data):
		self.data = data
		self.next = None

class LinkedList:

	def __init__(self):
		self.head = None

	def push_front(self, new_data):
		new_node = Node(new_data)
		new_node.next = self.head
		self.head = new_node

	def push_back(self, new_data):
		new_node = Node(new_data)
		if not self.head:
			self.head = new_node
			return

		node = self.head
		while node.next:
			node = node.next

		node.next = new_node

	def insert_after(self, prev_node, new_data):
		assert prev_node
		new_node = Node(new_data)
		node = prev_node.next
		prev_node.next = new_node
		new_node.next = node

	def remove(self, data):
		if not self.head:
			return

		node = self.head
		if node.data == data:
			self.head = node.next
			node = None
			return

		prev = node
		node = node.next
		while node: 
			if node.data == data: 
				prev.next = node.next
				node = None
				return
			prev = node
			node = node.next

	def __str__(self):
		node = self.head
		parts = []
		while node:
			parts.append(str(node.data))
			node = node.next
		return "->".join(parts)


if __name__ == "__main__":
	ll = LinkedList()
	ll.push_back(6)
	ll.push_front(7)
	ll.push_front(1)
	ll.push_back(4)
	ll.insert_after(ll.head.next, 8)
	print(ll)
	assert ll.__str__() == "1->7->8->6->4"
	ll.remove(6)
	print(ll)
	assert ll.__str__() == "1->7->8->4"