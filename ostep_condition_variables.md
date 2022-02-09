# OSTEP: Condition Variables

This is a summary of Chapter 30 ("Condition Variables") from “Operating Systems: Three Easy Pieces”.

## Introduction

Locks are not the only primitives we need to build concurrent programs: "In particular, there are many cases where a thread wishes to check whether a condition is true before continuing its execution. For example, a parent thread might wish to check whether a child thread has completed before continuing (this is often called a join())".

The program in Figure 30.1 motivates the need for condition variables. I translate that program into Python:

```python
import time
import threading


def child():
	time.sleep(1)
	print("child")
	# XXX how to indicate we are done?

if __name__ == "__main__":
	print("parent: begin")
	t = threading.Thread(target=child)
	t.start()
	# XXX how to wait for child?
	print("parent: end")
```

The program will output:

```
parent: begin
parent: end
child
```

But we want it to output:

```
parent: begin
child
parent: end
```

We could use a "spin-based approach" as follows (translation of Figure 30.2):

```python
def child():
	time.sleep(1)
	print("child")
	# XXX how to indicate we are done?
	global done
	done = 1

if __name__ == "__main__":
	print("parent: begin")
	global done
	done = 0
	t = threading.Thread(target=child)
	t.start()
	# XXX how to wait for child?
	while done == 0:
		pass  # spin
	print("parent: end")
```

But this approach wastes CPU cycles as the parent spins.

## Definition and Routines

A **condition variable** is "an explicit queue that threads can put themselves on when some state of execution
(i.e., some **condition**) is not as desired (by **waiting** on the condition); some other thread, when it changes said state, can then wake one (or more) of those waiting threads and thus allow them to continue (by **signaling** on the condition)."

Figure 30.3 shows how to solve the problem posed above with a condition variable. I translate it into Python:

```python
def child(condition, lock):
	time.sleep(1)
	print("child")
	# XXX how to indicate we are done?
	# thr_exit:
	lock.acquire()
	global done
	done = 1
	condition.notify()
	lock.release()

if __name__ == "__main__":
	global done
	done = 0

	print("parent: begin")
	lock = threading.Lock()
	condition = threading.Condition(lock)
	t = threading.Thread(target=child, args=(condition, lock))
	t.start()
	# XXX how to wait for child?
	# thr_join:
	lock.acquire()
	while done == 0:
		condition.wait()
	lock.release()
	print("parent: end")
```

A condition variable has 2 operations: wait() and notify() (notify() is called signal() in the textbook). wait() releases the lock and puts the thread that calls it to sleep. This is done atomically, i.e, the instructions that comprise wait() are executed together and cannot be interrupted. notify() is called when a thread wants to wake a sleeping thread.

To see how the program above works, consider 2 cases:
1. Parent creates the child thread, but continues executing. In this case, the parent acquires the lock, enters the while loop, releases the lock and goes to sleep. The child eventually runs, acquires the free lock, sets done to 1, wakes up the parent thread.
2. Parent creates the child thread and the child thread starts executing immediately. It "sets done to 1, calls signal to wake a sleeping thread (but there is none, so it just returns), and is done." The parent does not enter the while loop (done != 0) so it doesn't wait.

In the code above, I've simulated (1) by adding time.sleep(1) at the start of the child function. We can simulate (2) by moving the time.sleep(1) call to right after the child thread starts.

*Do we need the state variable?*

Below is a program without the state variable. Notice that time.sleep(1) is right after the child thread starts, so we are simulating case (2). This program works fine in case (1). However, in case (2), the child thread calls notify() and there is no thread to wake up, so the thread continues and exits. Then, the parent thread calls wait() and it waits indefinitely, because there is no notify() call coming.

```
def child(condition, lock):
	print("child")
	# XXX how to indicate we are done?
	# thr_exit:
	lock.acquire()
	condition.notify()
	lock.release()

if __name__ == "__main__":
	global done
	done = 0

	print("parent: begin")
	lock = threading.Lock()
	condition = threading.Condition(lock)
	t = threading.Thread(target=child, args=(condition, lock))
	t.start()
	time.sleep(1)
	# XXX how to wait for child?
	# thr_join:
	lock.acquire()
	condition.wait()
	lock.release()
	print("parent: end")
```

*Do we need the lock?*

The implementation of Condition requires a lock, so we can't define a Condition without one, but supposing we could define a Condition without a lock then we could run into a race condition: "Specifically, if the parent calls
thr_join() and then checks the value of done, it will see that it is 0 and thus try to go to sleep. But just before it calls wait to go to sleep, the parent is interrupted, and the child runs. The child changes the state variable
done to 1 and signals, but no thread is waiting and thus no thread is woken. When the parent runs again, it sleeps forever, which is sad."

## The Producer/Consumer (Bounded Buffer) Problem

Here's the setup for the Producer/Consumer problem: "Imagine one or more producer threads and one or more consumer
threads. Producers generate data items and place them in a buffer; consumers grab said items from the buffer and consume them in some way."

Here are some real world examples that use a bounded buffer:
* "a multi-threaded web server, a producer puts HTTP requests into a work
queue (i.e., the bounded buffer); consumer threads take requests out of
this queue and process them."
* "A bounded buffer is also used when you pipe the output of one program into another, e.g., grep foo file.txt | wc -l. This example runs two processes concurrently; grep writes lines from file.txt with the string foo in them to what it thinks is standard output; the UNIX shell redirects the output to what is called a UNIX pipe (created by the
pipe system call). The other end of this pipe is connected to the standard input of the process wc, which simply counts the number of lines in the input stream and prints out the result. Thus, the grep process is the
producer; the wc process is the consumer; between them is an in-kernel bounded buffer; you, in this example, are just the happy user."

### Incomplete initial code

We start out with some code where the shared buffer is just a single integer. This code will throw an assertion error if you run it. It's just meant to present a kind of scaffolding that we will continually improve on working towards the solution.

```python
import threading

def put(value):
	global count
	global buffer_

	assert count == 0
	count = 1
	buffer_ = value

def get():
	global count
	global buffer_

	assert count == 1
	count = 0
	return buffer_

def producer():
	global loops
	for i in range(loops):
		put(i)

def consumer():
	while True:
		tmp = get()
		print(tmp)

if __name__ == "__main__":
	global count
	global buffer_
	global loops
	count = 0
	buffer_ = [0]
	loops = 5
	producer_thread = threading.Thread(target=producer)
	consumer_thread = threading.Thread(target=consumer)
	producer_thread.start()
	consumer_thread.start()
	producer_thread.join()
	consumer_thread.join()
```

In this code: "The put() routine assumes the buffer is empty (and checks this with an assertion), and then simply puts a value into the shared buffer and marks it full by setting count to 1. The get() routine does the opposite, setting the buffer to empty (i.e., setting count to 0) and returning the value". Also, we have "a producer that puts an integer into the shared buffer loops number of times, and a consumer that gets the data out of that shared buffer (forever), each time printing out the data item it pulled from the shared buffer".

### A Broken Solution

The following code works when there is just one producer thread and one consumer thread, but breaks when there are more than one of either thread.

```python
import threading

def put(value):
	global count
	global buffer_

	assert count == 0
	count = 1
	buffer_ = value

def get():
	global count
	global buffer_

	assert count == 1
	count = 0
	return buffer_

def producer():
	global loops
	global mutex
	global cond

	for i in range(loops):
		mutex.acquire()  # p1
		if count == 1:   # p2
			cond.wait()  # p3
		put(i)			 # p4
		cond.notify()	 # p5
		mutex.release()	 # p6

def consumer():
	global loops
	global mutex
	global cond

	for i in range(loops):
		mutex.acquire()  # c1
		if count == 0:   # c2
			cond.wait()  # c3
		tmp = get()      # c4
		cond.notify()    # c5
		mutex.release()  # c6
		print(tmp)

if __name__ == "__main__":
	global count
	global buffer_
	global loops
	global mutex
	global cond
	
	count = 0
	buffer_ = [0]
	loops = 5
	mutex = threading.Lock()
	cond = threading.Condition(mutex)

	producer_thread = threading.Thread(target=producer)

	num_consumer_threads = 1
	consumer_threads = [threading.Thread(
		target=consumer) for _ in range(num_consumer_threads)]
	producer_thread.start()
	for i in range(len(consumer_threads)):
		consumer_threads[i].start()
	producer_thread.join()
	for i in range(len(consumer_threads)):
		consumer_threads[i].join()
```

If I run this code with num_consumer_threads = 2, then "assert count == 1" in get() throws an error. Here is an example execution that has the same behavior:

![ostep_figure30.9](/img/ostep_figure30.9.png)

Here is the crux of the problem: "after the producer woke $T_{c1}$, but before $T_{c1}$ ever ran, the state of the bounded buffer changed (thanks to $T_{c2}$). Signaling a thread only wakes them up; it is thus a hint that the state
of the world has changed (in this case, that a value has been placed in the buffer), but there is no guarantee that when the woken thread runs, the state will still be as desired."

An implementation where signaling a thread only wakes it up and doesn't immediately start running that thread is called **Mesa semantics** and stands in contrast to **Hoare semantics** where signaling a thread immediately starts executing that thread. Almost all systems use Mesa semantics.

### Better, But Still Broken: While, Not If

We can fix the particular error described above by replacing the if statement in the producer and the if statement in the consumer with a while statement in each. With that change, the "consumer $T_{c1}$ wakes up and (with the lock held) immediately re-checks the state of the shared variable (c2). If the buffer is empty at that point, the consumer simply goes back to sleep (c3)."

But the implementation with while loops still has a bug. As before, if I run the code with 1 producer thread and 1 consumer thread, then it works fine. But this time if I run the code with num_consumer_threads = 2, then it prints the expected output (the numbers 0 through 4 each on their own line), but then does not exit.

Here is an example execution that has the same behavior:

![ostep_figure30.11](/img/ostep_figure30.11.png)

The crux of the problem is that the program can get into a situation where one of the consumers calls notify() to wake one thread from sleeping, but both the other consumer and the producer are sleeping and if it happens to wake the consumer all 3 threads will end up sleeping.

### The Single Buffer Producer/Consumer Solution

The solution is to use 2 condition variables:

```python
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
```

## Covering Conditions

This section discusses an example where you can notify all other threads to wake up calling pthread_cond_broadcast() in C (or notify_all() in Python).

## Sources

* Chapter 30 ("Condition Variables"), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/threads-cv.pdf accessed on 2/2/2022