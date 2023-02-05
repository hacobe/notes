# Leaderless replication

In leader-based replication (single leader or multi-leader), a leader "determines the order in which writes should be processed, and followers apply the leader's writes in the same order". In leaderless replication, any node can accept writes from the client and no particular ordering of writes is enforced.

There are 2 approaches to get the system into a consistent state:
* Read repair: When making a read request, a client can send the same request to several nodes. The system can then detect stale responses and update them.
* Anti-entropy process: The system can run a background process that looks for inconsistencies and fixes them.

In leaderless replication, we use quorum reads and writes: "Normally, reads and writes are always sent to all n replicas in parallel...every write must be confirmed by w nodes to be considered successful, and we must query at least r nodes for each read...As long as w + r > n, we expect to get an up-to-date value when reading, because at least one of the r nodes we're reading from must be up to date."

We can configure w and r depending on the application: "Often, r and w are chosen to be a majority (more than n/2) of nodes, because that ensures w + r > n while still tolerating up to n/2 node failures...With a smaller w and r you are more likely to read stale values, because it's more likely that your read didn’t include the node with the latest value. On the upside, this configuration allows lower latency and higher availability: if there is a network interruption and many replicas become unreachable, there's a higher chance that you can continue processing reads and writes."

## Sources

* DDIA, Chapter 5, "Leaderless Replication", excluding:
	* "However, even with w + r > n, there are likely to be edge cases where stale values are returned. These depend on the implementation, but possible scenarios include: ..."
	* "Monitoring staleness"
	* "Sloppy Quorums and Hinted Handoff"
	* "Detecting Concurrent Writes"