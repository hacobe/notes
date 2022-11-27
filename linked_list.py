"""
Sources:
* https://leetcode.com/problems/design-linked-list/
* https://www.geeksforgeeks.org/linked-list-set-1-introduction/
* https://www.geeksforgeeks.org/linked-list-set-2-inserting-a-node/
* https://www.geeksforgeeks.org/linked-list-set-3-deleting-node/
"""

class Node:

	def __init__(self, val, next=None):
		self.val = val
		self.next = next


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
		node = Node(val)
		node.next = self.head
		self.head = node

	def addAtTail(self, val: int) -> None:
		# Handles the case of an empty list
		new_node = Node(val)
		if not self.head:
			self.head = new_node
			return

		node = self.head
		prev_node = None
		while node:
			prev_node = node
			node = node.next
		prev_node.next = new_node

	def addAtIndex(self, index: int, val: int) -> None:
		if index == 0:
			self.addAtHead(val)
			return

		node = self.head
		prev_node = None
		i = 0
		while node:
			if i == index:
				new_node = Node(val)
				prev_node.next = new_node
				new_node.next = node
				return
			prev_node = node
			node = node.next
			i += 1

		# "If index equals the length of the linked list, the node will be appended to the end of the linked list"
		if i == index:
			new_node = Node(val)
			prev_node.next = new_node

	def deleteAtIndex(self, index: int) -> None:
		if index == 0:
			self.head = self.head.next
			return
		node = self.head
		prev_node = None
		i = 0
		while node:
			if i == index:
				prev_node.next = node.next
				return
			prev_node = node
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