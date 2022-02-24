# OSTEP: Common Concurrency Problems

## Non-Deadlock Bugs

An **atomicity violation** is "according to Lu et al,...'The desired serializability among multiple memory accesses is violated (i.e. a code region is intended to be atomic, but the atomicity is not enforced during execution).'"

Here is an example from Figure 32.2

```
Thread 1:
if (thd->proc_info) {
	fputs(thd->proc_info, ...);
}

Thread 2:
thd->proc_info = NULL;
```

And the fix is just to add locks:

```
Thread 1:
pthread_mutex_lock(&proc_info_lock);
if (thd->proc_info) {
	fputs(thd->proc_info, ...);
}
pthread_mutex_unlock(&proc_info_lock);

Thread 2:
pthread_mutex_lock(&proc_info_lock);
thd->proc_info = NULL;
pthread_mutex_unlock(&proc_info_lock);
```

Another common type of bug is an **order violation**.

Here is an example from Figure 32.4:

```
Thread 1:
void init() {
	mThread = PR_CreateThread(mMain, ...);
}

Thread 2:
void mMain(...) {
	mState = mThread->State;
}
```

And the fix is to enforce ordering through condition variables:

![ostep_figure32.5](/img/ostep_figure32.5.png)

## Deadlock Bugs

Deadlock occurs because of the natural, complex dependencies that arise in a codebase and because of encapsulation. As an example of a way in which encapsulation can lead to deadlock, consider the following Java code:

```
Vector v1, v2;
v1.AddAll(v2);
```

If another thread calls v2.AddAll(v1) at nearly the same time, then you can get deadlock.

These 4 conditions need to be met for a deadlock to occur:
* Mutual exclusion
* Hold-and-wait
* No preemption
* Circular wait

Here are different ways to prevent deadlock:
* Circular wait: Enforce a total or partial ordering on lock acquisition (e.g., we can use the lock address and always lock the smaller address first)
* Hold-and-wait: Acquire all locks that you need atomically by wrapping the lock acquisition in a lock. The downsides are that "when calling a routine, this approach requires us to know exactly which locks must be held and to acquire them ahead of time. This technique also is likely to decrease concurrency as all locks must be acquired early on (at once) instead of when they are truly needed."
* No preemption: Use a trylock method, which tries to acquire a lock, but if it can't, then it returns immediately instead of blocking. For example, you could acquire the first lock, then try to the acquire the second lock, but if you can't, then release the first lock and go back to when you tried to acquire the first lock. This approach avoids deadlock, but then the problem of livelock might arise. You could add a random delay. But there are other problems with this approach: "along the way, it must make sure to carefully release them as well; for example, if after acquiring L1, the code had allocated some memory, it would have to release that memory upon failure to acquire L2, before jumping back to the top to try the entire sequence again. However, in limited circumstances (e.g., the Java vector method mentioned earlier), this type of approach could work well."
* Mutual exclusion: Use more powerful hardware to get more powerful atomic operations and build data structures based on that.

Instead of preventing deadlock, we can try to avoid it via scheduling. The downside is that this approach is "only useful in very limited environments, for example, in an embedded system where one has full knowledge of the entire set of tasks that must be run and the locks that they need. Further, such approaches can limit concurrency...".

The final strategy is to detect deadlock and recover. You can just reboot your computer for example. Some systems have a deadlock detector that runs periodically, building a resource graph and checking it for cycles. In the event of a cycle (deadlock), the system needs to be restarted. If more intricate repair of data structures is first required, a human being may be involved to ease the process."

## Summary

"The best solution in practice is to be careful, develop a lock acquisition order, and thus prevent deadlock from occurring in the first place...Perhaps the best solution is to develop new concurrent programming models: in systems such as MapReduce (from Google) [GD02], programmers can describe certain types of parallel computations without any locks whatsoever. Locks are problematic by their very nature; perhaps we should seek to avoid using them unless we truly must."

## Sources

* Chapter 32 ("Common Concurrency Problems"), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/threads-bugs.pdf accessed on 2/12/2022