# Megatron-style model parallelism

This post discusses the flavor of model parallelism introduced in [Shoeybi et al 2019](https://arxiv.org/abs/1909.08053).

A transformer is comprised of MLP and attention blocks.

Each MLP block consists of a linear layer followed by a nonlinearity followed by another linear layer followed by a dropout layer. A linear layer is just a matrix multiplication. The authors discuss 2 ways to parallelize a matrix multiplication as illustrated in the Python code below:

```python
import numpy as np

n = 4
p = 6
k = 8

X = np.random.randn(n, p)
A = np.random.randn(p, k)
Y = np.maximum(X @ A, 0)

# (1) Split A along its columns
#
#    A1   A2
# X [XA1 XA2]
A1 = A[:, :k//2]
A2 = A[:, k//2:]
Z1 = X @ A1
Z2 = X @ A2
np.testing.assert_almost_equal(np.maximum(np.concatenate([Z1, Z2], axis=1), 0), Y)

# (2) Split A alongs its rows
#        
#        A1
#        A2
# X1 X2 [X1A1 + X1A2]
X1 = X[:, :p//2]
X2 = X[:, p//2:]
A1 = A[:p//2, :]
A2 = A[p//2:, :]
Z1 = X1 @ A1
Z2 = X2 @ A2
np.testing.assert_almost_equal(np.maximum(Z1 + Z2, 0), Y)
```

The first approach is used for the first layer in the MLP block, because it allows the computation of the non-linearity to be done in parallel. The second approach is used for the second layer in the MLP block to keep the computation parallel as illustrated in the Python code below: 

```python
# Second layer
o = 10
B = np.random.randn(k, o)
O = Y @ B

Y1 = np.maximum(Z1, 0)
Y2 = np.maximum(Z2, 0)
B1 = B[:k//2, :]
B2 = B[k//2:, :]
O1 = Y1 @ B1
O2 = Y2 @ B2
np.testing.assert_almost_equal(O1 + O2, O)
```

(Note that I've switched the order of presentation of these approaches in the paper for purposes of exposition)

An all-reduce is applied before the dropout layer. Only 1 all-reduce is needed in the forward pass and only 1 is needed in the backward pass.

For the attention block:

"As shown in Figure 3b, for the self attention block we exploit inherent parallelism in the multihead attention operation, partitioning the GEMMs associated with key (K), query (Q), and value (V ) in a column parallel fashion such that the matrix multiply corresponding to each attention head is done locally on one GPU. This allows us to split per attention head parameters and workload across the GPUs, and
doesnt require any immediate communication to complete the self-attention. The subsequent GEMM from the output
linear layer (after self attention) is parallelized along its rows and takes the output of the parallel attention layer directly, without requiring communication between the GPUs."

The embeddings are also partitioned:

"The transformer language model has an output embedding with the dimension of hidden-size (H) times vocabularysize (v). Since the vocabulary size is on the order of tens of thousands of tokens for modern language models (for example, GPT-2 used a vocabulary size of 50,257), it is beneficial to parallelize the output embedding GEMM. However, in transformer language models, the output embedding layer shares weights with the input embedding, requiring modifications to both. We parallelize the input embedding weight matrix EH×v along the vocabulary dimension E = [E1, E2] (column-wise). Since each partition now only contains a portion of the embedding table, an all-reduce (g
operator) is required after the input embedding. For the output embedding, one approach is to perform the parallel GEMM [Y1, Y2] = [XE1, XE2] to obtain the logits, add an all-gather Y = all-gather([Y1, Y2]), and send the results to the cross-entropy loss function. However, for this case, the all-gather will communicate b × s × v elements (b is the batch-size and s is the sequence length) which is huge due to vocabulary size being large. To reduce the communication size, we fuse the output of the parallel GEMM [Y1, Y2] with the cross entropy loss which reduces the dimension to b × s. Communicating scalar losses instead of logits is a huge reduction in communication that improves the efficiency of our model parallel approach."

## Sources

* [Shoeybi et al 2019](https://arxiv.org/abs/1909.08053)

## Additional sources

* https://huggingface.co/docs/transformers/perf_train_gpu_many#tensor-parallelism
* https://lilianweng.github.io/posts/2021-09-25-train-large/#tensor-parallelism
