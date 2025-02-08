"""Embedding lookup.

# Sources

* https://github.com/NVIDIA/Megatron-LM/blob/076972e37420b5325c5fe06e7131be7d96f05b53/megatron/core/tensor_parallel/layers.py#L171
"""
import torch
import torch.distributed
import multiprocessing
import os

def main(rank, world_size):
	if world_size > 1:
		os.environ["MASTER_ADDR"] = "127.0.0.1"
		os.environ["MASTER_PORT"] = "29500"
		torch.distributed.init_process_group(
			"gloo", rank=rank, world_size=world_size)

	batch_size = 8
	seq_len = 16
	vocab_size = 32
	embed_dim = 64
	torch.manual_seed(0)
	weight = torch.randn(vocab_size, embed_dim)
	x = torch.randint(low=0, high=vocab_size, size=(batch_size, seq_len))

	vocab_size_per_rank = vocab_size // world_size
	start = rank * vocab_size_per_rank
	end = start + vocab_size_per_rank
	# Typically, we would initialize a weight matrix of this shape,
	# but slicing makes it easier to test.
	weight = weight[start:end, :]
	mask = ((x >= start) & (x < end))
	x -= start
	x *= mask
	embeddings = weight[x]
	embeddings[~mask] = 0
	torch.distributed.all_reduce(embeddings)

	torch.manual_seed(0)
	weight = torch.randn(vocab_size, embed_dim)
	x = torch.randint(low=0, high=vocab_size, size=(batch_size, seq_len))
	expected_embeddings = weight[x]

	assert torch.allclose(embeddings, expected_embeddings)

	if world_size > 1:
		torch.distributed.destroy_process_group()

if __name__ == "__main__":
	world_size = 2
	if world_size == 1:
		main(0, 1)
	else:
		processes = []
		for rank in range(world_size):
			p = multiprocessing.Process(target=main, args=(rank, world_size))
			p.start()
			processes.append(p)
		for p in processes:
			p.join()