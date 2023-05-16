"""Implement a linked list.

Sources:
* https://leetcode.com/problems/design-linked-list/
* https://www.geeksforgeeks.org/linked-list-set-1-introduction/
* https://www.geeksforgeeks.org/linked-list-set-2-inserting-a-node/
* https://www.geeksforgeeks.org/linked-list-set-3-deleting-node/
"""

class Node:

	def __init__(self, val):
		self.val = val
		self.next = None

class MyLinkedList:

	def __init__(self):
		self.head = None

	def get(self, index):
		node = self.head
		i = 0
		while node:
			if i == index:
				return node.val
			node = node.next
			i += 1
		return -1

	def addAtHead(self, val: int) -> None:
		new_node = Node(val)
		new_node.next = self.head
		self.head = new_node

	def addAtTail(self, val: int) -> None:
		new_node = Node(val)
		if not self.head:
			self.head = new_node
			return
		prev = None
		node = self.head
		while node:
			prev = node
			node = node.next
		prev.next = new_node

	def addAtIndex(self, index: int, val: int) -> None:
		if index == 0:
			self.addAtHead(val)
			return

		new_node = Node(val)
		prev = None
		node = self.head
		i = 0
		while node:
			if i == index:
				prev.next = new_node
				new_node.next = node
				return
			prev = node
			node = node.next
			i += 1
		if index == i:
			prev.next = new_node
			new_node.next = node

	def deleteAtIndex(self, index: int) -> None:
		if index == 0:
			self.head = self.head.next
			return

		prev = None
		node = self.head
		i = 0
		while node:
			if i == index:
				prev.next = node.next
				return
			prev = node
			node = node.next
			i += 1

	def __str__(self):
		node = self.head
		parts = []
		while node:
			parts.append(str(node.val))
			node = node.next
		return "->".join(parts)


if __name__ == "__main__":
	ll = MyLinkedList()
	ll.addAtTail(6)
	ll.addAtHead(7)
	ll.addAtHead(1)
	ll.addAtTail(4)
	ll.addAtIndex(2, 8)
	print(ll)
	assert ll.__str__() == "1->7->8->6->4"
	ll.deleteAtIndex(3)
	print(ll)
	assert ll.__str__() == "1->7->8->4"