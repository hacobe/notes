"""MLP with tensor parallelism.

* ColumnParallelLinear gets all_reduce(z) in the forward pass
* RowParallelLinear gets all_reduce(dx) in the backward pass
* Use 4 layers to make sure test will fail if the all_reduces are removed
* Be careful about having enough decimals in the tests
* Scale the weights to avoid nans

# Sources

* https://arxiv.org/pdf/1909.08053
* https://github.com/NVIDIA/Megatron-LM/blob/076972e37420b5325c5fe06e7131be7d96f05b53/megatron/core/tensor_parallel/layers.py#L674
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

class ColumnParallelLinear:

	def __init__(self, input_size, output_size, all_gather):
		output_size_per_rank = output_size // get_world_size()
		self.weight = torch.randn(input_size, output_size_per_rank) * 0.1
		self._cache = {}
		self._all_gather = all_gather

	def forward(self, x):
		self._cache["x"] = x
		z = x @ self.weight

		if self._all_gather:
			z_parts = [torch.empty_like(z) for _ in range(get_world_size())]
			torch.distributed.all_gather(z_parts, z)
			z = torch.concat(z_parts, dim=1)

		return z

	def backward(self, dy):
		if self._all_gather:
			size = dy.shape[1] // get_world_size()
			start = size * get_rank()
			end = start + size
		else:
			start = 0
			end = dy.shape[1]

		self.grad = self._cache["x"].T @ dy
		dx = dy[:, start:end] @ self.weight.T

		if get_world_size() > 1:
			torch.distributed.all_reduce(dx)

		return dx

class RowParallelLinear:

	def __init__(self, input_size, output_size):
		input_size_per_rank = input_size // get_world_size()
		self.weight = torch.randn(input_size_per_rank, output_size) * 0.1
		self._cache = {}

	def forward(self, x):
		self._cache["x"] = x
		z = x @ self.weight

		if get_world_size() > 1:
			torch.distributed.all_reduce(z)

		return z

	def backward(self, dy):
		self.grad = self._cache["x"].T @ dy
		dx = dy @ self.weight.T
		return dx

class ReLU:

	def __init__(self):
		self._cache = {}

	def forward(self, x):
		self._cache["x"] = x
		return F.relu(x, 0)

	def backward(self, dy):
		mask = self._cache["x"] > 0
		return dy * mask

class MSELoss:

	def __init__(self):
		self._cache = {}

	def forward(self, y, z):
		self._cache["y-z"] = y-z
		return ((y - z)**2).mean() 

	def backward(self):
		shape = self._cache["y-z"].shape
		return 2 * self._cache["y-z"] * (1/shape[0]) * (1/shape[1])

class MLP:

	def __init__(self, sizes):
		assert len(sizes) == 5
		self.layers = [
			ColumnParallelLinear(sizes[0], sizes[1], all_gather=False),
			ReLU(),
			RowParallelLinear(sizes[1], sizes[2]),
			ReLU(),
			ColumnParallelLinear(sizes[2], sizes[3], all_gather=False),
			ReLU(),
			RowParallelLinear(sizes[3], sizes[4]),
			ReLU()
		]

	def forward(self, x):
		for layer in self.layers:
			x = layer.forward(x)
		return x

	def backward(self, dy):
		for layer in reversed(self.layers):
			dy = layer.backward(dy)
		return dy

def main(rank, world_size):
	if world_size > 1:
		os.environ["MASTER_ADDR"] = "127.0.0.1"
		os.environ["MASTER_PORT"] = "29500"
		torch.distributed.init_process_group(
			"gloo", rank=rank, world_size=world_size)

	batch_size = 8
	sizes = [64, 32, 16, 8, 4]

	torch.manual_seed(0)
	x = torch.randn(batch_size, sizes[0])
	y = torch.randn(batch_size, sizes[-1])

	torch.manual_seed(rank) # different weights
	mlp = MLP(sizes)
	z = mlp.forward(x)

	mse_loss = MSELoss()
	loss = mse_loss.forward(z, y)
	
	dy = mse_loss.backward()
	dx = mlp.backward(dy)

	# Testing
	layer_weights = []
	layer_grads = []
	for layer in mlp.layers:
		if layer.__class__.__name__ not in ("RowParallelLinear", "ColumnParallelLinear"):
			continue
		dim = 0 if layer.__class__.__name__ == "RowParallelLinear" else 1
		weights = [torch.empty_like(layer.weight) for _ in range(world_size)]
		torch.distributed.all_gather(weights, layer.weight)
		layer_weights.append(torch.concat(weights, dim=dim).float())

		grads = [torch.empty_like(layer.grad) for _ in range(world_size)]
		torch.distributed.all_gather(grads, layer.grad)
		layer_grads.append(torch.concat(grads, dim=dim).float())

	layers_torch = []
	for i in range(1, len(sizes)):
		layers_torch.append(nn.Linear(sizes[i-1], sizes[i], bias=False))
		layers_torch.append(nn.ReLU())
	with torch.no_grad():
		for i in range(0, len(layers_torch), 2):
			layers_torch[i].weight[:] = layer_weights[i // 2].T
	z_torch = x
	for layer in layers_torch:
		z_torch = layer(z_torch)
	loss_torch = F.mse_loss(z_torch, y)
	loss_torch.backward()

	assert torch.allclose(loss, loss_torch)
	assert torch.allclose(layer_grads[0], layers_torch[0].weight.grad.T, atol=1e-5)
	for i in range(0, len(layers_torch), 2):
		assert torch.allclose(layer_grads[i // 2], layers_torch[i].weight.grad.T, atol=1e-5)

	torch.distributed.destroy_process_group()

if __name__ == "__main__":
	world_size = 4
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