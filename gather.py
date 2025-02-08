"""Gather.

Implement torch.distributed.gather using only send and recv
and with a naive approach.
"""
import os
import math
import torch
import torch.distributed

def naive_gather(tensor, gather_list, dst):
	"""Gather.

	# How does it work?

	Copy naive_reduce and replace:

	```
	if r == dst:
		continue
	tmp = torch.empty_like(tensor)
	torch.distributed.recv(tmp, src=r)
	tensor += tmp
	```

	with:

	```
	if r == dst:
		gather_list[r] = tensor.clone()
		continue
	torch.distributed.recv(gather_list[r], src=r)
	```

	# Efficiency

	Same as naive_reduce.

	We have to send the same amount of data. It just differs in what it does locally.
	naive_reduce adds what it has received to another buffer.
	naive_gather stores what it has received in a list.
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	if rank == dst:
		for r in range(world_size):
			if r == dst:
				gather_list[r] = tensor.clone()
				continue
			torch.distributed.recv(gather_list[r], src=r)
	else:
		torch.distributed.send(tensor, dst)

def main(rank, world_size, gather_fn):
	os.environ["MASTER_ADDR"] = "127.0.0.1"
	os.environ["MASTER_PORT"] = "29500"
	torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)

	dst = 1
	if rank == dst:
		gather_list = [torch.empty(world_size).float() for r in range(world_size)]
	else:
		gather_list = []
	tensor = torch.tensor([10 + rank for _ in range(world_size)]).float()
	gather_fn(tensor=tensor, gather_list=gather_list, dst=dst)

	print(rank, tensor)

	torch.distributed.destroy_process_group()
if __name__ == "__main__":
	world_size = 4
	#gather_fn = torch.distributed.gather
	gather_fn = naive_gather

	processes = []
	for rank in range(world_size):
		p = torch.multiprocessing.Process(target=main, args=(rank, world_size, gather_fn))
		p.start()
		processes.append(p)

	for p in processes:
		p.join()