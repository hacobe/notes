"""LRU cache.

Notes:
* We can solve the problem with an OrderedDict using the move_to_end and popitem(last=False) methods
* We could use collections.OrderedDict or build the OrderedDict from scratch.
* An OrderedDict consists of a dictionary from key to node and a doubly linked list
* We add a dummy node to the head and a dummy node to the tail in order to reduce the number of edge
  cases for linked list operations
* We have 2 helper methods: _remove_node_from_ll and _insert_node_into_ll_before_tail
* We need to define __init__, __len__, __contains__, __getitem__, __setitem__, move_to_end, popitem

Sources:
* Solves https://leetcode.com/problems/lru-cache/
* https://leetcode.com/problems/lru-cache/discuss/45926/Python-Dict-%2B-Double-LinkedList
"""

class Node:

    def __init__(self):
        self.key = None
        self.value = None
        self.next = None
        self.prev = None

class OrderedDict:

    def __init__(self):
        self.key_to_node = {}
        # Separate dummy nodes
        # (not the same node or else there will be a cycle)
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node_from_ll(self, node):
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p

    def _insert_node_into_ll_before_tail(self, node):
        p = self.tail.prev
        p.next = node
        self.tail.prev = node
        node.prev = p
        node.next = self.tail
    
    def __getitem__(self, key):
        node = self.key_to_node[key]
        return node.value

    def __setitem__(self, key, value):
        if key in self.key_to_node:
            node = self.key_to_node[key]
            node.value = value
            return

        node = Node()
        node.key = key
        node.value = value
        self.key_to_node[key] = node
        self._insert_node_into_ll_before_tail(node)

    def __len__(self):
        return len(self.key_to_node)

    def __contains__(self, key):
        return (key in self.key_to_node)

    def move_to_end(self, key):
        node = self.key_to_node[key]
        self._remove_node_from_ll(node)
        self._insert_node_into_ll_before_tail(node)

    def popitem(self, last):
        if last:
            raise NotImplementedError
        node = self.head.next
        self._remove_node_from_ll(node)
        self.key_to_node.pop(node.key)


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        value = self.cache[key]
        self.cache.move_to_end(key)
        return value
        

    def put(self, key: int, value: int) -> None:
        if (key not in self.cache) and (len(self.cache) == self.capacity):
            self.cache.popitem(last=False)
        self.cache[key] = value
        self.cache.move_to_end(key)