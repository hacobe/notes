"""All-reduce.

Implement torch.distributed.all_reduce using only send and recv
and with the following approaches:
(1) naive
(2) ring
"""

import os
import math
import torch
import torch.distributed

def naive_all_reduce(tensor):
	"""Naive all-reduce.

	# How does it work?

	Reduce + Broadcast.

	# Efficiency

	2 * (total time for reduce/broadcast)
	"""
	torch.distributed.reduce(tensor, dst=0)
	torch.distributed.broadcast(tensor, src=0)

def ring_all_reduce(tensor):
	"""Ring all-reduce.

	# How does it work?

	In the scatter-reduce:
	* As expected, each rank receives from (rank - 1) % world_size and sends to (rank + 1) % world_size
	* As expected, each rank starts by sending chunks[rank] and receiving chunks[(rank - 1) % world_size]
	* At the next iteration, each rank sends chunks[(rank - 1) % world_size] and receives chunks[(rank - 2) % world_size],
	  i.e., we move backwards (moving forwards gives the incorrect result; we can see this analyzing world_size = 3)

	The goal is to get one full sum in a different index on each rank.

	https://web.archive.org/web/20241221151124/https://andrew.gibiansky.com/blog/machine-learning/baidu-allreduce/
	
	# Efficiency

	2 * (p - 1) * (t_s + (m/p) * t_w)

	This scales better with p for latency-insensitive applications than the tree_reduce_broadcast_allreduce.

	The ring all-reduce has the same asymptotic time complexity as the linear_pipeline_reduce_broadcast_allreduce,
	but it is typically more efficient in practice because all processes are communicating in parallel at each step.
	In contrast, the linear pipeline has more sequential dependencies (I think this is related to the pipeline "bubble").
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	chunks = list(tensor.chunk(world_size))

	# scatter-reduce
	for step in range(world_size - 1):
		dst = (rank + 1) % world_size
		i = (rank - step) % world_size
		send_req = torch.distributed.isend(chunks[i], dst=dst)

		src = (rank - 1) % world_size
		j = (rank - step - 1) % world_size
		tmp = torch.zeros_like(chunks[j])
		torch.distributed.recv(tmp, src=src)
		chunks[j] += tmp

		send_req.wait()

	# all-gather
	# (same as scatter-reduce except we add 1 to i and j)
	for step in range(world_size - 1):
		dst = (rank + 1) % world_size
		i = (rank - step + 1) % world_size
		send_req = torch.distributed.isend(chunks[i], dst=dst)

		src = (rank - 1) % world_size
		j = (rank - step) % world_size
		torch.distributed.recv(chunks[j], src=src)

		send_req.wait()

def main(rank, world_size, all_reduce_fn):
	os.environ["MASTER_ADDR"] = "127.0.0.1"
	os.environ["MASTER_PORT"] = "29500"
	torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)

	# The tensor has to be a multiple of world_size for the pipelining.
	tensor = torch.tensor([rank for _ in range(world_size)])
	all_reduce_fn(tensor)
	print(rank, tensor)

	torch.distributed.destroy_process_group()
if __name__ == "__main__":
	world_size = 4
	#all_reduce_fn = torch.distributed.all_reduce
	#all_reduce_fn = naive_all_reduce
	all_reduce_fn = ring_all_reduce

	processes = []
	for rank in range(world_size):
		p = torch.multiprocessing.Process(target=main, args=(rank, world_size, all_reduce_fn))
		p.start()
		processes.append(p)

	for p in processes:
		p.join()