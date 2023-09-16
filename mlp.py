"""Implementation of an MLP using numpy layers.

Could do:
- Testing different shapes
- Test each layer individually
- Test for 1 layer using normal equation
- Multi-class softmax
- https://stackoverflow.com/questions/51976461/optimal-way-of-defining-a-numerically-stable-sigmoid-function-for-a-list-in-pyth
- biases
- x.exp() vs np.exp(x)
- torch.nn.functional
- BinaryCrossEntropy

See also:
- https://github.com/hacobe/notes/blob/main/MLP.ipynb
"""
import numpy as np


class Sigmoid:

	def __init__(self):
		self._cache = {}

	def forward(self, x):
		"""Forward pass for the sigmoid function.

		Args:
		- x: (*), where * means any number of dimensions.

		Returns:
		- y: (*), same shape as the input.

		Sources:
		- https://github.com/scipy/scipy/blob/main/scipy/special/_logit.h#L14
		- https://discuss.pytorch.org/t/where-is-the-real-implementation-of-codes-of-sigmoid/156417
		- https://github.com/pytorch/pytorch/blob/main/aten/src/ATen/native/cuda/UnarySpecialOpsKernel.cu#L123-L158
		- https://github.com/pytorch/pytorch/blob/main/aten/src/ATen/native/cpu/UnaryOpsKernel.cpp#L37-L68
		"""
		self._cache['y'] = 1./(1. + np.exp(-x))
		return self._cache['y']

	def backward(self, dy):
		"""Backward pass for the sigmoid function.

		Args:
		- dy: (*), where * means any number of dimensions.

		Returns:
		- dx: (*), same shape as the input.
		"""
		return dy * self._cache['y'] * (1. - self._cache['y'])


class ReLU:

	def __init__(self):
		self._cache = {}

	def forward(self, x):
		"""Forward pass for the ReLU function.

		Args:
		- x: (*), where * means any number of dimensions.

		Returns:
		- y: (*), same shape as the input.
		"""
		z = np.maximum(x, 0)
		self._cache['z'] = z
		return z

	def backward(self, dy):
		"""Backward pass for the ReLU function.

		Args:
		- dy: (*), where * means any number of dimensions.

		Returns:
		- dx: (*), same shape as the input.
		"""
		m = self._cache['z'] > 0
		dx = dy * m
		return dx


class Linear:

	def __init__(self, p_in, p_out, rng):
		self.weight = rng.normal(size=(p_in, p_out)) * (1/np.sqrt(p_in))
		self._cache = {}

	def forward(self, x):
		"""Forward pass for linear layer.

		Args:
		- x: (n, p_in)

		Returns:
		- y: (n, p_out)
		"""
		self._cache['x'] = x
		# [n, p_out] = [n, p_in] [p_in, p_out]
		return x @ self.weight

	def backward(self, dy):
		"""Backward pass for linear layer.

		Args:
		- dy: (n, p_out)

		Returns:
		- dw: (p_in, p_out)
		- dx: (n, p_in)
		"""
		# [p_in, p_out] = [p_in, n] [n, p_out]
		dw = self._cache['x'].T @ dy
		# [n, p_in] = [n, p_out] [p_out, p_in] 
		dx = dy @ self.weight.T
		return dw, dx


class BCELoss:

	def __init__(self):
		self._cache = {}
		self._eps = 1e-7

	def forward(self, p, y):
		p_clipped = np.clip(p, self._eps, 1 - self._eps)
		self._cache['y'] = y
		self._cache['p_clipped'] = p_clipped
		return np.mean(-y * np.log(p_clipped) - (1 - y) * np.log(1 - p_clipped))

	def backward(self):
		y = self._cache['y']
		n = len(y)
		return (1./n) * (-y/self._cache['p_clipped'] + (1-y)/(1-self._cache['p_clipped']))


class BCEWithLogitsLoss:
	"""Binary cross-entropy from logits.

	Sources:
	- https://pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html
	"""

	def __init__(self):
		self._sigmoid = Sigmoid()
		self._cache = {}

	def forward(self, z, y):
		"""Forward pass for binary cross-entropy from logits.

		The binary cross-entropy loss can be computed as follows:

		```
		loss = -1 * y * np.log(g(z)) - (1 - y) * np.log(1 - g(z))
		```

		where g(z) is the sigmoid function.

		We can write the sigmoid function as:

		```
		np.exp(0) / (np.exp(0) + np.exp(-z))
		```

		In this way, we can see that the sigmoid function is equivalent
		to the softmax over -z and 0.

		We can subtract off the maximum to avoid overflow:

		```
		t = np.maximum(-z, 0)
		np.exp(-t) / (np.exp(-t) + np.exp(-z-t))
		```

		Since we need to take the log of the sigmoid to compute cross-entropy,
		we can use the log-sum-exp trick:

		```
		z1 = np.zeros((len(z), 2))
		z1[:, 0] = -z[:, 0] - t[:, 0] 
		z1[:, 1] = -t[:, 0]
		y1 = np.zeros((len(y), 2))
		y1[:, 0] = 1 - y[:, 0]
		y1[:, 1] = y[:, 0]
		logprobs = z1 - np.log(np.sum(np.exp(z1), axis=1, keepdims=True))
		loss = -1 * np.sum(y1 * logprobs, axis=1, keepdims=True)
		```

		Here are the columns of logprobs:

		```
		1st column (y == 0): -z - t - np.log(np.exp(-z-t) + np.exp(-t))
		2nd column (y == 1): -t - np.log(np.exp(-z-t) + np.exp(-t))
		```

		We can write the loss as:

		```
		loss = -1 * y * (-t - np.log(np.exp(-z-t) + np.exp(-t))) - (1 - y) * (-z - t - np.log(np.exp(-z-t) + np.exp(-t)))
		```

		Simplifying further:

		```
		loss = yt + ylog(exp(-z-t) + exp(-t)) - (1-y)z + (1-y)t + (1-y)log(exp(-z-t) + exp(-t))
		     = yt + ylog(exp(-z-t) + exp(-t)) - z + yz + t -yt + log(exp(-z-t) + exp(-t)) -ylog(exp(-z-t) + exp(-t))
		     = -z + yz + t + log(exp(-z-t) + exp(-t))
		     = (1-y) * z + t + np.log(np.exp(-z-t) + np.exp(-t)) 
		```

		(we get the same loss if we don't subtract off the max, i.e., we set t to 0)
	
		Summarizing:

		```
		t = np.maximum(-z, 0)
		loss = (1-y) * z + t + np.log(np.exp(-z-t) + np.exp(-t))
		```

		A quick derivation:

		```
		loss = (-y log(g(z)) - (1-y)log(1-g(z)))
		g(z) = exp(0) / (exp(0) + exp(-z))
		t = np.maximum(-z, 0)
		g(z) = exp(-t) / (exp(-t) + exp(-z-t))
		1-g(z) = exp(-z-t) / (exp(-t) + exp(-z-t))
		-t - d
		-z-t - d
		-y (-t - d) - (1-y) (-z - t - d)
		yt + yd + (1-y)z + (1-y)t + (1-y)d
		yt + yd + z -zy + t - ty + d - dy
		z - zy + t + d
		(1-y)z + t + d
		```

		Args:
		- z: (n, 1). The logits.
		- y: (n, 1). The binary targets.

		Returns:
		- mean_loss: ()

		Sources:
		- https://stackoverflow.com/questions/66906884/how-is-pytorchs-class-bcewithlogitsloss-exactly-implemented
		- https://github.com/pytorch/pytorch/blob/main/aten/src/ATen/native/Loss.cpp#L356
		"""
		self._cache['z'] = z
		self._cache['y'] = y
		t = np.maximum(-z, 0)
		loss = (1-y) * z + t + np.log(np.exp(-z-t) + np.exp(-t))
		return np.mean(loss)

	def backward(self):
		"""Backward pass for binary cross-entropy from logits.

		For the i-th example:

		a = g(z)
		L = -y * log(a) - (1 - y) * log(1 - a)
	
		dLdz = dLda dadz
		dLda = -y/a + (1 - y)/(1 - a)
		dadz = a (1 - a)
		dLdz = a - y
		"""
		a = self._sigmoid.forward(self._cache['z'])
		n = len(self._cache['z'])
		return (1./n) * (a - self._cache['y'])


########
# Tests
########


import pytest
import torch


# http://ufldl.stanford.edu/tutorial/supervised/DebuggingGradientChecking/
_EPS = 1e-4


def test_bce_loss():
	rng = np.random.default_rng(seed=0)

	n = 10
	p_in = 4
	p_out1 = 3
	p_out2 = 1
	x = rng.normal(0, 1, (n, p_in))

	l1 = Linear(p_in, p_out1, rng)
	l2 = Linear(p_out1, p_out2, rng)
	g1 = ReLU()
	g2 = Sigmoid()
	p = g2.forward(l2.forward(g1.forward(l1.forward(x))))
	y = rng.binomial(1, p)

	loss = BCELoss()
	actual_loss = loss.forward(p, y)

	dx = loss.backward()
	dx = g2.backward(dx)
	actual_dw2, dx = l2.backward(dx)
	dx = g1.backward(dx)
	actual_dw1, _ = l1.backward(dx)

	# torch

	l1_ = torch.nn.Linear(p_in, p_out1, bias=False)
	l2_ = torch.nn.Linear(p_out1, p_out2, bias=False)
	with torch.no_grad():
	    l1_.weight[:] = torch.tensor(l1.weight.T).float()
	    l2_.weight[:] = torch.tensor(l2.weight.T).float()
	x_ = torch.tensor(x).float()
	p_ = torch.sigmoid(l2_(torch.relu(l1_(x_))))
	y_ = torch.tensor(y).float()
	loss_ = torch.nn.BCELoss()
	out = loss_(p_, y_)
	out.backward()
	expected_loss = out.tolist()
	expected_dw1 = np.array(l1_.weight.grad.T.tolist())
	expected_dw2 = np.array(l2_.weight.grad.T.tolist())

	np.testing.assert_almost_equal(actual_loss, expected_loss)
	np.testing.assert_almost_equal(actual_dw1, expected_dw1)
	np.testing.assert_almost_equal(actual_dw2, expected_dw2)

	# Gradient checking

	for w, actual_dw in [
	    (l1.weight, actual_dw1),
	    (l2.weight, actual_dw2)
	]:

		approx_dw = np.zeros(w.shape)
		for i in range(w.shape[0]):
			for j in range(w.shape[1]):
				# Why 2-sided gradient checking?
				# https://stats.stackexchange.com/questions/318380/why-is-two-sided-gradient-checking-more-accurate

				w[i,j] += _EPS
				p_plus = g2.forward(l2.forward(g1.forward(l1.forward(x))))
				l_plus = loss.forward(p_plus, y)
				w[i,j] -= _EPS

				w[i,j] -= _EPS
				p_minus = g2.forward(l2.forward(g1.forward(l1.forward(x))))
				l_minus = loss.forward(p_minus, y)
				w[i,j] += _EPS

				approx_dw[i,j] = (l_plus - l_minus) / (2 * _EPS)

		np.testing.assert_almost_equal(actual_dw, approx_dw)


def test_bce_loss_with_logits():
	rng = np.random.default_rng(seed=0)

	n = 10
	p_in = 4
	p_out1 = 3
	p_out2 = 1
	x = rng.normal(0, 1, (n, p_in))

	l1 = Linear(p_in, p_out1, rng)
	l2 = Linear(p_out1, p_out2, rng)
	g1 = ReLU()
	z = l2.forward(g1.forward(l1.forward(x)))

	p = Sigmoid().forward(z)
	y = rng.binomial(1, p)

	loss = BCEWithLogitsLoss()
	actual_loss = loss.forward(z, y)

	dx = loss.backward()
	actual_dw2, dx = l2.backward(dx)
	dx = g1.backward(dx)
	actual_dw1, _ = l1.backward(dx)

	# torch

	l1_ = torch.nn.Linear(p_in, p_out1, bias=False)
	l2_ = torch.nn.Linear(p_out1, p_out2, bias=False)
	with torch.no_grad():
	    l1_.weight[:] = torch.tensor(l1.weight.T).float()
	    l2_.weight[:] = torch.tensor(l2.weight.T).float()
	x_ = torch.tensor(x).float()
	z_ = l2_(torch.relu(l1_(x_)))
	y_ = torch.tensor(y).float()
	loss_ = torch.nn.BCEWithLogitsLoss()
	out = loss_(z_, y_)
	out.backward()
	expected_loss = out.tolist()
	expected_dw1 = np.array(l1_.weight.grad.T.tolist())
	expected_dw2 = np.array(l2_.weight.grad.T.tolist())

	np.testing.assert_almost_equal(actual_loss, expected_loss)
	np.testing.assert_almost_equal(actual_dw1, expected_dw1)
	np.testing.assert_almost_equal(actual_dw2, expected_dw2)

	# Gradient checking

	for w, actual_dw in [
	    (l1.weight, actual_dw1),
	    (l2.weight, actual_dw2)
	]:

		approx_dw = np.zeros(w.shape)
		for i in range(w.shape[0]):
			for j in range(w.shape[1]):
				# Why 2-sided gradient checking?
				# https://stats.stackexchange.com/questions/318380/why-is-two-sided-gradient-checking-more-accurate

				w[i,j] += _EPS
				z_plus = l2.forward(g1.forward(l1.forward(x)))
				l_plus = loss.forward(z_plus, y)
				w[i,j] -= _EPS

				w[i,j] -= _EPS
				z_minus = l2.forward(g1.forward(l1.forward(x)))
				l_minus = loss.forward(z_minus, y)
				w[i,j] += _EPS

				approx_dw[i,j] = (l_plus - l_minus) / (2 * _EPS)

		np.testing.assert_almost_equal(actual_dw, approx_dw)

