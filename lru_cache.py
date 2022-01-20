"""LRU cache.

Solves https://leetcode.com/problems/lru-cache/

Solution is based on:
https://leetcode.com/problems/lru-cache/discuss/45926/Python-Dict-%2B-Double-LinkedList

A simpler solution uses an OrderedDict

Notes:
* Removing a node is easy, because of the prev and next pointers
* The dictionary goes from key to node, not from key to value
* The linked list node stores the key and the value for entry in the dictionary
"""

class Node:

	def __init__(self, k, v):
		self.key = k
		self.val = v
		self.prev = None
		self.next = None

class LRUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.key_to_node = dict()
        
        # Initialize doubly linked list
        # with dummy head and tail.
        # Nodes closer to the tail have been used
        # more recently.
        # The LRU is right after the dummy head.
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        # Remove the node from the list
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p

    def _add(self, node):
        # Inserts the node right before the tail
        p = self.tail.prev
        p.next = node
        self.tail.prev = node
        node.prev = p
        node.next = self.tail
        
    def get(self, key):
        if key not in self.key_to_node:
            return -1
        node = self.key_to_node[key]
        self._remove(node)
        self._add(node)
        return node.val

    def put(self, key, value):
        if key in self.key_to_node:
            self._remove(self.key_to_node[key])
        node = Node(key, value)
        self._add(node)
        self.key_to_node[key] = node
        if len(self.key_to_node) > self.capacity:
            # Remove the node right after the head.
            node = self.head.next
            self._remove(node)
            del self.key_to_node[node.key]