"""Minimal implementation of autograd.

Sources:
* https://github.com/karpathy/micrograd/blob/master/micrograd/engine.py
* https://github.com/minitorch/minitorch/tree/main/minitorch
* https://minitorch.github.io
"""

class Scalar:

	def __init__(self, data, children=()):
		self.data = data
		self.children = children
		self.grad = 0.
		self._backward = lambda: None

	def __add__(self, other):
		# We create the parent from its children.
		#
		#      parent
		#        +
		#      /   \
		#   self  other 
		parent = Scalar(
			data=self.data + other.data,
			children=(self, other))

		def _backward():
			self.grad += parent.grad
			other.grad += parent.grad
		self._backward = _backward

		return parent

	def __mul__(self, other):
		parent = Scalar(
			data=self.data * other.data,
			children=(self, other))

		def _backward():
			self.grad += other.data * parent.grad
			other.grad += self.data * parent.grad
		self._backward = _backward

		return parent	

	def backward(self):

		def dfs(u, visited, order):
			if u in visited:
				return
			visited.add(u)
			for v in u.children:
				dfs(v, visited, order)
			order.append(u)

		dfs_order = []
		visited = set()
		dfs(self, visited, dfs_order)
		topo_order = dfs_order[::-1]

		self.grad = 1.0
		for u in topo_order:
			u._backward()


if __name__ == "__main__":
	# c = a + b
	# dcda = 1
	# dcdb = 1
	a = Scalar(2)
	b = Scalar(3)
	c = a + b
	c.backward()
	assert a.grad == 1.0
	assert b.grad == 1.0

	# c = a * b
	# dcda = b
	# dcdb = a
	a = Scalar(2)
	b = Scalar(3)
	c = a * b
	c.backward()
	assert a.grad == 3.0
	assert b.grad == 2.0