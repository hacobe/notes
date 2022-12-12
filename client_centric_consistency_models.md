# Client-centric consistency models

We summarize parts of this [report](https://www.microsoft.com/en-us/research/wp-content/uploads/2011/10/ConsistencyAndBaseballReport.pdf), which discusses different client-centric consistency models by using the analogy of a baseball game.

Suppose we have a replicated key-value store to keep track of the score of a baseball game. On each replica, the key-value store starts with the following values:

"home": 0
"visitors": 0

We designate one of the replicas to be the leader and the other replicas to be followers. We send writes to the leader. The leader applies each write to its local key-value store and then sends the write to its followers. It waits for an acknowledgement from a follower before sending another write to the same follower so that the order of writes applied to each follower is the same as the order of writes submitted to the leader.

Suppose the baseball game proceeds as follows:

```
         1 2 3 4 5 6 7 8 9 RUNS
Visitors 0 0 1 0 1 0 0        2
Home     1 0 1 1 0 2          5
```

Here are the writes that have been submitted to the leader:

```
Write ("home", 1)  	   # score: 0-1
Write ("visitors", 1)  # score: 1-1 
Write ("home", 2)      # score: 1-2
Write ("home", 3)      # score: 1-3
Write ("visitors", 2)  # score: 2-3
Write ("home", 4)      # score: 2-4
Write ("home", 5)      # score: 2-5
```

At this point, we make 2 read requests:

```
Read("visitors")
Read("home")
```

And we form a score from the responses. What score will we get?

This depends on the consistency guarantee implemented by the replicated key-value store.

We can specify a consistency guarantee in the form of the set of previous writes that have been applied to the local key-value store when we read.

**Strong consistency** is the guarantee that all previous writes have been applied to the local key-value store when we read. 
We can implement this guarantee using synchronous replication, i.e., the leader does not send back a response to the client after a write request until all followers have acknowledged receipt of that write. In this way, after each write the client requests, all the replicas have up-to-date data. It does not matter which replica we read from. We will always get the most recent score: 2-5.

**Eventual consistency** is the guarantee that some subset of previous writes have been applies to the local key-value store when we read. Suppose Follower A has not received any of the writes yet and we read "visitors" from Follower A and get 0. Suppose Follower B has received the first 3 writes and we read "home" from Follower B and get 2. In this way, we get a score of 0-2, which never was a score in the game. In fact, we could see any of these scores: 0-0, 0-1, 0-2, 0-3, 0-4, 0-5, 1-0, 1-1, 1-2, 1-3, 1-4, 1-5, 2-0, 2-1, 2-2, 2-3, 2-4, 2-5.

**Consistent prefix consistency** is the guarantee that an initial sequence of writes has been applied to the local key-value store when we read. Another way to put this guarantee is that "the reader sees a version of the data store that existed at the [leader] at some time in the past." We can implement this guarantee by always reading from the same replica. The scores that we may see are the scores that actually happened at some point in the game: 0-0, 0-1, 1-1, 1-2, 1-3, 2-3, 2-4, 2-5.

**Bounded staleness consistency** is the guarantee that all "old" writes have been applied to the local key-value store. For example, if we define "old" as "scores that are at most one inning out-of-date", then we get any of the following scores: 2-3, 2-4, 2-5.

**Monotonic read consistency** is the guarantee that an increasing subset of writes have been applied to the local key-value store. Suppose we make the 2 read requests after the first 4 writes and get a score of 1-3. Then we submit the last 3 writes and make the 2 read requests again. What score will we get? With monotonic read consistency, we will see one of the following scores: 1-3, 1-4, 1-5, 2-3, 2-4, or 2-5. We will never go back in time so to speak for either the number of runs by visitors or the number of runs by the home team.

**Read my writes consistency** is the guarantee that all the writes requested by the reader have been applied to the local key-value store. For the writer, we will see a score of 2-5, but for anyone else we only have an eventual consistency guaranteee.

## Sources

* https://www.microsoft.com/en-us/research/wp-content/uploads/2011/10/ConsistencyAndBaseballReport.pdf
