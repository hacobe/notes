# Log segments with a hash index

Consider a very simple key-value store that just writes by appending the key and value to a text file called the **log**. It then reads by scanning the log until the end and returning the value associated with the last key that matches.

If the log gets too large, we can close it and start a new log. The closed logs are called **segments**. We throw away duplicate keys in the segments keeping only the most recent key using a process called **compaction**. While running compaction, we also merge segments together. The merged segments are written to a new file (segments are closed after being written). When the merging process is complete, we can switch to using the new merged file as our log and delete the old segment files.

In order to delete a key, we append a special delete record for the key to the log.

Writing to this database is efficient, because appending to a file is generally efficient. Reading is very inefficient.

For partially written records, we use checksums to detect corrupted data.

For concurrency control, we only have one writer thread. Because segments are append-only and otherwise immutable, we can read from them using multiple, concurrent threads.

Why not update a file in-place?
* Appending and merging are sequential, write operations that are much faster than random writes
* Concurrency and crash recovery are simpler, because we do not have to worry about a crash while a value is being overwritten

To improve the efficiency of reads (at the cost of slowing down writes), we introduce an **index**, i.e., a data structure that stores metadata to locate records in the database. 

The simplest possible index is an in-memory hash map, where each key is mapped to a byte offset in the log. Each segment has its own hash map. To find a key, we first look in the most recent segment hash map, then the next most recent and so on. 

For crash recovery, we could re-read the entire segment file, but that would take a while, so instead we occassionally snapshot the in-memory hash maps.

The downsides of an in-memory hash map are:
* The hash map must fit into memory
* Range queries are inefficient

## Sources

* Chapter 3, DDIA