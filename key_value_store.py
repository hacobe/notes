"""Key-value store.

This is an educational implementation of a key-value store.

Functionality:
* We do not implement a way to pop keys. One strategy is to
  append a special record that signals the database to ignore
  all previous records with the key in the text file.

Encoding:
* We use a text file instead of a binary file and
  we use character offsets instead of byte offsets
* We assume keys and values are strings
  (in a more realistic setting, values might be binary blobs)

Free space management:
* One strategy is to close the text file once it reaches a certain
  size and then start a new text file. Once the text file is closed,
  we can load it into memory, remove old keys (compaction) and write a
  new text file to disk in a background thread. When the new text file
  is ready, we can switch to using that new text file and delete the
  old file.
* This strategy can also involve merging text files after compaction
  and then writing the merged file.
* In this way, each text file is append-only if it has not reached the
  file limit or immutable if it has.

Why use an append-only log (i.e., write-ahead log)?
* Sequential writes are faster than random writes.
* It is easier to find the last consistent state of the database.
  Suppose we modified data in place and the computer crashes, then
  we may have a corrupted value for the record that we were modifying.
  In this case, what do we restore to? We don't know the original
  value of the record. In the append-only, we can throw out a partially
  completed record that doesn't have a checksum or doesn't match its
  checksum and restore from the last write.

Concurrency:
* Single writer, multiple readers
* A reader will always have a consistent view of the database.
  The reader may have to throw away an incomplete record at the end of the
  log and the reader will not see writes until it restarts. But it 
  doesn't have to wait for writers.

See also:
* log_segments_with_hash_index.md

Sources: 
* Chapter 3, Designing Data-Intensive Applications, pg. 70-75
* https://github.com/avinassh/py-caskdb/blob/master/disk_store.py
	* Reliable saving: https://github.com/avinassh/py-caskdb/blob/master/disk_store.py#L153
* https://github.com/python/cpython/blob/3.12/Lib/dbm/dumb.py
	* The Python `shelve` module is a wrapper around `dbm`
	  (https://github.com/python/cpython/blob/3.12/Lib/shelve.py)
	  (https://en.wikipedia.org/wiki/DBM_(computing))
	* "A 'shelf' is a persistent, dictionary-like object"
	* "The shelve module does not support concurrent read/write access to
	  shelved objects. (Multiple simultaneous read accesses are safe.)
	  When a program has a shelf open for writing, no other program should
	  have it open for reading or writing. Unix file locking can be used to
	  solve this, but this differs across Unix versions and requires knowledge
	  about the database implementation used."
	  (https://docs.python.org/3/library/shelve.html)
* https://github.com/avinassh/py-caskdb?tab=readme-ov-file
* https://stackoverflow.com/questions/1733619/writing-a-key-value-store
* https://web.archive.org/web/20240317201607/https://ayende.com/blog/4542/building-data-stores-append-only
"""
import os

class Database:

	def __init__(self, path):
		self._path = path
		
		if not os.path.exists(path):
			f = open(path, 'w')
			f.close()

		self._index = {}
		# We could construct a dictionary of key-value
		# pairs in memory, but that might take up a lot
		# of space, because values could be large.
		#
		# Instead, we construct a dictionary of
		# key-(pos, siz) pairs, where pos is the character
		# index of the value in the file and siz is the
		# number of characters in the value.
		# 
		# If a key appears multiple times in the file,
		# then we take the last one.
		offset = 0
		with open(self._path, 'r') as f:
			for line in f:
				i = 0
				while i < len(line) and line[i] != ",":
					i += 1
				assert i < len(line) and line[i] == ","
				key = line[:i]
				# :-1 to remove '\n'
				val = line[i+1:-1]
				pos = offset + i
				self._index[key] = (pos, len(val) - 1)
				offset += len(line)

	def __getitem__(self, key):
		assert isinstance(key, str)
		pos, siz = self._index[key]
		with open(self._path, 'r') as f:
			f.seek(pos)
			dat = f.read(siz)
		return dat

	def __setitem__(self, key, val):
		assert isinstance(key, str)
		assert isinstance(val, str)

		# Append a key-value pair to the end of the file.
		with open(self._path, "a") as f:
			pos = f.tell() + len(f"{key},")
			f.write(f"{key},{val}\n")

		self._index[key] = (pos, len(val))

if __name__ == "__main__":
	import tempfile
	with tempfile.NamedTemporaryFile() as f:
		db = Database(f.name)
		db["key1"] = "value1"
		db["key2"] = "foo"
		print(db._index)
		print(f"<{db['key1']}>")
		print(f"<{db['key2']}>")


