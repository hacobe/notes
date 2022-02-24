import collections
import time
import threading

def thread():
	queue = collections.deque()
	while True:
		x = queue.popleft()

if __name__ == "__main__":
	t1 = threading.Thread(target=thread)
	t2 = threading.Thread(target=thread)
	t1.start()
	t2.start()
	time.sleep(0.5)
	t1.join()
	t2.join()