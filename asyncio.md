# asyncio

## Motivation

Consider a client interacting with a server:

```python
import multiprocessing
import socket
import time

HOST = "127.0.0.1"
SERVER_PORT = 8000

def handle_client_request(sock):
	request, (host, port) = sock.recvfrom(1024)  # blocks until it receives a message
	time.sleep(1)
	response = b"response for " + request
	sock.sendto(response, (host, port))

def server():
	# The server spins up 2 processes. Each of these processes waits for a request from the client,
	# sends back a response and then exits.
	#
	# For simplicity, imagine that the server has 2 cores, that each process runs on a separate
	# core and that the server only has to do CPU work in order to prepare a response to a request.
	# In this way, the server can clearly handle the 2 requests in parallel.
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	sock.bind((HOST, SERVER_PORT))
	p0 = multiprocessing.Process(target=handle_client_request, args=(sock,))
	p1 = multiprocessing.Process(target=handle_client_request, args=(sock,))
	p0.start()
	p1.start()
	p0.join()
	p1.join()
	sock.close()

def execute_api_call(request):
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	sock.sendto(request, (HOST, SERVER_PORT))
	response, _ = sock.recvfrom(1024)  # blocks until it receives a message
	sock.close()
	return response

def client():
	start_time = time.time()
	responses = [
		execute_api_call(b"request0"),
		execute_api_call(b"request1")
	]
	print(responses)
	print(time.time() - start_time)

def main():
	p_server = multiprocessing.Process(target=server)
	p_server.start()
	time.sleep(0.1)  # hack to let the server start receiving before the client starts
	client()
	p_server.join()

if __name__ == "__main__":
	main()
```

The client sends the first request to the server, the server takes about a second to prepare the response and then the client receives the response. The client then repeats the same steps for the second request. It takes about 2 seconds to complete both requests.

To speed this up, we could modify the client as follows:

```python
def client():
	start_time = time.time()
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

	sock.sendto(b"request0", (HOST, SERVER_PORT))
	sock.sendto(b"request1", (HOST, SERVER_PORT))

	responses = [
		sock.recvfrom(1024)[0],
		sock.recvfrom(1024)[0]
	]
	print(responses)

	sock.close()
	print(time.time() - start_time)
```

The client sends both requests first, the server prepares both responses in parallel, the client receives the first response that is ready and then the other response. It takes about 1 second to complete both requests.

If we wanted to keep the code that sends a request and receives a response encapsulated in the `execute_api_call` function while maintaining performance, we could use multithreading:

```python
import threading

def execute_api_call(request, responses):
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	sock.sendto(request, (HOST, SERVER_PORT))
	response, _ = sock.recvfrom(1024)  # blocking its thread until it receives a message
	sock.close()
	responses.append(response)

def client():
	start_time = time.time()

	responses = []
	t0 = threading.Thread(target=execute_api_call, args=(b"request0", responses))
	t0.start()
	t1 = threading.Thread(target=execute_api_call, args=(b"request1", responses))
	t1.start()

	t0.join()
	t1.join()
	print(responses)

	print(time.time() - start_time)
```

Alternatively, we could use asynchronous I/O:

```python
import asyncio

async def execute_api_call(request):
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	sock.sendto(request, (HOST, SERVER_PORT))
	# If the `recvfrom` call is blocking, then `sock_recvfrom` won't be able
	# to suspend execution to let another function run.
	sock.setblocking(False)
	response, _ = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
	sock.close()
	return response

async def client():
	start_time = time.time()

	t0 = asyncio.create_task(execute_api_call(b"request0"))
	t1 = asyncio.create_task(execute_api_call(b"request1"))

	responses = [
		await t0,
		await t1
	]
	print(responses)

	print(time.time() - start_time)

def main():
	p_server = multiprocessing.Process(target=server)
	p_server.start()
	time.sleep(0.1)  # let the server start receiving before the client starts
	asyncio.run(client())
	p_server.join()
```

(As an aside, if the `execute_api_call` coroutines shared a socket instead of creating one on each request, then you would need to use `asyncio.Lock` to avoid hangs.)

## Usage

A **coroutine** is a function that can suspend and later resume its execution. The built-in Python keyword `async` denotes a Python function as a coroutine making that explicit to the programmer. The built-in Python keyword `await` blocks the calling coroutine until some condition has been met. While the coroutine is waiting, another coroutine can run. The `asyncio` library implements a scheduler that coordinates switching between coroutines. The library exposes mechanisms for the programmer to provide input on scheduling. For example,  `await asyncio.get_event_loop().sock_recvfrom(...)` informs the scheduler to block the coroutine until the provided socket has received a message. `asyncio.create_task(...)` informs the scheduler to start the provided task soon. It also returns a handle, e.g., `t0`, which the caller can then use in an `await` statement, e.g., `await t0`, in order to block the coroutine until the task completes. The scheduler starts executing when `asyncio.run(...)` is called.

In rough analogy to Python's `threading` library:

| threading concept | threading command | asyncio command |
| ----------------- | ----------------- | --------------- |
| Create a thread and start running it | `thread = threading.Thread(...)`<br>`t.start()` | `task = asyncio.create_task(...)` |
| Block on completion of a child thread | `thread.join()` | `await task` |
| Block self on socket receiving a message | e.g., `select.select(...)` | e.g., `await loop.sock_recvfrom(...)`
| Scheduling | OS thread scheduler  | user-space scheduler executed by `asyncio.run(...)` |

Unlike multithreading, asynchronous I/O can run many functions concurrently in a single thread avoiding the overhead of spinning up threads, switching between threads and tearing down threads.

## How does it work?

An **iterator** is an instance of a class that defines an `__iter__` method, which returns itself, and a `__next__` method, which either returns a value or raises a `StopIteration` exception. For example:

```python
class MyIterator:

	def __iter__(self):
		self.i = 0
		return self

	def __next__(self):
		if self.i == 3:
			raise StopIteration
		j = self.i
		self.i += 1
		return j

iterator = MyIterator()
for item in iterator:
	print(item)
```

At the start of the for loop, the `__iter__` method is called. At each iteration, the `__next__` method is called until the `StopIteration` exception is raised at which point the loop breaks.

A **generator** is a function that returns an iterator. We define a generator using `yield`. For example:

```python
def my_generator():
	i = 0
	while True:
		if i == 3:
			return
		yield i
		i += 1

iterator = my_generator()
for item in iterator:
	print(item)
```

At the start of the for loop, the code up to the first `yield` statement in the generator is executed. At each iteration, the value of each `yield` statement is returned until the function returns at which point the loop breaks. We can think of a generator as convenient way to define an iterator, where the compiler does the work of translating from the generator to an iterator.

We can also define a generator using `yield from`, which enables us to nest generators. For example:

```python
def my_subgenerator():
	i = 0
	while True:
		if i == 3:
			return
		yield i
		i += 1

def my_generator():
	yield from my_subgenerator()

iterator = my_generator()
for item in iterator:
	print(item)
```

We can combine iterators in the sense of iterating through each of them one after the other as follows:

```python
def run(iterators):
	for iterator in iterators:
		for item in iterator:
			pass

def abc():
	print("A")
	yield
	print("B")
	yield
	print("C")

def xyz():
	print("X")
	yield
	print("Y")
	yield
	print("Z")

run([abc(), xyz()])
```

The code above prints:

```
A
B
C
X
Y
Z
```

We can also interleave iterators as follows:

```python
import collections

def run(iterators):
	ready = collections.deque(iterators)
	while ready:
		iterator = ready.popleft()
		try:
			next(iterator)
			ready.append(iterator)
		except StopIteration:
			pass

def abc():
	print("A")
	yield
	print("B")
	yield
	print("C")

def xyz():
	print("X")
	yield
	print("Y")
	yield
	print("Z")

run([abc(), xyz()])
```

The code above prints:

```
A
X
B
Y
C
Z
```

We now have the tools to reproduce some of the basic functionality of the `asyncio` library with `yield from` instead of `await` and our own customer scheduler.

```python
import collections
import heapq
import time

class Scheduler:

	def __init__(self):
		self._current = None
		self._ready = collections.deque()
		self._sleeping = []  # heap
		self._seq_no = 0  # used to break ties

	def add_iterator(self, iterator):
		self._ready.append(iterator)

	def sleep(self, delay):
		deadline = time.time() + delay
		heapq.heappush(self._sleeping, (deadline, self._seq_no, self._current))
		self._current = None
		self._seq_no += 1
		yield  # the caller will suspend here

	def run(self):
		while self._ready or self._sleeping:
			if not self._ready:
				deadline, _, iterator = heapq.heappop(self._sleeping)
				delta = deadline - time.time()
				if delta > 0:
					time.sleep(delta)
				self._ready.append(iterator)

			self._current = self._ready.popleft()
			try:
				next(self._current)
				if self._current:  # not sleep
					self._ready.append(self._current)
			except StopIteration:
				pass

_SCHEDULER = Scheduler()

class Task:

	def __init__(self):
		self._result = None
		self._done = False

	def done(self, result):
		self._result = result
		self._done = True

	def wait(self):
		while not self._done:
			yield from _SCHEDULER.sleep(0)  # cede control back to the scheduler
		return self._result

class myasyncio:

	@staticmethod
	def run(iterator):
		_SCHEDULER.add_iterator(iterator)
		_SCHEDULER.run()

	@staticmethod
	def sleep(delay):
		return _SCHEDULER.sleep(delay)

	@staticmethod
	def create_task(iterator):
		task = Task()

		def wrapped():
			result = yield from iterator
			task.done(result)

		_SCHEDULER.add_iterator(wrapped())

		return task.wait()

# Example 1

def main():
    print('hello')
    yield from myasyncio.sleep(1)
    print('world')

myasyncio.run(main())

# Example 2

def say_after(delay, what):
    yield from myasyncio.sleep(delay)
    print(what)

def main():
    start_time = time.time()
    yield from say_after(1, 'hello')
    yield from say_after(2, 'world')
    print(time.time() - start_time)

myasyncio.run(main())

# Example 3

def say_after(delay, what):
	yield from myasyncio.sleep(delay) 
	print(what)

def main():
	start_time = time.time()
	t0 = myasyncio.create_task(say_after(1, 'hello'))
	t1 = myasyncio.create_task(say_after(2, 'goodbye'))
	yield from t0
	yield from t1
	print(time.time() - start_time)

myasyncio.run(main())
```

We can add more functionality to reproduce our original client-server example:

```python
import collections
import heapq
import multiprocessing
import select
import socket
import time

HOST = "127.0.0.1"
SERVER_PORT = 8000

class Scheduler:

	def __init__(self):
		self._current = None
		self._ready = collections.deque()
		self._waiting = collections.defaultdict(collections.deque)
		self._sleeping = []  # heap
		self._seq_no = 0  # break ties

	def add_iterator(self, iterator):
		self._ready.append(iterator)

	def sleep(self, delay):
		deadline = time.time() + delay
		heapq.heappush(self._sleeping, (deadline, self._seq_no, self._current))
		self._current = None
		self._seq_no += 1
		yield  # the caller will suspend here

	def sock_recvfrom(self, sock, bufsize):
		self._waiting[sock].append(self._current)
		self._current = None
		yield
		return sock.recvfrom(bufsize)

	def run(self):
		while self._ready or self._waiting or self._sleeping:
			if not self._ready:
				if self._sleeping:
					deadline, _, iterator = self._sleeping[0]
					timeout = deadline - time.time()
					if timeout < 0:
						timeout = 0
				else:
					timeout = None

				can_read, _, _ = select.select(self._waiting, [], [], timeout)
				for sock in can_read:
					iterator = self._waiting[sock].pop()
					if not self._waiting[sock]:
						self._waiting.pop(sock)
					self._ready.append(iterator)

				now = time.time()
				while self._sleeping:
					deadline, _, _ = self._sleeping[0]
					if now > deadline:
						self._ready.append(heapq.heappop(self._sleeping)[-1])
					else:
						break

			self._current = self._ready.popleft()
			try:
				next(self._current)
				if self._current:
					self._ready.append(self._current)
			except StopIteration:
				pass

_SCHEDULER = Scheduler()

class Task:

	def __init__(self):
		self._result = None
		self._done = False

	def done(self, result):
		self._result = result
		self._done = True

	def wait(self):
		while not self._done:
			yield from _SCHEDULER.sleep(0)  # cede control back to the scheduler
		return self._result

class myasyncio:

	@staticmethod
	def run(iterator):
		_SCHEDULER.add_iterator(iterator)
		_SCHEDULER.run()

	@staticmethod
	def sleep(delay):
		return _SCHEDULER.sleep(delay)

	@staticmethod
	def create_task(iterator):
		task = Task()

		def wrapped():
			result = yield from iterator
			task.done(result)

		_SCHEDULER.add_iterator(wrapped())

		return task.wait()

	@staticmethod
	def sock_recvfrom(sock, bufsize):
		return _SCHEDULER.sock_recvfrom(sock, bufsize)

def handle_client_request(sock):
	request, (host, port) = sock.recvfrom(1024)  # blocks until it receives a message
	time.sleep(1)
	response = b"response for " + request
	sock.sendto(response, (host, port))

def server():
	# The server spins up 2 processes. Each of these processes waits for a request from the client,
	# sends back a response and then exits.
	#
	# For simplicity, imagine that the server has 2 cores, that each process runs on a separate
	# core and that the server only has to do CPU work in order to prepare a response to a request.
	# In this way, the server can clearly handle the 2 requests in parallel.
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	sock.bind((HOST, SERVER_PORT))
	p0 = multiprocessing.Process(target=handle_client_request, args=(sock,))
	p1 = multiprocessing.Process(target=handle_client_request, args=(sock,))
	p0.start()
	p1.start()
	p0.join()
	p1.join()
	sock.close()

def execute_api_call(request):
	sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	sock.sendto(request, (HOST, SERVER_PORT))
	# If the `recvfrom` call is blocking, then `sock_recvfrom` won't be able
	# to suspend execution to let another function run.
	sock.setblocking(False)
	response, _ = yield from myasyncio.sock_recvfrom(sock, 1024)
	sock.close()
	return response

def client():
	start_time = time.time()

	t0 = myasyncio.create_task(execute_api_call(b"request0"))
	t1 = myasyncio.create_task(execute_api_call(b"request1"))

	response0 = yield from t0
	response1 = yield from t1
	responses = [
		response0,
		response1
	]
	print(responses)

	print(time.time() - start_time)

def main():
	p_server = multiprocessing.Process(target=server)
	p_server.start()
	time.sleep(0.1)  # hack to let the server start receiving before the client starts
	myasyncio.run(client())
	p_server.join()

if __name__ == "__main__":
	main()
```

## Sources

* https://docs.python.org/3/library/asyncio.html
* [Build Your Own Async](https://www.youtube.com/watch?v=Y4Gt3Xjd7G8)
* https://gist.github.com/dabeaz/f86ded8d61206c757c5cd4dbb5109f74

## Additional sources

* https://stackoverflow.com/questions/49005651/how-does-asyncio-actually-work
* https://tenthousandmeters.com/blog/python-behind-the-scenes-12-how-asyncawait-works-in-python/
* https://news.ycombinator.com/item?id=40281139
* https://vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/