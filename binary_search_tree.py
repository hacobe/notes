"""Binary search tree.

Sources:
* https://www.geeksforgeeks.org/binary-search-tree-set-1-search-and-insertion/
* https://www.geeksforgeeks.org/binary-search-tree-set-2-delete/
"""

class Node:
	def __init__(self, key):
		self.left = None
		self.right = None
		self.val = key


def search(root, key):
	if root is None or root.val == key:
		return root

	if root.val < key:
		return search(root.right, key)

	return search(root.left, key)


def insert(root, key):
	if root is None:
		return Node(key)
	else:
		if root.val == key:
			return root
		elif root.val < key:
			root.right = insert(root.right, key)
		else:
			root.left = insert(root.left, key)
	return root


def _minValueNode(node):
	current = node
	while current.left is not None:
		current = current.left
	return current


def deleteNode(root, key):
	if root is None:
		return root

	if key < root.val:
		root.left = deleteNode(root.left, key)
	elif key > root.val:
		root.right = deleteNode(root.right, key)
	else:
		if root.left is None:
			temp = root.right
			root = None
			return temp
		elif root.right is None:
			temp = root.left
			root = None
			return temp

		temp = _minValueNode(root.right)
		root.val = temp.val
		root.right = deleteNode(root.right, temp.val)

	return root


def _inorder(root, vals):
	if root:
		_inorder(root.left, vals)
		vals.append(root.val)
		_inorder(root.right, vals)

def inorder(root):
	vals = []
	_inorder(root, vals)
	return vals


def test_binary_search_tree():
	root = None
	root = insert(root, 50)
	root = insert(root, 30)
	root = insert(root, 20)
	root = insert(root, 40)
	root = insert(root, 70)
	root = insert(root, 60)
	root = insert(root, 80)
	assert inorder(root) == [20, 30, 40, 50, 60, 70, 80]

	root = deleteNode(root, 20)
	assert inorder(root) == [30, 40, 50, 60, 70, 80]

	root = deleteNode(root, 30)
	assert inorder(root) == [40, 50, 60, 70, 80]

	root = deleteNode(root, 50)
	assert inorder(root) == [40, 60, 70, 80]


if __name__ == "__main__":
	test_binary_search_tree()

