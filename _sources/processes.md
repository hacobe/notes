# Processes

A **process** is an abstraction provided by the operating system for a running program.

The process API includes the following operations:

* Create a new process
* Destroy an existing process
* Wait until the process stops running
* Suspend a process and resume it later
* Check the status of a process

When a process is created, the operating system:

* Loads the process's code and static data into the address space of the process
* Allocates memory to the process's stack, including initializing the stack with arguments from the main() function
* Allocates memory to the heap if needed
* Setups I/O for standard input, output and error
* Jumps to the main() routine and transfers control of the CPU to the process

The state of the process can be:

* Initializing
* Running
* Ready to run
* Blocked (e.g., waiting for I/O to finish)
* Zombie (finished running, but not yet cleaned up)

## Sources

* Chapter 4 ("The Abstraction: The Process"), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf accessed on 2/1/2022
