# OSTEP Memory Virtualization

This is a very high-level summary of chapters 12 through 24 on memory virtualization from "Operating Systems: Three Easy Pieces".

The operating system provides an **address space** to each process that makes it appear that the process has access to a large, continguous block of memory. In fact, each address in an address space is a virtual address that the operating system translates to a physical address behind the scenes. In other words, the operating system virtualizes the physical memory.

The goals of memory virtualization are:
* transparency: a process can behave as if it has access to its own private memory
* protection: the operating system provides each process its own address space so that each process cannot interfere with memory used by another process or the operating system itself 
* efficiency

Early systems did not virtualize memory. Instead, processes directly accessed physical memory. Then, systems shared memory by giving a process full access to memory and saving the state of memory to disk before switching to a new process. However, it is very slow to save state to disk, so systems eventually supported keeping multiple processes in memory.

An address space is divided into **program code**, the **heap** and the **stack**. The heap contains dynamically allocated data and grows downwards and the stack contains local variables, function arguments, and return values and grows upwards.

Early systems virtualized memory using a simple **base and bounds** approach, which involves a base register and a bounds register. At run-time, the CPU adds the base register to each virtual address provided by the process to translate that virtual address into a physical address. It also checks that the physical address is within bounds by checking it against the bounds register. If the address is out of bounds, then the CPU raises an exception. The base and bounds registers and associated circuity are sometimes called the **memory management unit (MMU)**. In this way, the operating system allocates fixed-size slots of memory to each process. This approach suffers from **internal fragmentation**, where a lot of space inside each allocated unit is unused. In particular, a lot of the space in between the heap and the stack is unused.

An improvement is to use **segmentation**, where we introduce a base register and a bounds register for each logical segment of the address space, i.e., for the program code, for the heap and for the stack. In this way, we can place each logical segment into different locations in physical memory and do not have to allocate the space in between the heap and the stack. When say the heap segment needs to grow, the operating system makes a system call, which updates the registers for the segment providing more space for that segment. The CPU raises a **segmentation fault** when the virtual address is translated into a physical address that is outside of the bounds of the segment. Because memory is no longer divided into fixed-sized slots, but divided into intervals of variable length, this approach suffers from **external fragmentation**.

Modern operating systems like Linux use **paging** instead of segmentation (see [here](https://unix.stackexchange.com/questions/469253/does-linux-not-use-segmentation-but-only-paging)) and [here](https://web.archive.org/web/20230917021543/https://www.oreilly.com/library/view/understanding-the-linux/0596002130/ch02s03.html)). (If Linux uses paging, then why does it still raise segmentation faults? The name is an anachronism. See [here](https://stackoverflow.com/questions/69869318/why-exactly-is-segmentation-fault-still-a-thing-in-c)). Paging divides an address space into pages. A **page** is a fixed-sized unit of virtual memory. A **page frame** is a fixed-sized slot in physical memory, which contains a single page. Using fixed-sized units addresses the issue of external fragmentation. However, it introduces some internal fragmentation compared to segmentation, but much less than the first approach, because we keep pages relatively small (e.g., Linux uses a page size of 4KB for x86 processors). Obviously, processes can still reserve variable-sized units of memory, so we still need careful management of free space to reduce external fragmentation (see ostep_free_space_management.md for details).

In order to translate a virtual address to a physical address, the operating system maintains a **page table** per process. The page table is data structure that maps virtual pages to physical page frames. The simplest version is a **linear page table**, which is just an array. The index of the array is the virtual page number and the value at each index is the physical frame number.

Paging can take up a lot of time (we have to look up the page and then the offset within the page) and a lot of memory (the page tables can be large).

We can speed up paging with additional hardware support. In particular, the MMU has a **translation-lookaside buffer (TLB)**, which is a cache of popular virtual to physical address translations.

We can reduce the amount of memory used by replacing the linear page table with a **multi-level page table** (see chapter 20 of OSTEP for details).

What if we want to support many processes running concurrently that each have large address spaces? We may not be able to fit every address space of every running process into memory. In this case, we reserve some space on disk to store pages. We call this the **swap space**.

For example, suppose we have 4 processes with some pages in physical memory and some in the swap space on disk:

![ostep_figure21.1](/img/ostep_figure21.1.png)

In the figure, VPN = Virtual Page Number and PFN = Physical Frame Number. Notice that Proc 3 has all of its page in swap space so that process is not currently running.

The act of accessing a page that is not in memory is called a **page fault**. The operating system handles a page fault, not the hardware. If memory is full, then the operating system first pages out unused pages in memory and then pages in the new page. It decides which pages to page out based on a replacement policy such as **Least Recently Used**.

If the memory demands of the running processes exceed the available memory, then the operating system will constantly be paging in and out, which is sometimes referred to as **thrashing**.

## Sources

* Chapters 12 to 24 (inclusive), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/threads-intro.pdf accessed on 9/1/2023