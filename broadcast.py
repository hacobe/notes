"""Broadcast.

Implement torch.distributed.broadcast using only send and recv
and with the following approaches:
(1) naive
(2) tree (recursive doubling)
(3) linear pipeline

# Sources

* Introduction to Parallel Computing
* https://en.wikipedia.org/wiki/Collective_operation
* https://en.wikipedia.org/wiki/Broadcast_(parallel_pattern)
"""
import os
import math
import torch
import torch.distributed

def naive_broadcast(tensor, src):
	"""Naive broadcast.

	# How does it work?
	
	The `src` rank sends to every other rank.
	Every other rank receives from the `src` rank.

	# Efficiency

	Total time = (p-1) * (t_s + m * t_w)
	
	It does not scale well with the number of processes.

	Also from the Introduction to Parallel Computing:

	"...the source process becomes a bottleneck...communication network"
	"is underutilized because only the connection between a single pair of"
	"nodes is used at a time".
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	if rank == src:
		for r in range(world_size):
			if r == src:
				continue
			torch.distributed.send(tensor, dst=r)
	else:
		torch.distributed.recv(tensor, src=src)

def tree_broadcast(tensor, src):
	"""Tree broadcast (i.e., recursive doubling).

	# How does it work?

	The idea is that at the first step the `src` can only communicate with one node.
	At the second step, two nodes have the message and can communicate to two other nodes.
	And so on. 

	In particular:

	1) Round up the world_size to the nearest power of 2
	2) Draw a binary tree of intervals
		   [0,8)
		 /      \
	 [0,4)       [4,8)
     /    \      /    \
    [0,2) [2,4) [4,6) [6,8)
    ....
    3) Simplify the tree to only include the lower bound at each node
             0
           /   \
          0     4
         / \   / \
        0  2   4  6
       /\ / \ /\  /\
      0 1 2 3 4 5 6 7
    4) Traverse through each level of this tree
    	a) For each node on a level, send a message from the node to its right child

    # Efficiency

	Total time = log2(p) * (t_s + m * t_w)

	In this approach, you have the maximum number of nodes send a message at each step.
	In the naive approach, you have `src` communicate to all other nodes sequentially.
	
	Also from the Introduction to Parallel Computing:

	"The message recipients are selected in this manner at each step to avoid congestion on
	 the network".
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	n_levels = math.ceil(math.log2(world_size))
	for level in range(n_levels):
		node = 0
		interval_size = 2**(n_levels - level)
		while True:
			right_child = node + (interval_size // 2)
			if right_child >= world_size:
				break
			mapped_node = (node + src) % world_size
			mapped_right_child = (right_child + src) % world_size
			if rank == mapped_node:
				torch.distributed.send(tensor, dst=mapped_right_child)
			elif rank == mapped_right_child:
				torch.distributed.recv(tensor, src=mapped_node)
			node += interval_size

def linear_pipeline_broadcast(tensor, src):
	"""Linear pipeline broadcast.

	# How does it work?

	It requires a tensor of more than 1 element. Otherwise, we can't pipeline.

	* rank 0 has all the chunks already
	* rank 0 passes a chunk to rank 1
	* rank 1 receives a chunk from rank 0 and passes it to rank 2
	* rank 2 receives a chunk from rank 1 and passes it to rank 3
	...
	* rank n-1 receives a chunk from rank n-2 and stops (no one to pass it to)

	Imagine a line of people. The first person is next to a stack of boxes.
	The first person picks up a box and passes it to the next person. As soon as the first person
	hands off the box to the next person, they pick up another box and hand it to the second person
	as soon as the second person has their hands free. Multiple people could be handing boxes over and
	taking boxes at the same time.

	You have to recv before you send.

	# Efficiency

	Let k be the number of chunks.

	Each round is the time to send one chunk, which is (t_s + m * t_w).
	The last rank receives the first chunk after p-1 rounds.
	The last rank then receives 1 chunk each until it has received the remaining k-1 chunks.
	Therefore, the total time to communicate the message is:

	Total time = (p-1+k-1) * (t_s + (m/k) * t_w)

	If we ignore latency, we might choose k = p, which gives:

	Total time = 2 * (p-1) * (t_s + (m/p) * t_w)
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	chunks = list(tensor.chunk(world_size))
	# Each rank is running this loop in parallel (unlike in the naive_broadcast).
	for chunk in chunks:
		mapped_rank = (rank - src) % world_size

		if mapped_rank-1 >= 0:
			# We receive from the left in the ring.
			left = (rank - 1) % world_size
			torch.distributed.recv(tensor=chunk, src=left)

		if mapped_rank+1 < world_size:
			# And pass to the right in the ring.
			right = (rank + 1) % world_size
			torch.distributed.send(tensor=chunk, dst=right)

def main(rank, world_size, broadcast_fn):
	os.environ["MASTER_ADDR"] = "127.0.0.1"
	os.environ["MASTER_PORT"] = "29500"
	torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)

	# The tensor has to be a multiple of world_size for the `linear_pipeline_broadcast`.
	tensor = torch.tensor([rank for _ in range(world_size)])
	broadcast_fn(tensor, src=1)
	print(rank, tensor)

	torch.distributed.destroy_process_group()
if __name__ == "__main__":
	world_size = 4
	broadcast_fn = torch.distributed.broadcast
	#broadcast_fn = naive_broadcast
	#broadcast_fn = tree_broadcast
	#broadcast_fn = linear_pipeline_broadcast

	processes = []
	for rank in range(world_size):
		p = torch.multiprocessing.Process(target=main, args=(rank, world_size, broadcast_fn))
		p.start()
		processes.append(p)

	for p in processes:
		p.join()