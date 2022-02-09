# Concurrency

A computer program is a sequence of instructions. We can execute 2 computer programs **sequentially** by first executing the instructions of one of the programs and then executing the instructions of the other program. Alternatively, we could execute the 2 computer programs **concurrently** by executing their instructions during overlapping time periods. For example, we could alternate executing instructions from each program so that the programs are executed over roughly the same time period. If we had 2 or more processing units capable of executing instructions, then we could also execute the 2 computer programs in **parallel** by executing the instructions of 1 program on 1 processing unit and the other program on another processing unit. If we execute the 2 programs in parallel, then the 2 programs would be executed during overlapping time periods, which makes parallel computing a special case of concurrent computing.

## Glossary

* **Thread**: "In computer science, a thread of execution is the smallest sequence of programmed instructions that can be managed independently by a scheduler, which is typically a part of the operating system." (https://en.wikipedia.org/wiki/Thread_(computing))
* **Process**: "In computing, a process is the instance of a computer program that is being executed by one or many threads." (https://en.wikipedia.org/wiki/Process_(computing))
* **Lock**: A synchronization primitive to control access to a shared resource.
	* "In computer science, a lock or mutex (from mutual exclusion) is a synchronization primitive: a mechanism that enforces limits on access to a resource when there are many threads of execution." (https://en.wikipedia.org/wiki/Lock_(computer_science))
* **Mutex**: See "Lock"
* **Semaphore**: A variable used to control access to a shared resource, e.g., a count that is incremented or decremented or a bit that is toggled.
	* "In computer science, a semaphore is a variable or abstract data type used to control access to a common resource by multiple threads and avoid critical section problems in a concurrent system such as a multitasking operating system. A trivial semaphore is a plain variable that is changed (for example, incremented or decremented, or toggled) depending on programmer-defined conditions." (https://en.wikipedia.org/wiki/Semaphore_(programming))
* **Race condition**: "A race condition or race hazard is the condition of an electronics, software, or other system where the system's substantive behavior is dependent on the sequence or timing of other uncontrollable events." (https://en.wikipedia.org/wiki/Race_condition)
* **Critical section**: A section of code that accesses a shared resource.
	* "In concurrent programming, concurrent accesses to shared resources can lead to unexpected or erroneous behavior, so parts of the program where the shared resource is accessed need to be protected in ways that avoid the concurrent access. This protected section is the critical section or critical region. It cannot be executed by more than one process at a time."
* **Deadlock**: "In concurrent computing, a deadlock is a state in which each member of a group waits for another member, including itself, to take action, such as sending a message or more commonly releasing a lock." (https://en.wikipedia.org/wiki/Deadlock)
* **Livelock**: "A livelock is similar to a deadlock, except that the states of the processes involved in the livelock constantly change with regard to one another, none progressing." (https://en.wikipedia.org/wiki/Deadlock#Livelock)
* **Starvation**: "In computer science, resource starvation is a problem encountered in concurrent computing where a process is perpetually denied necessary resources to process its work." (https://en.wikipedia.org/wiki/Starvation_(computer_science))

## Sources

* https://en.wikipedia.org/wiki/Concurrent_computing
* https://en.wikipedia.org/wiki/Process_(computing)
