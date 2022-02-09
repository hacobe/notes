# OSTEP: Semaphores

This is a summary of Chapter 31 ("Semaphores") of "Operating Systems: Three Easy Pieces".

## Semaphores: A Definition

A **semaphore** is an object with an integer value. The user set the initial value of this integer when initializing the semaphore. It also has two routines associated with it that modify this integer value after initialization. In the POSIX standard, these routines are called sem_wait() and sem_post(). Here are their definitions from Figure 31.2:

```
int sem_wait(sem_t *s) {
	decrement the value of semaphore s by one
	wait if value of semaphore s is negative
}

int sem_post(sem_t *s) {
	increment the value of semaphore s by one
	if there are one or more threads waiting, wake one
}
```

In Python, sem_wait() is called acquire() and sem_post() is called release().

## Binary Semaphores (Locks)

We can use a semaphore as a lock if we set the initial value of the semaphore to 1. The section walks through an example of using a semaphore as a lock.

## Semaphores For Ordering

We can also use a semaphore as a way to order actions similar to how we used condition variables. Figure 31.6 gives an example. I translate the program into Python:

```python
import threading

def child():
	global sem
	print("child")
	sem.release()

if __name__ == "__main__":
	global sem
	sem = threading.Semaphore(0)

	print("parent: begin")
	t = threading.Thread(target=child)
	t.start()
	sem.acquire()  # wait here for child
	print("parent: end")
```

The section also traces through this program.

## The Producer/Consumer (Bounded Buffer) Problem

This section describes a solution to the Producer/Consumer problem using semaphores. See the post on condition variables for another solution.

## Reader-Writer Locks

This section describes the implementation of a Reader / Writer lock. This particular implementation "works (as desired), but does have some negatives, especially when it comes to fairness. In particular, it would be relatively easy for readers to starve writers." 

## The Dining Philosophers

Here is the basic setup for the Dining Philosophers problem:

"The basic setup for the problem is this (as shown in Figure 31.14): assume there are five 'philosophers' sitting around a table. Between each pair of philosophers is a single fork (and thus, five total). The philosophers each have times where they think, and don’t need any forks, and times where they eat. In order to eat, a philosopher needs two forks, both the one on their left and the one on their right."

In other words, each philosopher $p$ runs the following loop:

```
while (1) {
	think();
	get_forks(p);
	eat();
	put_forks(p);
}
```

And the challenge is to "write the routines get forks() and put forks() such that there is no deadlock, no philosopher starves and never gets to eat, and concurrency is high (i.e., as many philosophers can eat at the same time as possible)."

For the different candidate solutions, we define 2 helper functions:

```
int left(int p) { return p; }
int right(int p) { return (p + 1) % 5; }
```

We also initialize a semaphore for each fork:

```
sem t forks[5].
```

### Broken solution

```
void get_forks(int p) {
	sem_wait(&forks[left(p)]);
	sem_wait(&forks[right(p)]);
}

void put_forks(int p) {
	sem_post(&forks[left(p)]);
	sem_post(&forks[right(p)]);
}
```

The problem with this solution is deadlock: "If each philosopher happens to grab the fork on their left before any philosopher can grab the fork on their right, each will be stuck holding one fork and waiting for another, forever. Specifically, philosopher 0 grabs fork 0, philosopher 1 grabs fork 1, philosopher 2 grabs fork 2, philosopher 3 grabs fork 3, and philosopher 4 grabs fork 4; all the forks are acquired, and all the philosophers are stuck waiting for a fork that another philosopher possesses."

### A Solution: Breaking The Dependency

Below is a solution. It works, because "the last philosopher tries to grab right before left, there is no
situation where each philosopher grabs one fork and is stuck waiting for another; the cycle of waiting is broken."

```
void get_forks(int p) {
	if (p == 4) {
		sem_wait(&forks[right(p)]);
		sem_wait(&forks[left(p)]);
	} else {
		sem_wait(&forks[left(p)]);
		sem_wait(&forks[right(p)]);
	}
}
```

## Thread Throttling

We can use a semaphore to limit too many threads from accessing a section of the code at the same time. For example, maybe one section of the code is particularly memory intensive.

## How To Implement Semaphores

This section describes how to build a semaphore from locks and condition variables. Building a condition variable out of semaphores turns out to be much harder and the section does not discuss the details of it.

## Sources

* Chapter 31 ("Semaphores"), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/threads-sema.pdf accessed on 2/3/2022