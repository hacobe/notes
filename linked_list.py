"""
Sources:
* https://www.educative.io/edpresso/how-to-create-a-doubly-linked-list-in-python
"""

class Node:

	def __init__(self, data):
		self.data = data
		self.prev = None
		self.next = None

class DoublyLinkedList:

	def __init__(self):
		self.head = None
		self.tail = None

	def push_front(self, new_data):
		new_node = Node(new_data)
		new_node.next = self.head

		if self.head:
			self.head.prev = new_node
			self.head = new_node
		else:
			self.head = new_node
			self.tail = new_node

	def push_back(self, new_data):
		new_node = Node(new_data)
		new_node.prev = self.tail

		if self.tail:
			self.tail.next = new_node
			self.tail = new_node
		else:
			self.head = new_node 
			self.tail = new_node

	def pop_front(self):
		if self.head is None:
			raise ValueError("Empty list")
    
		temp = self.head
		temp.next.prev = None
		self.head = temp.next
		temp.next = None
		return temp.data

	def pop_back(self):
		if self.tail is None:
			raise ValueError("Empty list")
		temp = self.tail
		temp.prev.next = None
		self.tail = temp.prev
		temp.prev = None
		return temp.data

	def remove(self, data):
		node = self.head
		while node:
			if node.data == data:
				prev_node = node.prev
				next_node = node.next

				if prev_node:
					prev_node.next = next_node
				else:
					self.head = next_node

				if next_node:
					next_node.prev = prev_node
				else:
					self.tail = prev_node

				break

			node = node.next

	def __str__(self):
		node = self.head
		parts = []
		while node:
			parts.append(str(node.data))
			node = node.next
		return "->".join(parts)


if __name__ == "__main__":
	dll = DoublyLinkedList()
	dll.push_front(1)
	dll.push_front(2)
	dll.push_front(3)
	dll.push_front(4)
	dll.push_back(5)
	dll.push_back(6)
	print(dll)
	assert dll.__str__() == "4->3->2->1->5->6"
	assert dll.pop_front() == 4
	assert dll.pop_back() == 6
	print(dll)
	assert dll.__str__() == "3->2->1->5"
	dll.remove(2)
	print(dll)
	assert dll.__str__() == "3->1->5"
