# Single leader replication

**Replication** is "keeping a copy of the same data on multiple machines that are connected via a network."

The reasons to replicate are:
* Reduce latency by placing data geographically close to users
* Increase availability by keeping the system working even if some parts of the system have failed
* Increase read throughput by increasing the number of machines that can serve read queries

There are 3 popular algorithms for replicating changes between machines:
* Single-leader
* Multi-leader
* Leaderless

We focus here on **single-leader replication**, where one of the replicas is designated the leader and the other replicas are designated followers. We also assume that data is small enough to fit inside a single machine (we need partitioning when this assumption does not hold).

A read request is sent to any one of the replicas.

All write requests are sent to the leader. The leader first writes to its local storage. It then sends the data change to all of its followers in the form of a **replication log** or **change stream**. Each follower uses the log to update its local storage in the same order of the updates on the leader.

The write request can be synchronous or asynchronous. In **synchronous replication**, the leader waits until its followers have confirmed receipt of the write before reporting success to the user. In **asynchronous replication**, the leader sends the write requests to its followers, but doesn't wait for the followers to confirm receipt of the requests.

The advantage of synchronous replication is that all followers have an up-to-date copy of the data. The disadvantage is increased latency and even failure if a follower crashes and does not send back receipt of the request.

Because a single failure of a follower could cause the entire system to fail, it is usually impractical to make all followers synchronous. Instead, we can make one of the followers synchronous and then if that follower crashes, we can switch to another follower being synchronous. In this way, the leader and one of the followers always has an up-to-date copy of the database. This is sometimes called **semi-synchronous replication**.

The advantage of asynchronous replication is reduced latency and the system can continue accepting write requests even if one the followers fails. The disadvantage is that if the leader fails, then any writes that have not been replicated to followers are lost.

**How do you add a new follower?** You could lock the system until the new follower has an up-to-date copy of the database, but that reduces availability. You could copy the database without locking, but then you may lose writes that occur while copying

Here's a high-level approach:
* Take a consistent snapshot of the leader's data
* Copy the snapshot to the new follower
* The follower requests all the writes that have happened since the snapshot was taken
* Eventually it catches up and can process new writes just like any other follower

**How do you recover from a follower failure?** Each follower keeps a log of the data changes it has received. If there's a crash and that log is not lost, then it can just request from the leader all the changes since the last entry in its local log. This is called **catch-up recovery**.

**How do you recover from a leader failure?** This is more complicated. Very broadly, we have to:
* Determine that the leader has failed (e.g., via timeout of messages to the leader)
* Choose a new leader
* Reconfigure the system
This process is called **failover**.

Here are some potential problems with a failover:
* The new leader may not have received all the writes from the old leader before the old leader failed
* If the old leader recovers after the new leader has been promoted, then two machines could think they are the leader.

There are different ways to implement replication logs:
* **Statement-based replication**: The leader sends the write request to followers. However, if the write request includes a non-deterministic function like NOW() or includes a write request that depends on the current state of the database (like auto-incrementing a column), then this implementation can cause problems.
* **Write-ahead log (WAL) shipping**: The leader sends the underlying database log to followers. However, this closely couples replication to the storage engine, because the database log is so low-level.
* **Logical (row-based) log replication**: The leader sends a representation (the logical log) of the underlying database log to followers.
* **Trigger-based replication**: This method of replication usually has greater overhead than other types of replication, but it can be useful, because of its flexibility.

Single-leader replication is an attractive architecture for **read-heavy applications**. We can distribute the read requests among many followers. However, if we use many followers, then the likelihood that one of them will fail increases, so we need to use asynchronous replication. But if we use asynchronous replication, then the follower data may not be up-to-date. This requires thinking through different consistency models.

Here are some different consistency models:
* **Read-after-write**: This guarantees that a user can read what they write after reloading the page. There are a few possible techniques:
	* Read records that the user wrote from the leader
	* Read records that were recently written from the leader
	* Read from replicas that are up-to-date with the timestamp of the last write by the client
* **Monotonic reads**: This guarantees that if a user makes several reads in sequence, the user will not read older data after newer data.
	* We can achieve this by making sure that each user always reads from the same replica.
* **Consistent prefix reads**: This guarantees that if a sequence of writes happens in a particular order, then any user reading those writes will see the data in that order. This is an issue in partitioned databases, where each partition acts independently and there is no global ordering of writes.
	* We can achieve this by making sure that any writes causally related to each other are written to the same partition, but it can't always be done efficiently.

## Sources

* DDIA, Chapter 5, excluding:
	* "Multi-Leader Replication"
	* "Leaderless Replication"