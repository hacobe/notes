"""Implement a stack.

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

	def is_empty(self):
		return self.head is None

	def push(self, data):
		if self.head is None:
			self.head = Node(data)  
		else:
			newnode = Node(data)
			newnode.next = self.head
			self.head = newnode

	def pop(self):
		if self.is_empty():
			return None
		else:
			poppednode = self.head
			self.head = self.head.next
			poppednode.next = None
			return poppednode.data

	def peek(self):
		if self.is_empty():
			return None
		else:
			return self.head.data

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
	assert stack.peek() == 44
	stack.pop()
	stack.pop()
	assert stack.__str__() == "22->11"
	assert stack.peek() == 22


if __name__ == "__main__":
	test_stack()