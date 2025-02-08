"""Scatter.

Implement torch.distributed.scatter using only send and recv
and with the following approaches:
(1) naive
(2) tree (recursive doubling)
"""
import os
import math
import torch
import torch.distributed

def naive_scatter(tensor, scatter_list, src):
	"""Scatter.

	# How does it work?

	Copy naive_broadcast and replace:

	```
	if r == rank:
		continue
	torch.distributed.send(tensor, dst=r)
	```

	with:

	```
	if r == rank:
		tensor.copy_(scatter_list[r])
		continue
	torch.distributed.send(scatter_list[r], dst=r)
	```

	# Efficiency

	Same as naive_broadcast.
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	if rank == src:
		for r in range(world_size):
			if r == rank:
				tensor.copy_(scatter_list[r])
				continue
			torch.distributed.send(scatter_list[r], dst=r)
	else:
		torch.distributed.recv(tensor, src=src)

def tree_scatter(tensor, scatter_list, src):
	"""Tree scatter.

	# How does it work?

	We add the following to the tree_broadcast:

	```
	shape = [d for d in tensor.shape]
	batch_size = shape[0]
	shape[0] *= world_size

	if rank == src:
		scatter_tensor = torch.concat(scatter_list, dim=0)
	else:
		# We need a tensor, because torch.distributed cannot
		# send a list of messages and we don't want to send
		# the messages in a loop.
		scatter_tensor = torch.empty(shape)
	
	...

	if rank == src:
		tensor.copy_(scatter_list[rank])
	else:
		tensor.copy_(scatter_tensor.split(batch_size)[rank])
	```

	We also replace `tensor` with `scatter_tensor` in the `send` and `recv`.

	# Efficiency

	Total time = log2(p) * (t_s + m * p * t_w)

	Same as tree broadcast except multiply the unit message size by p.
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	shape = [d for d in tensor.shape]
	batch_size = shape[0]
	shape[0] *= world_size

	if rank == src:
		scatter_tensor = torch.concat(scatter_list, dim=0)
	else:
		# We need a tensor, because torch.distributed cannot
		# send a list of messages and we don't want to send
		# the messages in a loop.
		scatter_tensor = torch.empty(shape)

	n_levels = math.ceil(math.log2(world_size))
	for level in range(n_levels):
		node = 0
		interval_size = 2**(n_levels - level)
		while node < world_size:
			right_child = node + (interval_size // 2)
			mapped_node = (node + src) % world_size
			mapped_right_child = (right_child + src) % world_size
			if rank == mapped_node:
					torch.distributed.send(scatter_tensor, dst=mapped_right_child)
			elif rank == mapped_right_child:
					torch.distributed.recv(scatter_tensor, src=mapped_node)
			node += interval_size

	if rank == src:
		tensor.copy_(scatter_list[rank])
	else:
		tensor.copy_(scatter_tensor.split(batch_size)[rank])

def main(rank, world_size, scatter_fn):
	os.environ["MASTER_ADDR"] = "127.0.0.1"
	os.environ["MASTER_PORT"] = "29500"
	torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)

	src = 1
	if rank == src:
		scatter_list = [
			torch.tensor(
				[10 + r for _ in range(world_size)]
			).float() for r in range(world_size)
		]
	else:
		scatter_list = []
	tensor = torch.empty(world_size).float()
	scatter_fn(tensor=tensor, scatter_list=scatter_list, src=src)

	print(rank, tensor)

	torch.distributed.destroy_process_group()
if __name__ == "__main__":
	world_size = 4
	#scatter_fn = torch.distributed.scatter
	#scatter_fn = naive_scatter
	scatter_fn = tree_scatter

	processes = []
	for rank in range(world_size):
		p = torch.multiprocessing.Process(target=main, args=(rank, world_size, scatter_fn))
		p.start()
		processes.append(p)

	for p in processes:
		p.join()