"""
Notes:
* Interleave the locks

Sources:
* https://medium.com/swlh/getting-started-with-concurrency-in-python-part-ii-deadlocks-the-producer-consumer-model-gil-ae28afec3e7e

Output:

A acquired lock1
A acquired lock2
AAA
A released lock1
A released lock2

A acquired lock1
A acquired lock2
AAA
A released lock1
A released lock2

B acquired lock2
A acquired lock1
[Stalls here with B waiting A to release lock1 and A waiting for B to release lock2]
"""
import threading

def fnA(lock1, lock2):
	while True:
		lock1.acquire()
		print("A acquired lock1")
		lock2.acquire()
		print("A acquired lock2")
		print("AAA")
		lock1.release()
		print("A released lock1")
		lock2.release()
		print("A released lock2")

def fnB(lock1, lock2):
	while True:
		lock2.acquire()
		print("B acquired lock2")
		lock1.acquire()
		print("B acquired lock1")
		print("BBB")
		lock2.release()
		print("B released lock2")
		lock1.release()
		print("B released lock2")


if __name__ == "__main__":
	lock1 = threading.Lock()
	lock2 = threading.Lock()
	threadA = threading.Thread(target=fnA, args=(lock1, lock2), daemon=True)
	threadB = threading.Thread(target=fnB, args=(lock1, lock2), daemon=True)
	threadA.start()
	threadB.start()
	threadA.join()
	threadB.join()
