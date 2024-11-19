# OSTEP: Introduction to operating systems

An operating system (OS) is "system software that manages computer hardware, software resources, and provides common services for computer programs." (https://en.wikipedia.org/wiki/Operating_system)

At a high-level, the main goal of an operating system is to make it easy to run software on a computer.

There are a 3 different ways to view an operating system:
* An operating system is a virtual machine
* An operating system provides a standard library to applications
* An operating system is a resource manager

There are 3 conceptual pieces fundamental to operating systems:
* **Virtualization** is when the operating system "takes a physical resource (such as the processor, or memory, or a disk) and transforms it into a more general, powerful, and easy-to-use virtual form of itself".
* **Concurrency** refers to "host of problems that arise, and must be addressed, when working on many things at once (i.e., concurrently) in the same program"
* **Persistence** "refers to the characteristic of state of a system that outlives (persists more than) the process that created it." (https://en.wikipedia.org/wiki/Persistence_(computer_science))

The OS virtualizes the CPU and virtualizes memory. **Virtualizing the CPU** is "turning a single CPU (or a small set of them) into a seemingly infinite number of CPUs and thus allowing many programs to seemingly run at once". **Virtualizing memory** gives "Each process accesses its own private virtual address space (sometimes just called its address space), which the OS somehow maps onto the physical memory of the machine."

DRAM stores data in a volatile manner, so it can be easily lost if power goes away or the system crashes. A hard drive or a solid-state drive can store data persistently. The **file system** is the software in the operating system that manages the disk. A program can make **system calls**, which get routed to the file system. The file system issues I/O requests to the underlying storage device and particularly to a **device driver**, which is "some code in the operating system that knows how to deal with a specific device." The file system implements a protocol (e.g., journaling or copy-on-write) that carefully orders "writes to disk to ensure that if a failure occurs during the write sequence, the system can recover to reasonable state afterwards".

Here are some of the basic design goals when building an operating system:

* Convenience and ease-of-use (e.g., by developing good abstractions)
* High performance, i.e., minimize the overhead of the OS
* Protection between the OS and applications (e.g., by isolating processes from one another)
* Reliability
* Ohter goals, e.g., energy efficiency, security, mobility (i.e., able to run on small devices)

Here are some of the different epochs in the history of operating systems:

* **Just a library:** Early operating systems were basically just a library of common function calls. The mainframe systems that ran programs had a human operator and the human operator played the role of the operating system by, for example, scheduling jobs to run that were submitted to the mainframe.
* **Differentiating OS from other code:** One realization was that "code run on behalf of the OS was special; it had control of devices and thus should be treated differently than normal application code." This led to the idea of adding "a special pair of hardware instructions and hardware state to make the transition into the OS a more formal, controlled process". What distinguishes a system call and a procedure call is that a procedure call runs in **user mode**, while a system call runs in **kernel mode** and is given "full access to the hardware of the system and thus can do things like initiate an I/O request or make more memory available to a program".
* **Multiprogramming:** It became common for the OS to "load a number of jobs into memory and switch rapidly between them, thus improving CPU utilization." In this era, **memory protection** became important, because "we wouldn’t want one program to be able to access the memory of another program."
* **Modern era:** The first operating systems for the PC actually were worse than some of the operating systems developed earlier, but eventually the earlier lessons were incorporated: "Even today’s cell phones run operating systems (such as Linux) that are much more like what a minicomputer ran in the 1970s than what a PC ran in the 1980s (thank goodness); it is good to see that the good ideas developed in the heyday of OS development have found their way into the modern world."

## Process

* [60 min] Read and extract questions from OSTEP and write the summary

## Sources

* Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/intro.pdf accessed on 1/22/2022, Pgs. 1-19