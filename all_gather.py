"""All-gather.

Implement torch.distributed.all_gather using only send and recv
and with the ring approach.
"""

import os
import math
import torch
import torch.distributed

def ring_all_gather(tensor_list, tensor):
	"""Ring all-gather.

	# How does it work?

	Copy scatter phase of ring_all_reduce except:
	* add `tensor_list[rank].copy_(tensor)` before the loop
	* replace `chunks` with `tensor_list`

	# Efficiency

	It's the same time complexity as ring_all_reduce except that the message size
	is m not (m/p), because we have a p m-sized chunks in tensor_list rather than
	taking a tensor and chunking it into p (m/p)-sized chunks:

	2 * (p - 1) * (t_s + m * t_w)
	"""
	rank = torch.distributed.get_rank()
	world_size = torch.distributed.get_world_size()

	tensor_list[rank].copy_(tensor)

	for step in range(world_size - 1):
		dst = (rank + 1) % world_size
		i = (rank - step) % world_size
		send_req = torch.distributed.isend(tensor_list[i], dst=dst)

		src = (rank - 1) % world_size
		j = (rank - step - 1) % world_size
		torch.distributed.recv(tensor_list[j], src=src)

		send_req.wait()

def main(rank, world_size, all_gather_fn):
	os.environ["MASTER_ADDR"] = "127.0.0.1"
	os.environ["MASTER_PORT"] = "29500"
	torch.distributed.init_process_group("gloo", rank=rank, world_size=world_size)

	tensor = torch.tensor([rank])
	tensor_list = [torch.empty_like(tensor) for _ in range(world_size)]
	all_gather_fn(tensor_list, tensor)
	print(rank, tensor_list)

	torch.distributed.destroy_process_group()
if __name__ == "__main__":
	world_size = 4
	#all_gather_fn = torch.distributed.all_gather
	all_gather_fn = ring_all_gather

	processes = []
	for rank in range(world_size):
		p = torch.multiprocessing.Process(target=main, args=(rank, world_size, all_gather_fn))
		p.start()
		processes.append(p)

	for p in processes:
		p.join()