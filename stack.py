"""Implement a stack.

Notes:
* When you push you make the new node the head
* When you pop you remove the head

Sources:
* https://www.geeksforgeeks.org/implement-a-stack-using-singly-linked-list/
"""

class Node:

	def __init__(self, data):
		self.data = data
		self.next = None


class Stack:

	def __init__(self):
		self.head = None

	def push(self, data):
		if not self.head:
			self.head = Node(data) 
			return 

		new_node = Node(data)
		new_node.next = self.head
		self.head = new_node

	def pop(self):
		node = self.head
		data = node.data
		self.head = self.head.next
		node = None
		return data

	def __str__(self):
		iternode = self.head
		s = []
		while iternode is not None:
			s.append(str(iternode.data))
			iternode = iternode.next
		return "->".join(s)


def test_stack():
	stack = Stack()
	stack.push(11)
	stack.push(22)
	stack.push(33)
	stack.push(44)
	assert stack.__str__() == "44->33->22->11"
	stack.pop()
	stack.pop()
	assert stack.__str__() == "22->11"


if __name__ == "__main__":
	test_stack()