"""Implement a stack.

Notes:
* When you push you make the new node the head
* When you pop you remove the head

Sources:
* https://leetcode.com/problems/min-stack/
* https://www.geeksforgeeks.org/implement-a-stack-using-singly-linked-list/
"""

class Node:

	def __init__(self, val, min_val, next=None):
		self.val = val
		self.min_val = min_val
		self.next = next


class MinStack:

	def __init__(self):
		self.head = None

	def push(self, val):
		min_val = float('inf')
		if self.head:
			min_val = self.head.min_val
		min_val = min(val, min_val)
		node = Node(val, min_val)
		node.next = self.head
		self.head = node

	def pop(self):
		self.head = self.head.next

	def top(self):
		return self.head.val

	def getMin(self):
		return self.head.min_val

	def __str__(self):
		iternode = self.head
		s = []
		while iternode is not None:
			s.append(str(iternode.val))
			iternode = iternode.next
		return "->".join(s)


def test_stack():
	stack = MinStack()
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