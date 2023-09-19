# OSTEP: Free-Space Management

## Introduction

It is easy to manage memory when memory is divided into fixed size units. It is difficult when memory is divided into variable-sized units.

The main issue is **external fragmentation**, where free space is divided into variable-sized units and then "subsequent requests may fail because there is no single contiguous space that can satisfy the request, even though the total amount of free space exceeds the size of the request."

## Assumptions

We make the following assumptions:
* We assume the following basic interface for the memory manager:
	* void \*malloc(size_t size) "takes a single parameter, size, which is the number of bytes requested by the application; it hands back a pointer (of no particular type, or a void pointer in C lingo) to a region of that size (or greater)."
	* void free(void \*ptr) "takes a pointer and frees the corresponding chunk"
* We assume the key data structure for the memory manager is some kind of **free list** , which "contains references to all of the free chunks of space in the managed region of memory."
* We assume the main issue is external fragmentation and not **internal fragmentation**, where the memory allocator "hands out chunks of memory bigger than that requested" and there is the space in those chunks that is "unasked for (and thus unused)" by the requestors.
* We assume that "once memory is handed out to a client, it cannot be relocated to another location in memory" and therefore "no **compaction** of free space is possible" (compaction is the process of moving allocated objects so that those objects are together in memory).
* We assume that "the allocator manages a contiguous region of bytes."

## Low-level mechanisms

### Splitting and Coalescing

Suppose the heap looks like this:

```
|---free---|---used---|---free---|
0          10         20         30
```

The free list might then look like this:

```
head -> (addr:0, len:10) -> (addr:20, len:10) -> None
```

If we request an amount of memory that is less than the size of one of the free chunks, then the "allocator will perform an action known as **splitting**: it will find a free chunk of memory that can satisfy the request and split it into two" and the "first chunk it will return to the caller; the second chunk will remain on the list."

For example, if we requested 1 byte of memory, then the allocator might split the second chunk into [20, 21) and [21, 30). The resulting free list would be:

```
head -> (addr:0, len:10) -> (addr:21, len:9) -> None
```

Go back to a free list like this:

```
head -> (addr:0, len:10) -> (addr:20, len:10) -> None
```

Suppose we called free(10). We could end up with a free list like this:

```
head -> (addr:10, len:10) -> (addr:0, len:10) -> (addr:20, len:10) -> None
``` 

A user's request for 20 bytes would fail, because there is no chunk that has a size greater than or equal to 20 bytes even though there are 30 bytes free in total.

To solve this problem, when free is called the allocator does **coalescing**, i.e., looks "at the addresses of the chunk you are returning as well as the nearby chunks of free space; if the newly-freed space sits right next to one (or two, as in this example) existing free chunks, merge them into a single larger free chunk."

After coalescing, the free list above looks like:

```
head -> (addr:0, len:30) -> None
```

### Tracking The Size Of Allocated Regions

A call to free only requires a pointer and not the size of the previously allocated memory. Most allocators track the size associated with a pointer by storing "a little bit of extra information in a header block which is kept in memory, usually just before the handed-out chunk of memory".

In addition to the size, the header may also store a "magic number". We use the same value for this magic number for each allocation. When we a get a pointer to the header, we can check that the magic number read from the header matches the value that we expect.

## Other approaches

### Segregated lists

The **segregated lists** idea is to maintain multiple free lists, where each list only handles objects of a particular size, in addition to the more general memory manager. The segregated lists are used for objects of popular sizes. The **slab allocator** uses segregated lists. When one of the segregated lists is running low on space, it requests more slabs of memory from the general memory manager and "when the reference counts of the objects within a given slab all go to zero, the general allocator can reclaim them from the specialized allocator".

### Buddy allocation

See buddy_memory_manager.py.

### Other ideas

Searching free lists can be slow. Allocators speed this up by using more complex data structures like "balanced binary trees, splay trees, or partially-ordered trees". Also, "...a lot of effort has been spent making allocators work well on multiprocessor-based systems."

## Sources

* Chapter 17 ("Free-Space Management"), Operating Systems: Three Easy Pieces, https://pages.cs.wisc.edu/~remzi/OSTEP/vm-freespace.pdf accessed on 7/23/2023. Up to and including "Tracking The Size Of Allocated Regions" + "Other approaches"
