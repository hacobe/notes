"""Implement a bounded blocking queue.

Sources:
* https://github.com/python/cpython/blob/8d21aa21f2cbc6d50aab3f420bb23be1d081dac4/Lib/Queue.py#L200
* https://github.com/python/cpython/blob/8d21aa21f2cbc6d50aab3f420bb23be1d081dac4/Lib/test/test_queue.py
* https://leetcode.com/problems/design-bounded-blocking-queue/
"""
import threading
import collections


class BoundedBlockingQueue(object):

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.unfinished_tasks = 0
        self.queue = collections.deque()
        self.lock = threading.Lock()
        # All these Condition objects share the same lock
        # When acquired is called for any one of these,
        # then it locks all of them
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        self.all_tasks_done = threading.Condition(self.lock)

    def enqueue(self, element: int):
        self.not_full.acquire()
        while len(self.queue) == self.capacity:
            self.not_full.wait()
        self.queue.append(element)
        self.unfinished_tasks += 1
        self.not_empty.notify()
        self.not_full.release()
        
    def dequeue(self):
        self.not_empty.acquire()
        while len(self.queue) == 0:
            self.not_empty.wait()
        element = self.queue.popleft()
        self.not_full.notify()
        self.not_empty.release()
        return element

    def size(self):
        self.lock.acquire()
        n = len(self.queue)
        self.lock.release()
        return n
    
    def task_done(self):
        self.all_tasks_done.acquire()
        try:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
        finally:
            self.all_tasks_done.release()
            
    def join(self):
        self.all_tasks_done.acquire()
        try: # catches possible ValueError in task_done
            while self.unfinished_tasks:
                self.all_tasks_done.wait()  # wait on the notify in task_done when it reaches 0 tasks
        finally:
            self.all_tasks_done.release()
