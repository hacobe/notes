"""Producer-Consumer

Notes:
* Put and get update the buffer, increment the buffer indices and increment the count.
  They don't access any locks or conditions.
 

Sources:
* Chapter 30 ("Condition Variables"), Operating Systems: Three Easy Pieces
"""
import threading

def put(value):
	global fill_ptr
	global MAX
	global count
	global buffer_

	buffer_[fill_ptr] = value
	fill_ptr = (fill_ptr + 1) % MAX
	count += 1

def get():
	global use_ptr
	global MAX
	global count
	global buffer_

	tmp = buffer_[use_ptr]
	use_ptr = (use_ptr + 1) % MAX
	count -= 1
	return tmp

def producer():
	global loops
	global mutex
	global empty
	global fill

	for i in range(loops):
		mutex.acquire()
		while count == MAX:
			empty.wait()
		put(i)
		fill.notify()
		mutex.release()

def consumer():
	global loops
	global mutex
	global empty
	global fill

	for i in range(loops):
		mutex.acquire()
		while count == 0:
			fill.wait()
		tmp = get()
		empty.notify()
		mutex.release()
		print(tmp)

if __name__ == "__main__":
	global MAX
	global fill_ptr
	global use_ptr
	global count
	global buffer_
	global loops
	global mutex
	global empty
	global fill
	MAX = 1
	fill_ptr = 0
	use_ptr = 0
	count = 0
	buffer_ = [0]
	loops = 5
	mutex = threading.Lock()
	empty = threading.Condition(mutex)
	fill = threading.Condition(mutex)

	producer_thread = threading.Thread(target=producer)
	consumer_thread = threading.Thread(target=consumer)
	producer_thread.start()
	consumer_thread.start()
	producer_thread.join()
	consumer_thread.join()