"""Producer-Consumer

Notes:
* Put and get update the buffer, increment the buffer indices and increment the count.
  They don't access any locks or conditions.
 
See also:
* bounded_blocking_queue.py

Sources:
* Chapter 30 ("Condition Variables"), Operating Systems: Three Easy Pieces
"""
import threading

def put(value):
	global put_ptr
	global MAX
	global count
	global buffer_

	buffer_[put_ptr] = value
	put_ptr = (put_ptr + 1) % MAX
	count += 1

def get():
	global get_ptr
	global MAX
	global count
	global buffer_

	tmp = buffer_[get_ptr]
	get_ptr = (get_ptr + 1) % MAX
	count -= 1
	return tmp

def producer():
	global loops
	global lock
	global not_empty
	global not_full

	for i in range(loops):
		lock.acquire()
		while count == MAX:
			not_full.wait()
		put(i)
		not_empty.notify()
		lock.release()

def consumer():
	global loops
	global lock
	global not_empty
	global not_full

	for i in range(loops):
		lock.acquire()
		while count == 0:
			not_empty.wait()
		tmp = get()
		not_full.notify()
		lock.release()
		print(tmp)

if __name__ == "__main__":
	global MAX
	global put_ptr
	global get_ptr
	global count
	global buffer_
	global loops
	global lock
	global not_empty
	global not_full
	MAX = 1
	put_ptr = 0
	get_ptr = 0
	count = 0
	buffer_ = [0]
	loops = 5
	lock = threading.Lock()
	not_empty = threading.Condition(lock)
	not_full = threading.Condition(lock)

	producer_thread = threading.Thread(target=producer)
	consumer_thread = threading.Thread(target=consumer)
	producer_thread.start()
	consumer_thread.start()
	producer_thread.join()
	consumer_thread.join()