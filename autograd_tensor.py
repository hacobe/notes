"""Implementation of a Tensor with autograd and MLP example.

Sources:
* https://github.com/karpathy/micrograd/blob/master/micrograd/engine.py
* https://github.com/minitorch/minitorch/tree/main/minitorch
* https://minitorch.github.io

See also:
* autograd_scalar.py
* mlp.py
* https://github.com/hacobe/notes/blob/main/MLP.ipynb
"""
import numpy as np


class Tensor:

	def __init__(self, arr, children=()):
		self.arr = arr
		self.children = children
		self.grad = np.zeros(arr.shape)
		self._backward = lambda: None

	def __matmul__(self, other):
		# [n, k] = [n, p] @ [p, k]
		parent = Tensor(self.arr @ other.arr, children=(self, other))

		def _backward():
			# [n, p] += [n, k] x [k, p]
			self.grad += parent.grad @ other.arr.T
			# [p, k] += [p, n] x [n, k]
			other.grad += self.arr.T @ parent.grad
		parent._backward = _backward

		return parent

	def __add__(self, other):
		if isinstance(other, float) or isinstance(other, int):
			other = Tensor(np.zeros_like(self.arr) + other)

		parent = Tensor(arr=self.arr + other.arr, children=(self, other))

		def _backward():
			self.grad += parent.grad
			other.grad += parent.grad
		parent._backward = _backward

		return parent

	def __radd__(self, other):
		return self + other

	def __mul__(self, other):
		if isinstance(other, float) or isinstance(other, int):
			other = Tensor(np.ones_like(self.arr) * other)

		parent = Tensor(arr=self.arr * other.arr, children=(self, other))

		def _backward():
			self.grad += parent.grad * other.arr
			other.grad += parent.grad * self.arr
		parent._backward = _backward

		return parent

	def __rmul__(self, other):
		return self * other

	def __neg__(self):
		return self * Tensor(-1 * np.ones_like(self.arr))

	def __sub__(self, other):
		return self + (-other)

	def __rsub__(self, other):
		return other + (-self)

	def relu(self):
		parent = Tensor(arr=np.maximum(self.arr, 0), children=(self,))

		def _backward():
			self.grad += parent.grad * (self.arr > 0)
		parent._backward = _backward

		return parent

	def log(self):
		parent = Tensor(arr=np.log(self.arr), children=(self,))

		def _backward():
			self.grad += parent.grad * (1./self.arr)
		parent._backward = _backward

		return parent	

	def exp(self):
		a = np.exp(self.arr)
		parent = Tensor(arr=a, children=(self,))

		def _backward():
			self.grad += parent.grad * a
		parent._backward = _backward

		return parent

	def sigmoid(self):
		a = 1/(1 + np.exp(-self.arr))
		parent = Tensor(arr=a, children=(self,))

		def _backward():
			self.grad += parent.grad * a * (1 - a)
		parent._backward = _backward

		return parent

	def sum(self):
		parent = Tensor(arr=self.arr.sum(keepdims=True), children=(self,))

		def _backward():
			self.grad += parent.grad
		parent._backward = _backward

		return parent

	def backward(self):

		def dfs(u, visited, order):
			if u in visited:
				return
			visited.add(u)
			for v in u.children:
				dfs(v, visited, order)
			order.append(u)

		dfs_order = []
		visited = set()
		dfs(self, visited, dfs_order)
		topo_order = dfs_order[::-1]

		self.grad = np.array([[1.0]])
		for u in topo_order:
			u._backward()


class Linear:

	def __init__(self, in_features, out_features, rng):
		self.weight = Tensor(rng.normal(size=(in_features, out_features)))

	def forward(self, x):
		return x @ self.weight


class Model:

	def __init__(self, p_in, p_out1, p_out2, rng, sigmoid):
		self.l1 = Linear(p_in, p_out1, rng)
		self.l2 = Linear(p_out1, p_out2, rng)
		self._sigmoid = sigmoid

	def forward(self, x):
		x = self.l1.forward(x)
		x = x.relu()
		x = self.l2.forward(x)
		if self._sigmoid:
			x = x.sigmoid()
		return x


class BCELoss:

	def forward(self, p, y):
		losses = (-y * p.log() - (1 - y) * (1 - p).log())
		return (1./p.arr.shape[0]) * losses.sum()


class BCEWithLogitsLoss:

	def forward(self, z, y):
		t = (-z).relu()
		losses = (1-y) * z + t + ((-z-t).exp() + (-t).exp()).log()
		return (1./z.arr.shape[0]) * losses.sum()

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
	x = Tensor(rng.normal(0, 1, (n, p_in)))

	model = Model(p_in, p_out1, p_out2, rng, sigmoid=True)
	p = model.forward(x)
	y = Tensor(rng.binomial(1, p.arr))

	loss = BCELoss()
	out = loss.forward(p, y)
	out.backward()
	actual_loss = out.arr[0,0]
	actual_dw1 = model.l1.weight.grad
	actual_dw2 = model.l2.weight.grad

	# torch

	l1_ = torch.nn.Linear(p_in, p_out1, bias=False)
	l2_ = torch.nn.Linear(p_out1, p_out2, bias=False)
	with torch.no_grad():
	    l1_.weight[:] = torch.tensor(model.l1.weight.arr.T).float()
	    l2_.weight[:] = torch.tensor(model.l2.weight.arr.T).float()
	x_ = torch.tensor(x.arr).float()
	p_ = torch.sigmoid(l2_(torch.relu(l1_(x_))))
	y_ = torch.tensor(y.arr).float()
	loss_ = torch.nn.BCELoss()
	out_ = loss_(p_, y_)
	out_.backward()
	expected_loss = out_.tolist()
	expected_dw1 = np.array(l1_.weight.grad.T.tolist())
	expected_dw2 = np.array(l2_.weight.grad.T.tolist())

	np.testing.assert_almost_equal(actual_loss, expected_loss)
	np.testing.assert_almost_equal(actual_dw1, expected_dw1)
	np.testing.assert_almost_equal(actual_dw2, expected_dw2)

	# Gradient checking

	for w, actual_dw in [
	    (model.l1.weight, actual_dw1),
	    (model.l2.weight, actual_dw2)
	]:

		approx_dw = np.zeros(w.arr.shape)
		for i in range(w.arr.shape[0]):
			for j in range(w.arr.shape[1]):
				# Why 2-sided gradient checking?
				# https://stats.stackexchange.com/questions/318380/why-is-two-sided-gradient-checking-more-accurate

				w.arr[i,j] += _EPS
				p_plus = model.forward(x)
				l_plus = loss.forward(p_plus, y)
				w.arr[i,j] -= _EPS

				w.arr[i,j] -= _EPS
				p_minus = model.forward(x)
				l_minus = loss.forward(p_minus, y)
				w.arr[i,j] += _EPS

				approx_dw[i,j] = (l_plus.arr - l_minus.arr) / (2 * _EPS)

		np.testing.assert_almost_equal(actual_dw, approx_dw)


def test_bce_with_logits_loss():
	rng = np.random.default_rng(seed=0)

	n = 10
	p_in = 4
	p_out1 = 3
	p_out2 = 1
	x = Tensor(rng.normal(0, 1, (n, p_in)))

	model = Model(p_in, p_out1, p_out2, rng, sigmoid=False)
	z = model.forward(x)
	y = Tensor(rng.binomial(1, z.sigmoid().arr))

	loss = BCEWithLogitsLoss()
	out = loss.forward(z, y)
	out.backward()
	actual_loss = out.arr[0,0]
	actual_dw1 = model.l1.weight.grad
	actual_dw2 = model.l2.weight.grad

	# torch

	l1_ = torch.nn.Linear(p_in, p_out1, bias=False)
	l2_ = torch.nn.Linear(p_out1, p_out2, bias=False)
	with torch.no_grad():
	    l1_.weight[:] = torch.tensor(model.l1.weight.arr.T).float()
	    l2_.weight[:] = torch.tensor(model.l2.weight.arr.T).float()
	x_ = torch.tensor(x.arr).float()
	z_ = l2_(torch.relu(l1_(x_)))
	y_ = torch.tensor(y.arr).float()
	loss_ = torch.nn.BCEWithLogitsLoss()
	out_ = loss_(z_, y_)
	out_.backward()
	expected_loss = out_.tolist()
	expected_dw1 = np.array(l1_.weight.grad.T.tolist())
	expected_dw2 = np.array(l2_.weight.grad.T.tolist())

	np.testing.assert_almost_equal(actual_loss, expected_loss)
	np.testing.assert_almost_equal(actual_dw1, expected_dw1)
	np.testing.assert_almost_equal(actual_dw2, expected_dw2)

	# Gradient checking

	for w, actual_dw in [
	    (model.l1.weight, actual_dw1),
	    (model.l2.weight, actual_dw2)
	]:

		approx_dw = np.zeros(w.arr.shape)
		for i in range(w.arr.shape[0]):
			for j in range(w.arr.shape[1]):
				# Why 2-sided gradient checking?
				# https://stats.stackexchange.com/questions/318380/why-is-two-sided-gradient-checking-more-accurate

				w.arr[i,j] += _EPS
				z_plus = model.forward(x)
				l_plus = loss.forward(z_plus, y)
				w.arr[i,j] -= _EPS

				w.arr[i,j] -= _EPS
				z_minus = model.forward(x)
				l_minus = loss.forward(z_minus, y)
				w.arr[i,j] += _EPS

				approx_dw[i,j] = (l_plus.arr - l_minus.arr) / (2 * _EPS)

		np.testing.assert_almost_equal(actual_dw, approx_dw)
