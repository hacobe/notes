"""Reduce.

Implement torch.distributed.reduce using only send and recv
and with the following approaches:
(1) naive
(2) tree (recursive doubling)
(3) linear pipeline
"""
import os
import math
import torch
import torch.distributed

def naive_reduce(tensor, dst):
	"""Naive reduce.

	# How does it work?
	
	Every rank sends to the `dst` rank.
	`dst` receives from every rank iteratively computing the sum.

	# Efficiency

	Same as naive_broadcast.
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	if rank == dst:
		for r in range(world_size):
			if r == dst:
				continue
			tmp = torch.empty_like(tensor)
			torch.distributed.recv(tmp, src=r)
			tensor += tmp
	else:
		torch.distributed.send(tensor, dst=dst)

def tree_reduce(tensor, dst):
	"""Tree reduce.

	# How does it work?

	Same as tree_broadcast.

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
    4) Traverse through each level of this tree starting from the bottom
    	a) for each right child on the level, send a message from that right child to its parent
    	   on the level above

	# Efficiency
	
	Same as tree_broadcast.
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	n_levels = math.ceil(math.log2(world_size))
	for level in range(n_levels-1, -1, -1):
		node = 0
		interval_size = 2**(n_levels - level)
		while True:
			right_child = node + (interval_size // 2)
			if right_child >= world_size:
				break
			mapped_node = (node + dst) % world_size
			mapped_right_child = (right_child + dst) % world_size
			if rank == mapped_right_child:
				torch.distributed.send(tensor, dst=mapped_node)
			elif rank == mapped_node:
				tmp = torch.tensor(tensor)
				torch.distributed.recv(tmp, src=mapped_right_child)
				tensor += tmp
			node += interval_size

def linear_pipeline_reduce(tensor, dst):
	"""Linear pipeline reduce.

	# How does this work?

	Reverse the direction of linear pipeline broadcast, i.e., rank r sends
	to r-1 and receives from r+1 instead of vice versa.

	# Efficiency

	Same as linear_pipeline_broadcast.
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	chunks = list(tensor.chunk(world_size))
	# Each rank is running this loop in parallel (unlike in the naive_broadcast).
	for chunk in chunks:
		mapped_rank = (rank - dst) % world_size

		if mapped_rank+1 < world_size:
			right = (rank + 1) % world_size
			tmp = torch.empty_like(chunk)
			torch.distributed.recv(tensor=tmp, src=right)
			chunk += tmp

		if mapped_rank-1 >= 0:
			left = (rank - 1) % world_size
			torch.distributed.send(tensor=chunk, dst=left)

def main(rank, world_size, broadcast_fn):
	os.environ["MASTER_ADDR"] = "127.0.0.1"
	os.environ["MASTER_PORT"] = "29500"
	torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)

	# The tensor has to be a multiple of world_size for the `linear_pipeline_reduce`.
	tensor = torch.tensor([rank for _ in range(world_size)])
	broadcast_fn(tensor, dst=1)
	print(rank, tensor)

	torch.distributed.destroy_process_group()
if __name__ == "__main__":
	world_size = 4
	#reduce_fn = torch.distributed.reduce
	#reduce_fn = naive_reduce
	#reduce_fn = tree_reduce
	reduce_fn = linear_pipeline_reduce

	processes = []
	for rank in range(world_size):
		p = torch.multiprocessing.Process(target=main, args=(rank, world_size, reduce_fn))
		p.start()
		processes.append(p)

	for p in processes:
		p.join()