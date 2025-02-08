"""MLP with pipeline parallelism

MLP duplicated across ranks except:
* Initialize a layer on each rank (less bookkeeping and illustrates the idea)
	* Initialize the full layers and then slice to make it easier to test
* Add send and recv in the forward pass
* Only the last rank computes the loss
* Only test the loss on the last rank
* Add send and recv in the backward pass
* Only test each gradient on the rank that has it
* Divide the batch into microbatches

# Sources

* https://github.com/siboehm/ShallowSpeed
* https://web.archive.org/web/20241229024855/https://siboehm.com/articles/22/pipeline-parallel-training
"""

import torch
import torch.distributed
import torch.nn as nn
import torch.nn.functional as F
import multiprocessing
import os

def get_rank():
	if torch.distributed.is_initialized():
		return torch.distributed.get_rank()
	return 0

def get_world_size():
	if torch.distributed.is_initialized():
		return torch.distributed.get_world_size()
	return 1

class Linear:

	def __init__(self, input_size, output_size):
		# Important to scale down `self.weight` for multiple layers.
		self.weight = torch.randn(input_size, output_size) * 0.1
		self.grad = None
		self._cache = {}

	def forward(self, x, micro_batch_idx):
		self._cache[f"x_{micro_batch_idx}"] = x
		return x @ self.weight

	def backward(self, dy, micro_batch_idx):
		# [p, q] = [p, n] [n, q]
		self.grad = self._cache[f"x_{micro_batch_idx}"].T @ dy

		# [n, p] = [n, q] @ [q, p]
		dx = dy @ self.weight.T
		return dx

class ReLU:

	def __init__(self):
		self._cache = {}

	def forward(self, x, micro_batch_idx):
		self._cache[f"x_{micro_batch_idx}"] = x
		return F.relu(x, 0)

	def backward(self, dy, micro_batch_idx):
		mask = self._cache[f"x_{micro_batch_idx}"] > 0
		return dy * mask

class MSELoss:

	def __init__(self):
		self._cache = {}

	def forward(self, y, z, micro_batch_idx=0):
		self._cache[f"y-z_{micro_batch_idx}"] = y-z
		return ((y - z)**2).mean() 

	def backward(self, micro_batch_idx=0):
		shape = self._cache[f"y-z_{micro_batch_idx}"].shape
		return 2 * self._cache[f"y-z_{micro_batch_idx}"] * (1/shape[0]) * (1/shape[1])

class MLP:

	def __init__(self, batch_size, sizes):
		self.batch_size = batch_size

		self.full_layers = []
		for i in range(1, len(sizes)):
			self.full_layers.append(Linear(sizes[i-1], sizes[i]))
			self.full_layers.append(ReLU())

		# Typically, we would initialize the layers directly instead
		# of intializing the full layers and then slicing, but this
		# makes it easier to test.
		rank = get_rank()
		world_size = get_world_size()
		if world_size > 1:
			assert len(self.full_layers) == 2 * world_size
			start = 2 * rank
			end = start + 2
			self.layers = self.full_layers[start:end]
		else:
			start = 0
			end = len(self.full_layers)
		self.layers = self.full_layers[start:end]

	def forward(self, x, micro_batch_idx=0):
		rank = get_rank()
		world_size = get_world_size()

		if rank-1 >= 0:
			x = torch.empty(self.batch_size, self.layers[rank-1].weight.shape[0])
			torch.distributed.recv(x, src=rank-1)

		for layer in self.layers:
			x = layer.forward(x, micro_batch_idx)

		if rank+1 < world_size:
			torch.distributed.send(x, dst=rank+1)

		return x

	def backward(self, dy, micro_batch_idx=0):
		rank = get_rank()
		world_size = get_world_size()

		if rank+1 < world_size:
			dy = torch.empty(self.batch_size, self.layers[rank].weight.shape[1])
			torch.distributed.recv(dy, src=rank+1)

		for layer in reversed(self.layers):
			dy = layer.backward(dy, micro_batch_idx)

		if rank-1 >= 0:
			torch.distributed.send(dy, dst=rank-1)

		return dy

def main(rank, world_size):
	if world_size > 1:
		os.environ["MASTER_ADDR"] = "127.0.0.1"
		os.environ["MASTER_PORT"] = "29500"
		torch.distributed.init_process_group(
			"gloo", rank=rank, world_size=world_size)

	batch_size = 8
	sizes = [64, 32, 16]
	micro_batch_size = 2
	assert batch_size % micro_batch_size == 0
	num_micro_batches = batch_size // micro_batch_size

	torch.manual_seed(0)
	x_global = torch.randn(batch_size, sizes[0])
	y_global = torch.randn(batch_size, sizes[-1])

	mlp = MLP(micro_batch_size, sizes)
	mse_loss = MSELoss()
	loss = torch.zeros(1)

	schedule = "GPIPE"

	if schedule == "NAIVE":
		for micro_batch_idx in range(num_micro_batches):
			start = micro_batch_idx * micro_batch_size
			end = start + micro_batch_size
			x = x_global[start:end, :]
			y = y_global[start:end, :]
			z = mlp.forward(x)
		
			if rank == world_size - 1:
				loss += mse_loss.forward(z, y) * (1./num_micro_batches)
				dy = mse_loss.backward()
			else:
				loss = torch.empty(1)
				dy = None
			dx = mlp.backward(dy)

			if micro_batch_idx == 0:
				grad = mlp.layers[0].grad * (1./num_micro_batches)
			else:
				grad += mlp.layers[0].grad * (1./num_micro_batches)
	elif schedule == "GPIPE":
		for micro_batch_idx in range(num_micro_batches):
			start = micro_batch_idx * micro_batch_size
			end = start + micro_batch_size
			x = x_global[start:end, :]
			y = y_global[start:end, :]
			z = mlp.forward(x, micro_batch_idx)
		
			if rank == world_size - 1:
				loss += mse_loss.forward(z, y, micro_batch_idx) * (1./num_micro_batches)
			else:
				loss = torch.empty(1)
		
		for micro_batch_idx in range(num_micro_batches):
			start = micro_batch_idx * micro_batch_size
			end = start + micro_batch_size
			x = x_global[start:end, :]
			y = y_global[start:end, :]
			
			if rank == world_size - 1:
				dy = mse_loss.backward(micro_batch_idx)
			else:
				dy = None
			dy = mlp.backward(dy, micro_batch_idx)
		
			if micro_batch_idx == 0:
				grad = mlp.layers[0].grad * (1./num_micro_batches)
			else:
				grad += mlp.layers[0].grad * (1./num_micro_batches)
	else:
		raise ValueError("Unrecognized schedule")

	# Testing
	layers_torch = []
	for i in range(1, len(sizes)):
		layers_torch.append(nn.Linear(sizes[i-1], sizes[i], bias=False))
		layers_torch.append(nn.ReLU())
	with torch.no_grad():
		for i in range(0, len(layers_torch), 2):
			layers_torch[i].weight[:] = mlp.full_layers[i].weight.T
	z_torch = x_global
	for layer in layers_torch:
		z_torch = layer(z_torch)
	loss_torch = F.mse_loss(z_torch, y_global)
	loss_torch.backward()
	if rank == world_size-1:
		assert torch.allclose(loss, loss_torch)
	assert torch.allclose(grad, layers_torch[2 * rank].weight.grad.T, atol=1e-5)

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