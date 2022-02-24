"""Binary search tree.

Sources:
* https://www.geeksforgeeks.org/binary-search-tree-set-1-search-and-insertion/
* https://www.geeksforgeeks.org/binary-search-tree-set-2-delete/
* https://leetcode.com/problems/delete-node-in-a-bst/discuss/93374/Simple-Python-Solution-With-Explanation
"""

class Node:
	def __init__(self, val):
		self.left = None
		self.right = None
		self.val = val


def search(root, key):
	if (not root) or (root.val == key):
		return root

	if key <= root.val:
		return search(root.left, key)

	return search(root.right, key)


def insert(root, key):
	if not root:
		return Node(key)

	if key <= root.val:
		root.left = insert(root.left, key)
	else:
		root.right = insert(root.right, key)

	return root


def _min_value_node(root):
	assert root
	node = root
	while node.left:
		node = node.left
	return node


def remove(root, key):
	if not root:
		return root

	if key < root.val:
		root.left = remove(root.left, key)
	elif key > root.val:
		root.right = remove(root.right, key)
	else:
		# At this point, root is the node that
		# we want to remove. The question is what
		# to replace it with.
		if not root.right:
			return root.left
		elif not root.left:
			return root.right

		# At this point, we know the node we want to replace
		# has a left child and a right child.
		# We replace the node with node that has the min value in the
		# right subtree and then we remove that node with min value
		# from the right subtree.
		min_value_node_in_right_subtree = _min_value_node(root.right)
		root.val = min_value_node_in_right_subtree.val
		root.right = remove(root.right, min_value_node_in_right_subtree.val)

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

	root = remove(root, 20)
	assert inorder(root) == [30, 40, 50, 60, 70, 80]

	root = remove(root, 30)
	assert inorder(root) == [40, 50, 60, 70, 80]

	root = remove(root, 50)
	assert inorder(root) == [40, 60, 70, 80]


if __name__ == "__main__":
	test_binary_search_tree()

