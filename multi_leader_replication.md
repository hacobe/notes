# Multi-leader replication

In single-leader replication, all writes go through the leader. In single-leader replication with partitioning, there is a single leader per partition and all writes to a particular partition go through the leader for that partition. If the client can't connect to the leader, then the client cannot write to the partition. 

In multi-leader replication, we have multiple leaders and each leader is a follower of all the other leaders. Reads can go to any node and writes go to one of the leaders.

Multi-leader replication is complex. Here are some applications with the additional complexity might be justified:
* Multi-datacenter operation (a leader in each data center)
* Clients with offline operation (every device is a leader)
* Collaborative editing (similar to clients with offline operation)

The main challenge of multi-leader replication is resolving write conflicts.

Suppose 2 users are editing the title of a document. The first user requests a write to change the document title from A to B and the second user requests a write to change the document title from A to C. In single-leader replication, one of the writes is received by the leader first. Suppose the first user's request arrives first and the title is changed to B. When the second write arrives, the conflict can be detected (trying to change the title from A to C, but the title is now B) and an error can be returned to the second user. In multi-leader replication, the first user's request might go to one leader and the second user's request might go to a different leader. Whichever leader receives a write request first could lock writing on all other leaders until its write has been replicated, but if we do that (synchronous conflict resolution), then we might as well just use single-leader replication, because leaders won't be able to accept writes independently. However, if we don't do that (asynchronous conflict resolution), then we only detect a conflict when a write from one leader gets sent to another leader and that other leader has already applied a different write.

What are different strategies to deal with write conflicts?
* Conflict avoidance (e.g., a particular user is always routed to the leader in the same datacenter)
* Converging towards a consistent state (e.g., last write wins)
* Custom conflict resolution (e.g., call a conflict handler when a conflict is detected on write or alternatively return all conflicting writes on read)

In single-leader replication, we replicate from the single leader to all the replicas. In multi-leader replication with 2 leaders, we replicate from one leader to the other leader and vice versa. In multi-leader replication with more than 2 leaders, we need to choose a "replication topology" that determines "the communication paths along which writes are propagated from one node to another". For example, we could a circular topology, a star topology or an all-to-all topology. 

Here are some trade-offs:
* "A problem with circular and star topologies is that if just one node fails, it can interrupt the flow of replication messages between other nodes, causing them to be unable to communicate until the node is fixed."
* "On the other hand, all-to-all topologies can have issues too. In particular, some network links may be faster than others (e.g., due to network congestion), with the result that some replication messages may 'overtake' others"

## Sources

* DDIA, Chapter 5, "Multi-Leader Replication", excluding:
	* "Automatic Conflict Resolution"
	* "What is a conflict?"