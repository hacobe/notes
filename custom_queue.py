"""Implement a queue.

Notes:
* Don't forget to check assign back to be empty if front is in dequeue
* Queue has a front and a back pointer, while the basic Linked List only has a head pointer
* When you enqueue, you make the new node the back
* When you dequeue, you remove the front
* Think of front and back as pointers to nodes in the linked list rather than as nodes themselves

Sources:
* https://www.geeksforgeeks.org/queue-linked-list-implementation/
"""

class Node:

	def __init__(self, data):
		self.data = data
		self.next = None


class Queue:

	def __init__(self):
		self.front = None
		self.back = None

	def enqueue(self, new_data):
		new_node = Node(new_data)

		if not self.back:
			self.front = new_node
			self.back = new_node
			return

		self.back.next = new_node
		self.back = new_node

	def dequeue(self):
		assert self.front

		self.front = self.front.next

		if not self.front:
			self.back = None


def test_queue():
	q = Queue()
	q.enqueue(10)
	q.enqueue(20)
	q.dequeue()
	q.dequeue()
	q.enqueue(30)
	q.enqueue(40)
	q.enqueue(50) 
	q.dequeue()  
	assert q.front.data == 40
	assert q.back.data == 50


if __name__ == "__main__":
	test_queue()
