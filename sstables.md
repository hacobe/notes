# SSTables

An SSTable "provides a persistent, ordered immutable map from keys to values, where both keys and values are arbitrary byte strings. Operations are provided to look up the value associated with a specified key, and to iterate over all key/value pairs in a specified key range" (Bigtable paper).

When a write comes in, we add it to an in-memory balanced tree data structure (e.g., a red-black tree). This index is sometimes called a memtable. When the memtable exceeds a certain size, we write out the data to a segment file on disk with the records stored in sorted order by key. During the writing process, the records are grouped together into blocks, the blocks are compressed and the blocks are written to the segment file. Compression reduces disk space and I/O bandwidth use.

Because the keys are stored in sorted order, compaction and merging are simple and efficient. Merging happens like in mergesort and if multiple segments contain the same key, "we can keep the value from the most recent segment and discard the values in older segments."

In addition to the in-memory balanced tree, there is a hash map that maps the keys that start a block to the location of the start of the block on disk. We do not need to store all the keys in the hash map, because the keys are in sorted order on disk, so we can find the rough location and then scan until we get the exact location.

When a read comes in, we first try to find the key in the memtable and then in the hash map for the most recent segment, then in the hash map for the next most recent segment and so on.

To avoid losing the data in the memtable but not yet on disk, "we can keep a separate log on disk to which every write is immediately appended, just like in the previous section. That log is not in sorted order, but that doesn't matter, because its only purpose is to restore the memtable after a crash. Every time the memtable is written out to an SSTable, the corresponding log can be discarded."

A common optimization is to have Bloom filter for each segment to check if a key is contained in the segment and avoid disk reads.

## Sources

* "Bigtable: A Distributed Storage System for Structured Data" (https://static.googleusercontent.com/media/research.google.com/en/archive/bigtable-osdi06.pdf)
* Chapter 3, DDIA
* https://stackoverflow.com/questions/69103575/how-to-maintain-the-sparse-index-in-a-lsm-tree