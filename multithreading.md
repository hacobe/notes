# Multithreading

## What is a thread?

A **process** is an instance of a computer program (a sequence of instructions) that is being executed by the operating system. It has its own memory space. A **thread** is a component of a process. A process can execute multiple threads concurrently and have them share memory space.

## Why use multithreading?

On a computer with multiple cores, multiple threads can run on different cores at the same time. On a computer with a single core, you can still run multiple threads, but they cannot run at the same time. Instead, the operating system will simulate them running at the same time by rapidly switching back and forth between the different threads.

If your program is CPU bound (meaning that the bottleneck for the program’s execution time is the speed of the processor), then you can speed up the program by using multiple threads on multiple cores. However, if you only have 1 core, then multiple threads will not speed up the program.

If your program is I/O bound (meaning that the bottleneck for the program’s execution time is the speed of input/output operations like downloading a file from a website or reading a file from disk), then you can speed up the program by using multiple threads on multiple cores or by using multiple threads on a single core. You don’t necessarily need multiple cores, because even on a single core the operating system can switch to a thread ready to compute while another thread sits idle waiting for an I/O operation to finish.