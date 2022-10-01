"""Implementation of BatchNorm.

Sources:
* https://pytorch.org/docs/stable/generated/torch.nn.BatchNorm1d.html#torch.nn.BatchNorm1d
"""

import numpy as np
import torch


class BatchNorm:

	def __init__(self, num_features, eps=1e-5, momentum=0.1):
		self.weight = np.ones((1, num_features))
		self.bias = np.zeros((1, num_features))
		self.running_mean = np.zeros((1, num_features))
		self.running_var = np.ones((1, num_features))
		self.eps = eps
		self.momentum = momentum
		self.training = True

	def __call__(self, x):
		assert len(x.shape) == 2

		if self.training:
			m = np.mean(x, axis=0, keepdims=True)
			v = np.var(x, axis=0, keepdims=True)
			# modify the running mean and variance at the end of the call
			# and only in training
			# = not +=
			self.running_mean = (1. - self.momentum) * m + self.momentum * self.running_mean
			self.running_var = (1. - self.momentum) * v + self.momentum * self.running_var
		else:
			m = self.running_mean
			v = self.running_var

		z = (x - m) / np.sqrt(v + self.eps)
		return self.weight * z + self.bias


if __name__ == "__main__":
	np.random.seed(0)
	num_features = 100
	x = np.random.randn(20, num_features)
	x_tensor = torch.FloatTensor(x)
	torch_batch_norm_layer = torch.nn.BatchNorm1d(num_features)
	batch_norm_layer = BatchNorm(num_features)
	expected = np.array(torch_batch_norm_layer(x_tensor).tolist())
	actual = batch_norm_layer(x)
	np.testing.assert_almost_equal(actual, expected, decimal=6)