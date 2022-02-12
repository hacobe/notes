# OSTEP: Locked data structures

This is a summary of Chapter 29 ("Locked Data Structures") of "Operating Systems: Three Easy Pieces".

## Concurrent Counters

Figure 29.1 presents a non-thread-safe counter. I translate the program into Python:

```python
class Counter:

	def __init__(self):
		self.value = 0

	def increment(self):
		self.value += 1

	def decrement(self):
		self.value -= 1

	def get(self):
		return self.value
```

Figure 29.2 presents a thread-safe counter. I translate the program into Python:

```python
import threading

class ThreadSafeCounter:

	def __init__(self):
		self.value = 0
		self.lock = threading.Lock()

	def increment(self):
		self.lock.acquire()
		self.value += 1
		self.lock.release()

	def decrement(self):
		self.lock.acquire()
		self.value -= 1
		self.lock.release()

	def get(self):
		self.lock.acquire()
		ret = self.value
		self.lock.release()	
		return ret
```

This works, but scales very poorly with the number of threads: "Whereas a single thread can complete the million counter updates in a tiny amount of time (roughly 0.03 seconds), having two threads each update the counter one million times concurrently leads to a massive slowdown (taking over 5 seconds!). It only gets worse with more threads."

Figure 29.4 is a counter that scales better with the number of threads at the cost of some accuracy in the count. I translate it into Python:

```python
import threading

class ScalableApproxCounter:

	def __init__(self, num_cpus, threshold):
		self.num_cpus = num_cpus
		self.threshold = threshold

		self.global_count = 0
		self.global_lock = threading.Lock()
		self.local_counts = [0] * num_cpus
		self.local_locks = [threading.Lock()] * num_cpus

	def update(self, thread_id, amt):
		cpu = thread_id % self.num_cpus
		self.local_locks[cpu].acquire()
		self.local_counts[cpu] += amt
		if self.local_counts[cpu] >= self.threshold:
			self.global_lock.acquire()
			self.global_count += self.local_counts[cpu]
			self.global_lock.release()
			self.local_counts[cpu] = 0
		self.local_locks[cpu].release()

	def get(self):
		self.global_lock.acquire()
		ret = self.global_count
		self.global_lock.release()
		return ret
```

## Concurrent Linked Lists

Figures 29.7 and 29.8 present 2 versions of a thread-safe linked list. Figure 29.8 answers the question: "can we rewrite the insert and lookup routines [of the program in Figure 29.7] to remain correct under concurrent insert but avoid the case where the failure path also requires us to add the call to unlock?" The issue has to do with malloc, so is not relevant to a Python implementation, so I just start with Figure 29.8 and translate it into a Python program:

```python
import threading

class Node:

	def __init__(self, key):
		self.key = key
		self.next = None

class LinkedList:

	def __init__(self):
		self.head = None
		self.lock = threading.Lock()

	def insert(self, key):
		node = Node(key)
		self.lock.acquire()
		node.next = self.head
		self.head = node
		self.lock.release()

	def lookup(self, key):
		rv = -1
		self.lock.acquire()
		curr = self.head
		while curr:
			if curr.key == key:
				rv = 0
				break
			curr = curr.next
		self.lock.release()
		return rv

if __name__ == "__main__":
	ll = LinkedList()
	ll.insert(5)
	ll.insert(3)
	ll.insert(10)
	assert ll.lookup(4) == -1
	assert ll.lookup(3) == 0
```

The chapter mentions that this approach doesn't scale that well and discusses one possible solution called hand-over-hand locking or lock coupling, where "Instead of having a single lock for the entire
list, you instead add a lock per node of the list. When traversing the list, the code first grabs the next node's lock and then releases the current node's lock". However, the chapter notes that "in practice, it is hard to make such a structure faster than the simple single lock approach, as the overheads of acquiring and releasing locks for each node of a list traversal is prohibitive."

It seems that this section is more about the following design principle (which is not well-illustrated in Python): "be wary of control flow changes that lead to function returns, exits, or other similar error conditions that halt the execution of a function. Because many functions will begin by acquiring a lock, allocating some memory, or doing other similar stateful operations, when errors arise, the code has to undo all of the state before returning, which is errorprone. Thus, it is best to structure code to minimize this pattern."

## Concurrent Queues

This section has a brief discussion of "a slightly more concurrent queue" than the one you get by just adding a lock. The idea is to have a lock for the head and a lock for the tail with the goal of enabling "concurrency of enqueue and dequeue operations. In the common case, the enqueue routine will only access the tail lock, and
dequeue only the head lock."

## Concurrent Hash Table

This section discusses a concurrent hash table, which is just like a regular hash table except that we use the linked list implementation in Figure 29.8. It scales very well, because "instead of having a single
lock for the entire structure, it uses a lock per hash bucket (each of which is represented by a list). Doing so enables many concurrent operations to take place."

```python
class HashTable:

	def __init__(self):
		self.num_buckets = 5
		self.lists = [LinkedList() for _ in range(self.num_buckets)]

	def insert(self, key):
		return self.lists[key % self.num_buckets].insert(key)

	def lookup(self, key):
		return self.lists[key % self.num_buckets].lookup(key)
```

## Summary

* "be careful with acquisition and release of locks around control flow changes"
* "enabling more concurrency does not necessarily increase performance"
* "performance problems should only be remedied once they exist"

## Sources

* Chapter 29 ("Locked Data Structures"), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks-usage.pdf accessed on 2/3/2022
