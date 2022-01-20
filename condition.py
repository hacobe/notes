"""
Output:
Thread 1 acquired lock
Thread 1 about to release lock and wait
Thread 2 acquired lock
Thread 2 notified all
Thread 2 released lock
Thread 1 done waiting and reacquired lock
Thread 1 released lock
"""
import threading
import time


def thread1(lock, cond):
    lock.acquire()
    print("Thread 1 acquired lock")
    print("Thread 1 about to release lock and wait")
    cond.wait()
    print("Thread 1 done waiting and reacquired lock")
    lock.release()
    print("Thread 1 released lock")

def thread2(lock, cond):
    lock.acquire()
    print("Thread 2 acquired lock")
    cond.notify_all()
    print("Thread 2 notified all")
    lock.release()
    print("Thread 2 released lock")
   

if __name__ == "__main__": 
    lock = threading.Lock()
    cond = threading.Condition(lock)
    t1 = threading.Thread(target=thread1, args=(lock, cond))
    t2 = threading.Thread(target=thread2, args=(lock, cond))
    t1.start()
    t2.start()
    t1.join()
    t2.join()