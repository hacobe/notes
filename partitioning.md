# Partitioning

**Partitioning** is dividing data up into **partitions** (or **shards**).

The main reason is to handle large datasets and high query loads.

Replication and partitioning are often combined, but the choice of replication scheme is mostly independent from the choice of partitioning scheme, so we ignore replication in our discussion of partitioning to make the discussion simpler.

We also do not discuss queries for analytics, which are more complicated.

If some partitions have more data or more queries than other partitions, then we call the partitioning **skewed**.

A partition with disproportionately high load is called a **hot spot**.

We want to avoid skewed partitions and hot spots by distributing data and query load evenly across partitions.

Here are some different strategies for partitioning a key-value store:

* **Partitioning by key range**: Assign a contiguous range of keys to each partition. Within each partition, keep keys in sorted order. The advantage of this scheme is that we do efficient range queries. The disadvantage is that it can lead to hot spots (e.g., if the key is a timestamp).
* **Partitioning by hash of key range**: This is partitioning by the hash of key range instead of the key range. The advantage of this scheme is that it distributes keys evenly across partitions avoiding hot spots. The disadvantage is that we no longer get efficient range queries.
* **Hybrid approach**: Consider a compound key consisting of a user key and a timestamp. We hash the user key to choose a partition and then we store the data associated with that user sorted by the timestamp in the partition.

Note that we do not use the mod of the key or the hash of the key to determine the partition, because this makes rebalancing difficult when new partitions are added.

Even when partitioning by the hash of a key, we can still get hot spots. For example, a celebrity on a social media site may cause a hot spot. One way of dealing with it is to a random number to the key. This splits writes across multiple partititions. Reads then have to combine the data from multiple partitions.

We now discuss partitioning in the presence of **secondary indexes** (an index that is not a primary index and may have duplicates).

Suppose we are operating a website for selling used cars. Each listing is associated with a document that has a unique document ID. We want to let users search for cars by color and make, so we add a secondary index for color and a secondary index for make. The primary index enables a fast look up of a document by its document ID. The secondary index for color enables a fast look up of all the documents for a listing of a car with a certain color (and similarly for the secondary index for make). If we **partition by document**, then each partition maintains its own secondary indexes. In this scheme, writes only have to deal with one partition, but we might have to send a read query to all partitions (e.g., to search for a red car).

Instead of partitioning by document and having each partition maintain its own, independent secondary index, we can maintain a global index that **partition by term**. For example, we can have a global index for color that we partition by first letter of the color. In this scheme, reads are more efficient than with partitioning by document, but writes are slower and more complicated.

**Rebalancing** is the process of moving data or query load from one partition to another. Here are some strategies:

* **Fixed number of partitions**: Start with a fixed number of partitions that is much larger than the number of nodes. If a new node is added to the cluster, then steal a few partitions from existing nodes. In this scheme, we only have to change the assignment of nodes to partitions.
* **Dynamic partitioning**: When partition exceeds a certain size, then the partition is split into 2 partitions and one of the partitions is transferred to another node. When a partition falls below a certain size, then it is merged with an adjacent partition.
* **Fixed number of partitions per node**: "When a new node joins the cluster, it randomly chooses a fixed number of existing partitions to split, and then takes ownership of one half of each of those split partitions while leaving the other half of each partition in place".

Partitioning by key range use dynamic partitioning, but fixed sized partitioning could result in all the data being assigned to one partition.

Rebalancing requires rerouting queries and moving data, so it's usually good to do rebalancing somewhat manually.

How do we route queries appropriately?
* Send a query to any node. If the node can handle the query, then it does. Otherwise, it forwards the query to another node.
* Send a query to a partition-aware load balancer first.
* Send a query to the appropriate node (the client must be aware of the partitions)

Many systems rely on a separate coordination service like ZooKeeper. Each node registers with ZooKeeper when it is created. ZooKeeper maintains the mapping of partitions to nodes. Partition-aware load balancers can subscribe to ZooKeeper.

## Sources

* DDIA, Chapter 6, "Partitioning"