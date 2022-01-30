"""Implement a queue.

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

	def is_empty(self):
		return self.front is None

	def enqueue(self, new_data):
		new_node = Node(new_data)
		if not self.back:
			self.front = new_node
			self.back = new_node
			return
		node = self.back
		self.back = new_node
		node.next = self.back

	def dequeue(self):
		if self.is_empty():
			return
		node = self.front
		self.front = node.next

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
