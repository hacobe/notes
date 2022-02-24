# Multi-threaded web crawler

## Single-threaded web crawler

```python
import collections

def crawl(startUrl, htmlParser):
    queue = collections.deque([startUrl])
    visited = {startUrl}
    while queue:
        url = queue.popleft()
        neighbor_urls = htmlParser.getUrls(url)
        for neighbor_url in neighbor_urls:
            if neighbor_url in visited:
            	continue
            visited.add(neighbor_url)
            queue.append(neighbor_url)
    return list(visited)
```

## Incorrect multi-threaded web web crawler

This code is basically multiple threads running the code we used for the single-threaded crawler.

```python
import collections
import threading

class Crawler:

	def __init__(self, htmlParser):
		self.htmlParser = htmlParser
		self.visited = set()
		self.queue = collections.deque()

	def _worker(self):
		while self.queue:
			url = self.queue.popleft()
			neighbor_urls = self.htmlParser.getUrls(url)
			for neighbor_url in neighbor_urls:
				if neighbor_url in self.visited:
					continue
				self.visited.add(neighbor_url)
				self.queue.append(neighbor_url)

	def crawl(self, startUrl):
		self.visited.add(startUrl)
		self.queue.append(startUrl)

		num_threads = 8
		threads = []
		for _ in range(num_threads):
			threads.append(threading.Thread(target=self._worker))

		for thread in threads:
			thread.start()

		for thread in threads:
			thread.join()

		return list(self.visited)
```

Note that `deque` is thread-safe.[^1] But the code still has 2 problems:
1. Threads may exit early possibly with exceptions thrown and even resulting in a singled-threaded process
2. A url can get visited twice

### Problem #1: Threads may exit early

The problem is that we can have the first thread pop a url from the queue making it empty and then before it gets a chance to add the links for that url, the OS interrupts and switches to another thread, which sees that the queue is empty and exits.

Consider the following execution of 2 threads:

thread 1           				| thread 2
-------------------------------------------------
queue is not empty 				|
pops startUrl      				| 
calls getUrls      				|
			       				| queue is empty (or it tries)
			                    | exits 
add a url to the queue          |
[now we only have 1 thread]     |

Here's another execution:

thread 1           				| thread 2
-------------------------------------------------
								| queue is not empty
queue is not empty 				|
pops startUrl      				| 
calls getUrls      				|
			       				| attempts to pop from the queue and throws an error
			                    | exits 
add a url to the queue          |
[now we only have 1 thread]     |

### Problem #2: A url can get visited twice

The problem is that link 1 and link 2 might link to the same page. One thread, which has extracted the page from processing link 1, checks that the page is not in visited and proceeds, but before it can get added to visited it is interrupted by another thread, which has extracted the page from processing link 2.

Consider the execution below of 2 threads (described in detail in handwritten/race_condition_url_visited_twice_web_crawler_20220216.pdf). Suppose that we start with queue = [b, c] and visited = {a, b, c} (we can imagine sequential execution up to that point within one of the threads).

thread 1           		  | thread 2
-------------------------------------------------
queue is not empty 		  |
pops a url from the queue | 
getUrls(b)     	          |
d not in visited          |
						  | queue is not empty
						  | pop url
						  | getUrls(c)
						  | d not visited
						  | add d to visited
						  | add d to queue
add d to visited          |
add d to queue            |

At the end of the execution, the queue will be [d, d] ensuring that d gets visited twice.

## Multi-threaded web crawler with blocking queue

Here are the fixes:

1. Threads may exit early
	1. Have the while loop go forever without explicit breaking.
	2. Use Python's blocking queue to block on get when the queue is empty instead of throwing an error
	3. Use the task tracking features of Python's blocking queue (`task_done` and `join`) to signal when the work has actually been completed.
	4. After the work has been completed, break explicitly by enqueuing a stop item for each thread.
2. A url can get visited twice
	1. Wrap checking for visited and adding to visited in a lock to ensure atomic execution.

The shared variables that get updated are self.visited and self.queue. Each queue operation is synchronized with a lock internal to the queue. And we've wrapped the checking and modification of self.visited with a lock.

```python
import collections
import threading
from queue import Queue

class Crawler:

	def __init__(self, htmlParser):
		self.htmlParser = htmlParser
		self.visited = set()
		self.queue = Queue()
		self.lock = threading.Lock()

	def _worker(self):
		while True:
			url = self.queue.get()
			if url is None:
				break
			neighbor_urls = self.htmlParser.getUrls(url)
			for neighbor_url in neighbor_urls:
				with self.lock:
					if neighbor_url in self.visited:
						continue
					self.visited.add(neighbor_url)
					self.queue.put(neighbor_url)
			self.queue.task_done()

	def crawl(self, startUrl):
		self.visited.add(startUrl)
		self.queue.put(startUrl)

		num_threads = 8
		threads = []
		for _ in range(num_threads):
			threads.append(threading.Thread(target=self._worker))

		for thread in threads:
			thread.start()

		self.queue.join()

		for _ in range(num_threads):
			self.queue.put(None)

		for thread in threads:
			thread.join()

		return list(self.visited)
```

## Blocking queue

```python
import collections
import threading

class Queue:

	def __init__(self):
		self.queue = collections.deque()
		self.lock = threading.Lock()
		self.not_empty = threading.Condition(self.lock)
		self.all_tasks_done = threading.Condition(self.lock)
		self.unfinished_tasks = 0

	def get(self):
		with self.lock:
			while len(self.queue) == 0:
				self.not_empty.wait()
			item = self.queue.popleft()
		return item

	def put(self, item):
		with self.lock:
			self.queue.append(item)
			self.unfinished_tasks += 1
			self.not_empty.notify()

	def task_done(self):
		with self.lock:
			self.unfinished_tasks -= 1
			if self.unfinished_tasks == 0:
				self.all_tasks_done.notify_all()

	def join(self):
		with self.lock:
			while self.unfinished_tasks != 0:
				self.all_tasks_done.wait()
```

### Why do condition variables need to be in while statements?

At a high-level, a thread can check the condition, the condition can be true at that point, but by the time the thread wakes up and re-acquires the lock, then the condition has changed. Also, sometimes a thread can woken up spuriously, but I think that's more rare.

At a medium-level:
* Thread 1 goes to sleep waiting for the queue not to be empty
* Thread 2 acquires the lock to put a new item in the queue
* Thread 3 calls get() but gets blocked waiting for the lock
* Thread 2 wakes up Thread 1, but Thread 3 grabs the lock first and takes the item that was added to the queue
* Thread 1 is finally able to reacquire the lock, but now tries to pop from an empty queue 

At a low-level, suppose that we just used an if statement instead of a while loop and consider the following execution. We start with the queue = [b, c], visited = {a, b, c} and unfinished_tasks = 2. In other words, we've finished processing URL a, but not URL b and c that were linked to from a.

thread 1           		          | thread 2						| thread 3
----------------------------------|---------------------------------|-------------------------------------
get() returns b 		          |									|
parses b [finds no links]         | 								|
task_done()   	                  |									|
				                  | get() returns					|
				                  | parses c [finds link d]			|
get()			              	  |                                 |
	if len(queue) == 0 [true] 	  |									|
		not_empty.wait()	   [1]|									|
						  	  	  | put(d)						    |
						  	  	  | 	acquires lock 			 [2]|
						  	  	  |     adds d to the queue         |
						  	  	  |                                 | get()
						  	  	  |									|	blocks on acquiring lock       [3]
						      	  |		not_empty.notify()		 [4]| 
						  	  	  |              					|
	thread wakes up 		  	  |                                 |
	blocks on reacquiring lock [5]|                                 |
							      |		releases lock            [6]|
						  	      | 								| 	acquires lock                  [7]
						  	      |									| 	removes d from the queue       [8]
						  	      | 								| 	not_empty.notify()
                          	      |                                 | 	releases lock
	reacquires lock          	  | 								|
	pops from empty            [9]|									|     

The numbers in brackets corresponds to the list numbers in this [post](http://web.archive.org/web/20210118112846/http://256stuff.com/gray/docs/misc/producer_consumer_race_conditions/).

## Practical tips

How to analyze concurrent programs:
* Imagine an adversarial scheduler.
* Draw a picture with a column for each thread and a column for each the important state to keep track of. The state column is what happens after the instruction in the same row is executed.
* Imagine sequential execution within one thread to get to the point of execution that you want to analyze.
* Think of what parts of the code you want to execute atomically, i.e., without interruption

Questions that come up for the multi-threaded web crawler:
* When do you know that you're done?
* Is the wait call wrapped in a while loop?
* Will the wait call wait forever?
* Will every sleeping thread eventually get a signal to wake up?
* Are there no returns, continues, or errors in between lock acquire and release?
* Is every url only visited once?
* Is the lock held for when signalling?

Problems that come up for the multi-threaded web crawler:
* threads exit early reducing the program to a single threaded one
* infinite loop from interrupted update to the counter
	* adding to a counter is not an atomic operation
	* https://stackoverflow.com/questions/1717393/is-the-operator-thread-safe-in-python
* visting the same url twice because checking visited and adding to visited are not executed atomically
* wasting time in a while loop waiting for the queue to be empty (we'd rather cede control when it's empty)
* the condition not being true anymore if you use an if statement rather than while loop

These [notes](http://web.mit.edu/6.826/www/notes/HO14.pdf) define "Easy concurrency" as:
* "Every shared variable must be protected by a lock. A variable is shared if it is touched by
more than one thread..."
* "You must hold the lock for a shared variable before you touch the variable..."
* "If you want an atomic operation on several shared variables that are protected by different
locks, you must not release any locks until you are done..."

Some of the tips from OSTEP:
* **Use a disassembler** to see what instructions make up e.g., an addition
* Some tips related to "There are a number of small but important things to remember when
you use the POSIX thread library (or really, any thread library)", including "Always use condition variables to signal between threads"
* Think about concurrency as a **malicious scheduler**
* **More concurrency isn't necessarily faster**: "If the scheme you design adds a lot of overhead (for example, by acquiring and releasing locks frequently, instead of once), the fact that it is more concurrent may not be important...All of that said, there is one way to really know: build both alternatives (simple but less concurrent, and complex but more concurrent) and measure how they do."
* **Be wary of locks and control flow**: "...be wary of control flow changes that lead to function returns,
exits, or other similar error conditions that halt the execution of a function. Because many functions will begin by acquiring a lock, allocating some memory, or doing other similar stateful operations, when errors arise, the code has to undo all of the state before returning, which is error-prone."
* **Always hold the lock while signalling**: "The example above shows a case where you must hold the lock for correctness; however, there are some other cases where it is likely OK not to, but probably is something you should avoid...The converse of this tip, i.e., hold the lock when calling wait, is not just a tip, but rather mandated by the semantics of wait, because wait always (a) assumes the lock is held when you call it, (b) releases said lock when putting the caller to sleep, and (c) re-acquires the lock just before returning..."
* **Use while (not if) for conditions**: "When checking for a condition in a multi-threaded program, using a while loop is always correct; using an if statement only might be, depending on the semantics of signaling. Thus, always use while and your code will behave as expected. Using while loops around conditional checks also handles the case where spurious wakeups occur."
* **Enforce locking ordering by lock address**

## See also

* web_crawler_concurrent_with_queue.py
* web_crawler_concurrent_without_queue.py
* blocking_queue.py

## Further questions

* **Does signalling have to be done inside the lock?** Generally it's a good idea and I don't think hurts, but is it strictly necessary? There is some discussion of it in the [chapter](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf) on condition variables in OSTEP starting with "In this example, we imagine that one does not need to hold a lock in order to signal and wait. What problem could occur here?" However, I think that discussion is when you pretend that condition variables don't require a lock for waiting and you show what happens if you don't lock around waiting and signaling.
* Relatedly, **why do condition variables require a lock?** I think it's just understanding this key paragraph from the same chapter: "The issue here is a subtle race condition. Specifically, if the parent calls thr join() and then checks the value of done, it will see that it is 0 and thus try to go to sleep. But just before it calls wait to go to sleep, the parent is interrupted, and the child runs. The child changes the state variable done to 1 and signals, but no thread is waiting and thus no thread is woken. When the parent runs again, it sleeps forever, which is sad."
* **How is a condition variable implemented?**

## Sources

* https://home.cs.colorado.edu/~kena/classes/5828/s10/lectures/10_eightsimplerules.pdf
* https://homes.cs.washington.edu/~djg/teachingMaterials/spac/sophomoricParallelismAndConcurrency.pdf
* http://web.mit.edu/6.826/www/notes/HO14.pdf
* https://pages.cs.wisc.edu/~remzi/OSTEP/

## Footnotes

[^1:] "Deques support thread-safe, memory efficient appends and pops from either side of the deque..." (https://docs.python.org/3/library/collections.html#collections.deque)
