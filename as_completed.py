"""Implementation of simplified concurrent.futures.as_completed.

Sources:
* https://github.com/python/cpython/blob/main/Lib/concurrent/futures/_base.py
"""

import threading
import concurrent.futures
import random
import time
import numpy as np


class _AcquireFutures:

	def __init__(self, futures):
		self.futures = sorted(futures, key=id)

	def __enter__(self):
		for future in self.futures:
			future._condition.acquire()

	def __exit__(self, *args):
		for future in self.futures:
			future._condition.release()


class _Waiter:
	"""
	class Future:

		def set_result(self, result):
			...
			waiter.add_result(result)
			self._condition.notify_all()
			...
	"""

	def __init__(self):
		self.event = threading.Event()
		self.finished_futures = []
		self.lock = threading.Lock()

	def add_result(self, future):
		with self.lock:
			self.finished_futures.append(future)
			self.event.set()


def as_completed(futures):
	futures = set(futures)
	with _AcquireFutures(futures):
		finished = set([f for f in futures if f._state == "FINISHED"])
		pending = futures - finished
		waiter = _Waiter()
		for f in futures:
			f._waiters.append(waiter)

	finished = list(finished)

	while finished:
		yield finished.pop()

	while pending:
		# The same Waiter is added to each
		# future. If the event is set in any
		# of the futures, the wait is done
		# here.
		waiter.event.wait()

		with waiter.lock:
			finished_futures = waiter.finished_futures
			waiter.finished_futures = []
			waiter.event.clear()

		finished_futures.reverse()
		while finished_futures:
			f = finished_futures[-1]
			pending.remove(f)
			yield finished_futures.pop()

	for f in futures:
		with f._condition:
			f._waiters.remove(waiter)


def fn(i):
	time.sleep(random.random())
	return i


if __name__ == "__main__":
	print("as_completed from library:")
	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(fn, i) for i in range(10)]
		# If the loop below is in the context (as it is here),
		# then it returns in the order of completion.
		# 
		# If the loop is out of the context,
		# then the executor has shutdown. If shutdown has
		# wait set to True (the default), then all the workers will
		# have finished at that point. In that case, the order of
		# finished workers is given by:
		# fs = list(set([future for future in futures]))
		# while fs:
		#	f = fs.pop()
		#   print(f.result())
		for future in concurrent.futures.as_completed(futures):
			print(future.result())

	print("as_completed from scratch:")
	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(fn, i) for i in range(10)]
		for future in as_completed(futures):
			print(future.result())