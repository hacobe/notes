"""Simplified implementaiton of ThreadPoolExecutor.

This implementation excludes several features:
* waiters
* cancel
* timeout
* set_running_or_notify_cancel
	* if it's in state cancelled then set state to cancelled_and_notified and return false
	* if it's in state pending then set state to running and return true
	* otherwise raise an error
* set_running_or_notify_cancel in _worker
	* call this to see if we should run the future
* _global_shutdown_lock
* shutdown lock
* https://github.com/python/cpython/commit/c13d454e84aabe80fbc7763491bdfb3c924016fe
	* "Should be called periodically to prevent memory leaks in scenarios such as:"
* callbacks
* shutdown arguments

Sources:
* https://github.com/python/cpython/blob/main/Lib/concurrent/futures/_base.py
* https://github.com/python/cpython/blob/main/Lib/concurrent/futures/thread.py
"""
import queue
import threading


PENDING = "PENDING"
RUNNING = "RUNNING"
FINISHED = "FINISHED"


class Future:

	def __init__(self):
		self._state = PENDING
		self._condition = threading.Condition()
		self._result = None
		self._exception = None

	def set_result(self, result):
		with self._condition:
			self._result = result
			self._state = FINISHED
			self._condition.notify_all()

	def set_exception(self, exception):
		with self._condition:
			self._exception = exception
			self._state = FINISHED
			self._condition.notify_all()

	def result(self, timeout=None):
		with self._condition:
			# Why 2 if statements in the original code?
			while self._state == PENDING:
				self._condition.wait(timeout)
		if self._exception:
			raise self._exception
		else:
			return self._result


def _worker(work_queue, idle_semaphore):
	while True:
		work_item = work_queue.get(block=True)
		
		if work_item is None:
			break

		future, fn, args = work_item

		try:
			result = fn(*args)
			future.set_result(result)
		except BaseException as e:
			future.set_exception(e)

		idle_semaphore.release()


class ThreadPoolExecutor:

	def __init__(self, max_workers=32):
		self._max_workers = max_workers
		self._work_queue = queue.SimpleQueue()
		self._idle_semaphore = threading.Semaphore(0)
		self._threads = set()

	def submit(self, fn, *args):
		f = Future()
		work_item = (f, fn, args)
		self._work_queue.put(work_item)
		self._adjust_thread_count()
		return f

	def _adjust_thread_count(self):
		if self._idle_semaphore.acquire(timeout=0):
			return

		num_threads = len(self._threads)
		# < because we're adding a thread
		if num_threads < self._max_workers:
			t = threading.Thread(target=_worker, args=(self._work_queue, self._idle_semaphore))
			t.start()
			self._threads.add(t)

	def map(self, fn, *iterables):
		futs = [self.submit(fn, *args) for args in zip(*iterables)]

        # Yield must be hidden in closure so that the line above
        # is executed without requiring the iteration through the map
        # result.
		def result_iterator():
			# We reverse in the map method because we pop from futures.
			# We don't iterate through futures because we're changing its size. 
			futs.reverse()

			while futs:
				fut = futs.pop()
				try:
					yield fut.result()
				except:
					yield None

		return result_iterator()

	def shutdown(self):
		for _ in range(len(self._threads)):
			self._work_queue.put(None)

		for t in self._threads:
			t.join()


import time

def fn(i):
	time.sleep(1)
	print(f"running {i}")
	return i


if __name__ == "__main__":
	executor = ThreadPoolExecutor()
	future = executor.submit(fn, 10)
	executor.shutdown()

	print("----")

	executor = ThreadPoolExecutor()
	result_iterator = executor.map(fn, range(4))

	for result in result_iterator:
		print(result)

	executor.shutdown()
