# Memory hierarchy

Computers organize memory into a hierarchy with smaller, faster, costlier per byte storage at the top of the hierarchy and larger, slower and cheaper per byte storage at the bottom. Going from top to bottom in the hierarchy, computers have registers, an L1 cache, an L2 cache, an L3 cache and main memory (and the hierarchy extends further with local disks and remote disks). The caches use SRAM, or static random access memory. The main memory uses DRAM, or dynamic random access memory. The hierarchy helps to hide some of the "processor-memory gap", which has developed as a result of memory not improving as fast as compute historically.

Main memory is divided into chunks called cache lines. When a byte in memory is accessed, the entire cache line it belongs to is pulled into the caches. Consider a program reading data sequentially from main memory. When the program reads the first byte from main memory, the cache line it belongs to is pulled into the caches. When the program reads the next byte, it avoids the long trip to main memory and reads the data from the L1 cache.

Consider the following C program:

```C
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 10000

int main() {
    // Contiguous block.
    int *data = (int*)malloc(SIZE * SIZE * sizeof(int));
    
    int **arr = (int**)malloc(SIZE * sizeof(int*));
    for (int r = 0; r < SIZE; r++) {
        arr[r] = &data[r * SIZE];
    }

	srand(1);
	for (int r = 0; r < SIZE; r++) {
		for (int c = 0; c < SIZE; c++) {
			arr[r][c] = rand();
		}
	}

	clock_t start = clock();
	int total = 0;
	for (int c = 0; c < SIZE; c++) {
		for (int r = 0; r < SIZE; r++) {
			total += arr[r][c];
		}
	}
    clock_t end = clock();
	double cpu_seconds = ((double)(end - start)) / CLOCKS_PER_SEC;
	printf("%f seconds\n", cpu_seconds);
	
	free(arr);
	free(data);

	return 0;
}
```

Running it a few times with `gcc main.c && ./a.out`, we get around 0.6 seconds. 

If instead we change the order of the loops like this:

```C
for (int r = 0; r < SIZE; r++) {
	for (int c = 0; c < SIZE; c++) {
		total += arr[r][c];
	}
}
```

We get around 0.1 seconds.

Consider a 3 x 3 dimensional array as an example:

```
(0, 0) (0, 1) (0, 2)
(1, 0) (1, 1) (1, 2)
(2, 0) (2, 1) (2, 2)
```

We have it laid out in memory in row-major order:

```
0      1      2      3      4      5      6      7      8
(0, 0) (0, 1) (0, 2) (1, 0) (1, 1) (1, 2) (2, 0) (2, 1) (2, 2)
```

If we have columns in the outer loop and rows in the inner loop, then we read in the following order:

```
0: (0, 0)
3: (1, 0)
6: (2, 0)
1: (0, 1)
4: (1, 1)
7: (2, 1)
2: (0, 2)
5: (1, 2)
8: (2, 2)
```

Notice that it does not read through memory addresses sequentially. However, if we have rows in the outer loop and columns in the inner loop, then we read the array in the same order as it is laid out in memory.

Suppose we iterate through a large array of ints. If the value of each element of the array could be stored in a short, then we could improve performance by changing the type of the array from int to short. In that way, more of the values could fit into the cache.

Suppose have an array of structs and we want to iterate through one of the fields of the structs. In this case, the cache line will include the data from other fields in the struct next to the field of interest in memory. To improve performance, we could consider a struct of arrays, where we could iterate through the array of interest and the data will be contiguous in memory.

Suppose we have a Python list containing heterogeneous types (e.g., `[1, "foo", 3.14, [1, 2, 3], {"key": "value"}]`). This is implemented as an array of `PyObject*` pointers. When we iterate through this list, we're not accessing the actual values sequentially in memory - instead, we're following pointers to scattered memory locations. This means that even though the pointers themselves are contiguous, the actual data they point to may be spread across different cache lines, reducing cache efficiency compared to arrays of primitive types where the values are stored contiguously.

## Sources

* https://csprimer.com/watch/cache-line/
* https://csprimer.com/watch/cache-levels/
* https://csprimer.com/watch/cpu-caches/
* Computer Systems: A Programmer's Perspective, 1.5 Caches Matter and 1.6 Storage Devices Form a Hierarchy
