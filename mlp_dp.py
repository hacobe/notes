"""MLP with data parallelism.

MLP duplicated across ranks except:
* Split the batch
* All-reduce the loss
* All-reduce the grad

# Sources

* https://github.com/siboehm/ShallowSpeed
* https://web.archive.org/web/20241229025020/https://siboehm.com/articles/22/data-parallel-training
"""
import torch
import torch.distributed
import torch.nn as nn
import torch.nn.functional as F
import multiprocessing
import os

def get_world_size():
	if torch.distributed.is_initialized():
		return torch.distributed.get_world_size()
	return 1

class Linear:

	def __init__(self, input_size, output_size):
		self.weight = torch.randn(input_size, output_size) * 0.1
		self.grad = None
		self.handle = None
		self._cache = {}

	def forward(self, x):
		self._cache["x"] = x
		return x @ self.weight

	def backward(self, dy):
		# [p, q] = [p, n] [n, q]
		self.grad = self._cache["x"].T @ dy

		world_size = get_world_size()
		if world_size > 1:
			self.grad *= (1/world_size)
			self.handle = torch.distributed.all_reduce(self.grad, async_op=True)

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
		loss = ((y - z)**2).mean()

		world_size = get_world_size()
		if world_size > 1:
			loss *= (1/world_size)
			torch.distributed.all_reduce(loss)

		return loss

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
		
		if get_world_size() > 1:
			for layer in reversed(self.layers):
				if hasattr(layer, "handle"):
					layer.handle.wait()

		return dy

def main(rank, world_size):
	if world_size > 1:
		os.environ["MASTER_ADDR"] = "127.0.0.1"
		os.environ["MASTER_PORT"] = "29500"
		torch.distributed.init_process_group(
			"gloo", rank=rank, world_size=world_size)

	global_batch_size = 8
	sizes = [64, 32, 16]
	batch_size = global_batch_size // world_size

	torch.manual_seed(0)
	x_global = torch.randn(global_batch_size, sizes[0])
	y_global = torch.randn(global_batch_size, sizes[-1])
	start = batch_size * rank
	end = start + batch_size
	x = x_global[start:end, :]
	y = y_global[start:end, :] 

	mlp = MLP(sizes)
	z = mlp.forward(x)

	mse_loss = MSELoss()
	loss = mse_loss.forward(z, y)
	
	dy = mse_loss.backward()
	dx = mlp.backward(dy)

	layers_torch = []
	for i in range(1, len(sizes)):
		layers_torch.append(nn.Linear(sizes[i-1], sizes[i], bias=False))
		layers_torch.append(nn.ReLU())
	with torch.no_grad():
		for i in range(0, len(layers_torch), 2):
			layers_torch[i].weight[:] = mlp.layers[i].weight.T
	z_torch = x_global
	for layer in layers_torch:
		z_torch = layer(z_torch)
	loss_torch = F.mse_loss(z_torch, y_global)
	loss_torch.backward()
	assert torch.allclose(loss, loss_torch)
	for i in range(0, len(layers_torch), 2):
		assert torch.allclose(mlp.layers[i].grad, layers_torch[i].weight.grad.T, atol=1e-5)

	if world_size > 1:
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