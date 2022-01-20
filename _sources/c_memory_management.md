# C memory management

For simplicity, assume that we have a computer that runs one program at a time and that the program uses all of the computer’s memory. Suppose further that this computer is a 32 bit system, i.e., each memory address is represented by an unsigned 32 bit integer and points to a byte (8 bits) in memory. The system therefore has $2^{32}$ bytes of memory, or roughly 4GB of memory.

Memory is a contiguous block of bits, but by convention we divide it as follows:

![cs61c_program_address_space](/img/cs61c_program_address_space.png)

FFFF FFFF in hexadecimal is 32 1s in binary.

The **code** and the **static data** sections are loaded when the program starts. The code section contains the instructions that comprise the program. The static data section contains global variables. We know how much memory is needed for these variables at compile time instead of run time, they do not shrink or grow, and they exist for the lifetime of the program.

The **stack** has a rigid pattern of allocating and de-allocating memory. The “stack pointer” points to the end of the stack. We move the stack pointer down when we want to allocate more memory on the stack and we move it up when we want to de-allocate memory. A new block of memory allocated on the stack is called the “stack frame”. The stack is used whenever a function is called. When a function is called, we allocate a new frame on the stack, which includes the return address, i.e., the address of the instruction that called the function, the function arguments and primitive variables (e.g., ints, floats, arrays, etc.) declared inside the function.

The **heap** does not follow the same rigid pattern of allocating and de-allocating memory as the stack. Instead, allocating memory in the heap and de-allocating is managed explicitly by the programmer.

## Sources

* UC Berkeley, CS61C, Spring 2015
	* [Lecture 4](https://www.youtube.com/watch?v=4orEBUAb8ps&list=PLhMnuBfGeCDM8pXLpqib90mDFJI-e1lpk&index=4)