"""Hash table.

Sources:
* https://coderbook.com/@marcus/how-to-create-a-hash-table-from-scratch-in-python/

See also:
* hash_map_with_linked_list.py
"""

class HashTable(object):

	def __init__(self, length=4):
		self.array = [None] * length

	def _hash(self, key):
		length = len(self.array)
		return hash(key) % length

	def add(self, key, value):
		index = self._hash(key)
		if self.array[index] is not None:
			found = False
			for kvp in self.array[index]:
				if kvp[0] == key:
					kvp[1] = value
					found = True
					break
			if found:
				self.array[index].append([key, value])
		else:
			self.array[index] = []
			self.array[index].append([key, value])

	def get(self, key):
		index = self._hash(key)
		if self.array[index] is None:
			raise KeyError()
		else:
			for kvp in self.array[index]:
				if kvp[0] == key:
					return kvp[1]
			raise KeyError()


if __name__ == "__main__":
	hash_table = HashTable()
	hash_table.add("foo", "bar")
	assert hash_table.get("foo") == "bar"