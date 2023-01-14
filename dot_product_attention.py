"""Implementation of dot-product attention.

Dimensional analysis:
softmax(Q K^T) V
Q: [n_q, d]
K: [n_kv, d]
V: [n_kv, v]
Q K^T: [n_q, d] [d, n_kv] = [n_q, n_kv]

Sources:
* [VSP+17](https://arxiv.org/abs/1706.03762)
* https://flax.readthedocs.io/en/latest/_modules/flax/linen/attention.html
* https://ajcr.net/Basic-guide-to-einsum/
"""
import flax.linen
import jax
import numpy as np
import scipy.special


def matrix_attention(query, key, value):
	"""
	query: qd
	key: kd
	value: ke
	"""
	return scipy.special.softmax(
		query @ key.T * (1. / np.sqrt(key.shape[-1])), axis=1) @ value


def tensor_attention(query, key, value):
	"""
	query: ...qhd
	key: ...khd
	value: ...khe

	same number of keys as values, but values could have
	a different dimension.
	"""

	# d_k == query.shape[-1] == key.shape[-1]
	d_k = key.shape[-1]

	# for each head and between each query and key,
	# we take a dot product of vectors of length d,
	# which results in a dimensionless scalar
	
	# Repeating letters between input arrays means that values
	# along those axes will be multiplied together.
	# The products make up the values for the output array.
	# Omitting a letter from the output means that values along that axis will be summed.
	# We can return the unsummed axes in any order we like

	attn_weights = np.einsum('...qhd,...khd->...hqk', query, key / np.sqrt(d_k))

	attn_weights = scipy.special.softmax(attn_weights, axis=-1)
	# output: (n, n_queries, num_heads, v_depth_per_head)
	# carry over ...hqk from building the attn_weights
	out = np.einsum('...hqk,...khe->...qhe', attn_weights, value)
	return out


def test_attention():
	np.random.seed(0)

	num_heads = 2
	n = 3
	dk = 4
	dv = 8
	d = 6

	n = 2
	n_queries = 3
	n_kv_pairs = 4
	num_heads = 5
	qk_depth_per_head = 6
	v_depth_per_head = 7

	query = np.random.randn(n, n_queries, num_heads, qk_depth_per_head)
	key = np.random.randn(n, n_kv_pairs, num_heads, qk_depth_per_head)
	value = np.random.randn(n, n_kv_pairs, num_heads, v_depth_per_head)

	# (n, n_queries, num_heads, v_depth_per_head)
	expected = flax.linen.dot_product_attention(query, key, value)
	expected = np.array(expected)

	actual = tensor_attention(query, key, value)
	
	assert actual.shape == expected.shape
	TOL = 1e-3
	assert (abs(actual - expected) < TOL).all()

	query = np.random.randn(1, 3, 1, 5)
	key = np.random.randn(1, 4, 1, 5)
	value = np.random.randn(1, 4, 1, 6) 
	expected2 = flax.linen.dot_product_attention(query, key, value)
	expected2 = np.array(expected2)

	# The equation in VSP+17 is when there is no batch dimension,
	# but multiple queries
	q = query[0, :, 0, :]
	k = key[0, :, 0, :]
	v = value[0, :, 0, :]
	actual2a = matrix_attention(q, k, v)
	assert expected2[0, :, 0, :].shape == actual2a.shape
	assert (abs(actual2a - expected2[0, :, 0, :]) < TOL).all()

	actual2b = tensor_attention(query, key, value)
	assert (abs(actual2b - expected2) < TOL).all()


if __name__ == "__main__":
	test_attention()