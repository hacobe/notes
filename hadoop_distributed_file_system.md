# Hadoop Distributed File System (HDFS)

An **HDFS cluster** consists of multiple nodes. One of the nodes is designated the **NameNode** and the other nodes are designated **DataNodes**.

**HDFS clients** initiate reading and writing to the cluster.

The NameNode is an RPC server, each HDFS client is an RPC client and each DataNode is an RPC client. The RPC clients send RPC requests to the NameNode.[^1] The NameNode concurrently handles requests from multiple clients using multi-threading.

At **initialization** of the cluster, each DataNode connects to the NameNode and performs a handshake. The NameNode checks that the DataNode's namespace ID (read: cluster ID) and software version matches its own namespace ID and software version. If they do not match, then the DataNode is shut down. If a DataNode is newly initialized and does not have a namespace ID, then it adopts the NameNode's namespace ID. Checking the namespace ID ensures that nodes with a different namespace ID cannot join the cluster. Checking the software version ensures compatibility with all the nodes on the cluster. 

After a successful handshake, the DataNode **registers** with the NameNode. The NameNode responds with a unique storage ID that identifies the DataNode. The DataNode persistently stores its storage ID. The storage ID makes each DataNode recognizable even if its IP address changes.

An **HDFS file** consists of fixed-size **blocks**. Each block is replicated on multiple DataNodes. A block replica is represented by (1) a file that contains the actual data and (2) a file that contains the metadata including checksums for the block data and the block's generation stamp.

When an HDFS client **writes** a file, it first asks the NameNode to choose 3 DataNodes to host the replicas of the first block in the file. The client sends the data directly to the choosen DataNodes. When the first block is filled, the client asks the NameNode to choose 3 DataNodes (not necessarily the same ones) to host the replicas of the next block and so on. No other client can write to the file while it is open.

When an HDFS client **reads** a file, it first asks the NameNode for the list of DataNodes that host replicas of the blocks of the file. It then contacts a DataNode directly to request the transfer of the block of interest. Multiple clients can read from a file concurrently.

The NameNode maintains the ***mapping of file blocks to DataNodes***. It gets the information to build the mapping via block reports from the DataNode. The block report includes the block ID, the generation stamp, and the length of each block replica that the DataNode hosts. The first block report is sent immediately after the DataNode registers and subsequent block reports are sent every hour.

Each DataNode also sends heartbeats every 3 seconds to the NameNode to confirm that it is operating and its block replicas are available. The NameNode never directly calls the DataNode. Instead, it uses responses to heartbeats to send instructions. If the NameNode does not receive a heartbeat from a DataNode for 10 minutes, then the DataNode is marked out-of-service and the block replicas on that DataNode are marked unavailable. The NameNode then requests for new replicas to be created on other DataNodes.

## Sources

* https://www.educative.io/courses/grokking-adv-system-design-intvw/JYY0oV0Vw6y
* [HDFS Architecture](http://web.archive.org/web/20221108202751/https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
* https://storageconference.us/2010/Papers/MSST/Shvachko.pdf

[^1]: "All HDFS communication protocols are layered on top of the TCP/IP protocol. A client establishes a connection to a configurable TCP port on the NameNode machine. It talks the ClientProtocol with the NameNode. The DataNodes talk to the NameNode using the DataNode Protocol. A Remote Procedure Call (RPC) abstraction wraps both the Client Protocol and the DataNode Protocol. By design, the NameNode never initiates any RPCs. Instead, it only responds to RPC requests issued by DataNodes or clients." (HDFS Architecture)


