# Memory mapping

Suppose we run the following program to create a `data.bin` file:

```python
import numpy as np

arr = np.array([0, 1, 2, 3], dtype=np.int32)

with open("data.bin", "wb") as fp:
    arr.tofile(fp)
```

Now consider this program:

```python
import numpy as np
fp = open("data.bin", "rb+")
arr = np.fromfile(fp, dtype=np.int32)
arr[2:] = 0
arr.tofile(fp)
```

The program copies the array from the file on disk into memory. It modifies the array in memory. And then copies the modified array in memory back to the file on disk.

Using `np.fromfile` and `np.ndarray.tofile`, we have no way of reading in just a part of the array and we have no way of writing to just a part of the file. For example, we modify only a part of the array, but we have to write out the entire array to update the file. This limitation also applies to `np.load` and `np.save`.

Now consider this program that performs the same task:

```python
import numpy as np
mm = np.memmap("data.bin", dtype="int32", mode="r+")
mm[2:] = 0
mm.flush()
```

The program calls `np.memmap` to memory map the file, i.e., to create a byte-to-byte correspondence between a portion of virtual memory and the file.

Virtual memory is an abstraction that the operating system provides to a program to make it appear as if the program has access to physical memory. When a program accesses a virtual address in virtual memory, the operating system (in concert with the hardware) translates that virtual address to a physical address. Virtual memory is divided into fixed-sized units called pages. A page is stored in physical memory or in swap space on disk. When a program accesses an address in a page in swap space, the operating system moves that page into physical memory (potentially moving out a page that has not been recently used from physical memory to swap space to make room).

The `np.memmap` returns an array-like object that can be used anywhere an np.ndarray is accepted.

Memory-mapping does not require loading the entire array into memory. When the program modifies part of the array, the operating system finds the data in the file for the page being modified and loads that page into memory.

Changes to the array may not be immediately written to the file. The `flush` call ensures that changes in memory are reflected in the file on disk.

Using `np.memmap`, we can read in just part of the array, modify it and write back to part of the file when necessary. 

Memory-mapped files trade-off memory for performance. Also, memory-mapped files have size limitations (e.g., cannot be larger than 2GB on 32-bit systems).

## Sources

* https://numpy.org/doc/stable/reference/generated/numpy.memmap.html
* https://realpython.com/python-mmap/