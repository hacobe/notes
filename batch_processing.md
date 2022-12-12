# Batch processing

At a high-level, we can categorize systems into 3 types:
* **Services** (online systems): "A service waits for a request or instruction from a client to arrive. When one is received, the service tries to handle it as quickly as possible and sends a response back."
* **Batch processing systems** (offline systems): "A batch processing system takes a large amount of input data, runs a job to process it, and produces some output data."
* **Stream processing systems** (near real-time systems): "Like a batch processing system, a stream processor consumes inputs and produces outputs (rather than responding to requests). However, a stream job operates on events shortly after they happen, whereas a batch job operates on a fixed set of input data."

The main performance metric for services is usually response time. The main performance metric for batch processing is usually throughput. Stream processing systems are somewhere in between services and batch processing systems.

What are some simple ways to do log analysis?
* Chain of Unix tools
* A custom program

For example, the chain of Unix tools to print the 5 most popular pages on a website might look like:

```
cat /var/log/nginx/access.log |
 	awk '{print $7}' |
 	sort |
 	uniq -c |
 	sort -r -n |
 	head -n 5
```

A custom program might look like:

```python
counts = {}
with open("/var/log/nginx/access.log", "r") as fin:
	for line in fin:
		url = line.split()[6]
		counts[url] = counts.get(url, 0) + 1
counts_list = [(url, counts[url]) for url in counts]
counts_list.sort(key=lambda x: -x[1])
for url, count in counts_list[0:5]:
	print("{0} {1}".format(count, url))
```

In the chain of Unix tools approach, we use sorting and scanning to count the number of URLs, while in the custom program approach we use an in-memory hash map.

An advantage of the sorting approach is that it works even if we have too many URLs to fit into memory. Why does the sorting approach still work? We can sort chunks of the file, write the sorted chunks to disk, and then merge those sorted chunks. This process has "sequential access patterns that perform well on disks".

The Unix sort utility in particular can also parallelize sorting across multiple CPU cores.

The chain of Unix tools approach can process gigabytes of log files in a matter of seconds.

In general, the Unix philosophy was described as:
* "Make each program do one thing well. To do a new job, build afresh rather than complicate old programs by adding new “features."
* "Expect the output of every program to become the input to another, as yet unknown, program. Don't clutter output with extraneous information. Avoid stringently columnar or binary input formats. Don't insist on interactive input."
* "Design and build software, even operating systems, to be tried early, ideally within weeks. Don't hesitate to throw away the clumsy parts and rebuild them."
* "Use tools in preference to unskilled help to lighten a programming task, even if you have to detour to build the tools and expect to throw some of them out after you've finished using them."

Unix program are very composable, because of their:
* **Uniform interface**: "In Unix, that interface is a file (or, more precisely, a file descriptor). A file is just an ordered sequence of bytes. Because that is such a simple interface, many different things can be represented using the same interface: an actual file on the filesystem, a communication channel to another process (Unix socket, stdin, stdout), a device driver (say /dev/audio or /dev/lp0), a socket representing a TCP connection, and so on...By convention, many (but not all) Unix programs treat this sequence of bytes as ASCII text...awk, sort, uniq, and head all treat their input file as a list of records separated by the \n"
* **Separation of logic and writing**: "Another characteristic feature of Unix tools is their use of standard input (stdin) and standard output (stdout)."
* **Transparency and experimentation**: "The input files to Unix commands are normally treated as immutable...You can end the pipeline at any point, pipe the output into less, and look at it to see if it has the expected form...You can write the output of one pipeline stage to a file and use that file as input to the next stage"

The biggest limitation of Unix tools is that they only work on a single machine.

MapReduce is kind of like the Unix tools:
* "A single MapReduce job is comparable to a single Unix process: it takes one or more inputs and produces one or more outputs."
* "While Unix tools use stdin and stdout as input and output, MapReduce jobs read and write files on a distributed filesystem"
* "The handling of output from MapReduce jobs follows the same philosophy. By treating inputs as immutable and avoiding side effects (such as writing to external databases), batch jobs not only achieve good performance but also become much easier to maintain"

MapReduce processes data as follows:
* "Read a set of input files, and break it up into records."
* "Call the mapper function to extract a key and value from each input record."
* "Sort all of the key-value pairs by key."
* "Call the reducer function to iterate over the sorted key-value pairs."

The MapReduce scheduler "tries to run each mapper on one of the machines that stores a replica of the input file...This principle is known as putting the computation near the data [27]: it saves copying the input file over the network, reducing network load and increasing locality."

The mapper "partitions its output by reducer, based on the hash of the key" and "Each of these partitions is written to a sorted file on the mapper's local disk".

When the mapper finishes, the scheduler "notifies the reducers that they can start fetching the output files from that mapper. The reducers connect to each of the mappers and download the files of sorted key-value pairs for their partition. The process of partitioning by reducer, sorting, and copying data partitions from mappers to reducers is known as the shuffle [26] (a confusing term—unlike shuffling a deck of cards, there is no ran‐ domness in MapReduce)."

The reducer writes output files to the distributed filesystem.

It is very common to chain together MapReduce jobs into **workflows**. Various workflow schedulers like Airflow have been developed.

Suppose that we want to run a MapReduce job that joins together user activity stored in log files in the distributed filesystem with user information stored in a database.

A naive implementation would be to query a database on a remote server for the user information, but "Making random-access requests over the network for every record you want to process is too slow".

Instead, we should copy the user information into the distributed filesystem. Then, we can run a mapper on both the user activity to get (user ID, event) key-value pairs and on the user information to get (user ID, info) key-value pairs. The mapper will write these key-value pairs sorted by the key. The reducer then merges the user activity and the user information together. This is a **sort-merge join**.

Skew, or hot spots, can lead to stragglers in the MapReduce job. One method to handle hot keys is a **skewed join**, which involves first detecting hot keys and then dividing the "work of handling the hot key over several reducers, which allows it to be parallelized better, at the cost of having to replicate the other join input to multiple reducers."

The sort-merge join and the skewed join are **reduce-side joins**.

There are also **map-side joins**. A **broadcast hash join** involves reading one of the datasets into an in-memory hash map. If the input datasets are partitioned in the same way (each partition contains the same user IDs), then we can use a **partitioned hash join**, which involves applying a hash join to each partition. If the input datasets are partitioned in the same way and sorted based on the same key, then we can use a **map-side merge join**, which executes the same merging step as in the reduce-side join.

**Materialization** is the process of writing out intermediate state. MapReduce materializes intermediate state, while the chain of Unix tools does not. The chain of Unix tools "stream the output to the input incrementally, using only a small in-memory buffer".

Materializing intermediate state has some downsides:
* "A MapReduce job can only start when all tasks in the preceding jobs (that generate its inputs) have completed, whereas processes connected by a Unix pipe are started at the same time, with output being consumed as soon as it is produced."
* "Mappers are often redundant: they just read back the same file that was just written by a reducer, and prepare it for the next stage of partitioning and sorting."
* "Storing intermediate state in a distributed filesystem means those files are repli‐ cated across several nodes, which is often overkill for such temporary data."

To address these issues, dataflow engines like Spark "handle an entire workflow as one job, rather than breaking it up into independent subjobs."

They are similar to MapReduce in that "they work by repeatedly calling a user-defined function to process one record at a time on a single thread. They parallelize work by partitioning inputs, and they copy the output of one function over the network to become the input to another function." However, they differ from MapReduce in that "these functions need not take the strict roles of alternating map and reduce, but instead can be assembled in more flexible ways."

Because dataflow engines avoid unnecessarily materializing intermediate state, they have to take a different approach to fault tolerance: "if a machine fails and the intermediate state on that machine is lost, it is recomputed from other data that is still available".

## Sources

* Chapter 10, DDIA