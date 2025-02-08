"""MLP duplicated across ranks.

We implement the backward pass by hand, but use
torch so that it's easier to introduce collective communications
using torch.distributed.
"""
import torch
import torch.distributed
import torch.nn as nn
import torch.nn.functional as F
import multiprocessing
import os

class Linear:

	def __init__(self, input_size, output_size):
		self.weight = torch.randn(input_size, output_size) * 0.1
		self.grad = None
		self._cache = {}

	def forward(self, x):
		self._cache["x"] = x
		return x @ self.weight

	def backward(self, dy):
		# [p, q] = [p, n] [n, q]
		self.grad = self._cache["x"].T @ dy

		# [n, p] = [n, q] @ [q, p]
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
		self.layers = []
		for i in range(1, len(sizes)):
			self.layers.append(Linear(sizes[i-1], sizes[i]))
			self.layers.append(ReLU())

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
	sizes = [64, 32, 16]

	torch.manual_seed(0)
	x = torch.randn(batch_size, sizes[0])
	y = torch.randn(batch_size, sizes[-1])

	mlp = MLP(sizes)
	z = mlp.forward(x)

	mse_loss = MSELoss()
	loss = mse_loss.forward(z, y)
	
	dy = mse_loss.backward()
	dx = mlp.backward(dy)

	# Testing
	layers_torch = []
	for i in range(1, len(sizes)):
		layers_torch.append(nn.Linear(sizes[i-1], sizes[i], bias=False))
		layers_torch.append(nn.ReLU())
	with torch.no_grad():
		for i in range(0, len(layers_torch), 2):
			layers_torch[i].weight[:] = mlp.layers[i].weight.T
	z_torch = x
	for layer in layers_torch:
		z_torch = layer(z_torch)
	loss_torch = F.mse_loss(z_torch, y)
	loss_torch.backward()
	assert torch.allclose(loss, loss_torch)
	for i in range(0, len(layers_torch), 2):
		assert torch.allclose(mlp.layers[i].grad, layers_torch[i].weight.grad.T, atol=1e-5)

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