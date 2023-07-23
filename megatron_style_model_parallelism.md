# Megatron-style model parallelism

## Intro

This post discusses the flavor of model parallelism introduced in [Shoeybi et al 2019](https://arxiv.org/abs/1909.08053).

Suppose we have multiple GPUs. The number of GPUs is called the **world size**. Each GPU receives an ID in [0, 1, ..., world size - 1]. This ID is called the **rank** of the GPU.

We launch the same program on each GPU.

## Data loading

Let B be the batch size and S be the sequence length.

In the program, the logic for loading a B x S batch of token indices looks like:[^1]

```python
if rank == 0:
	# load batch
	batch = ...
else:
	pass

torch.distributed.broadcast(batch, src=0)
```

The GPU with rank 0 loads the data. That GPU then sends the data to all the other GPUs using a broadcast operation. Each other GPU blocks until it has received the data from source GPU.

## Embedding lookup

Let V be the vocab size and E be the embedding dimension.

We want to initialize a V x E embedding matrix.

Each GPU initializes its own slice of the embedding matrix by partitioning across the vocab dimension like this:

```python
per_partition_vocab_size = vocab_size // world_size
start_index = rank * per_partition_vocab_size
end_index = start_index + per_partition_vocab_size
# init (per_partition_vocab_size, embedding_dim) embedding matrix
# responsible for the token indices in [start_index, end_index).
...
```

We pass the full batch into the embedding layer on each GPU. We zero out the parts of the resulting B x S x E embedded tensor that do not "belong" to that GPU (i.e., correspond to token indices outside of the rank's index range). Each GPU then calls an All-Reduce sum, which computes the sum of the embedded tensor on each GPU and then broadcasts the summed B x S x E tensor to all the GPUs. In this way, each GPU gets the embedded inputs.

## Self-attention

At this point, we have a copy of the B x S x E embedded input tensor on each GPU.

We want to matrix multiply it by a E x 3E matrix to get a B x S x 3E tensor.[^2] We need 3E, because we need E for the query, E for the key and E for the value tensor.

Each GPU initializes a E x (3E/world_size) slice of the E x 3E matrix, i.e., we partition the E x 3E matrix column-wise.

On each GPU, we matrix multiply the embedded input tensor by this slice to get a B x S x (3E / world_size) tensor, which we then split into the B x S x (E / world_size) query, key and value tensors.

Each GPU has its own query, key and value tensors that we feed into the self-attention mechanism to get a B x S x (E / world_size) tensor.

We want to matrix multiply this tensor by a E x E tensor (a linear layer after attention).

Each GPU initializes a (E / world_size) x E tensor, i.e., we partition the E x E matrix row-wise.

On each GPU, we matrix multiply the B x S x (E / world_size) output of the self-attention mechanism by the (E / world_size) x E matrix to get a B x S x E tensor.

We then compute an All-Reduce sum across the B x S x E tensors on each GPU.

## MLP

At this point, we have a copy of the B x S x E tensor output of the self-attention layer on each GPU.

We now want to feed it through an MLP that consists of a linear layer with a GeLU activation and a linear layer with no activation. The code below illustrates how we partition both layers:

```python
import numpy as np
np.random.seed(0)
B = 2
S = 3
E = 4
F = 6
world_size = 2

X = np.random.randn(B, S, E)

# First layer (column-wise partitioning)
W11 = np.random.randn(E, F // world_size)
W12 = np.random.randn(E, F // world_size)
Z11 = X @ W11
Z12 = X @ W12
A11 = np.maximum(Z11, 0)  # ReLU
A12 = np.maximum(Z12, 0)  # ReLU

# Second layer (row-wise partitioning)
W21 = np.random.randn(F // world_size, E)
W22 = np.random.randn(F // world_size, E)
Z21 = A11 @ W21
Z22 = A12 @ W22
Z2 = Z21 + Z22 # All-Reduce sum

# Tests
W1 = np.concatenate([W11, W12], axis=1)
Z1 = X @ W1
expected_A1 = np.maximum(Z1, 0)
np.testing.assert_almost_equal(expected_A1, np.concatenate([A11, A12], axis=2))
W2 = np.concatenate([W21, W22], axis=0)
expected_Z2 = expected_A1 @ W2
np.testing.assert_almost_equal(expected_Z2, Z2)
```

## Cross-entropy loss

In the last layer, we want to matrix multiply the B x S x E output of the last MLP layer by a E x V matrix to get a B x S x V logits tensor and then apply a softmax.

We could partition the E x V matrix column-wise. If the world size was 2, we could initialize a E x (V // 2) matrix called W_a on 1 GPU and a E x (V // 2) matrix called W_b on the other GPU. We would then compute Z_a = X @ W_a on the first GPU and Z_b = X @ W_b on the second GPU in parallel. In order to compute the softmax, we would need to first perform an All-Gather operation on each GPU to get Z_a and Z_b on both GPUs. We could then concatenate Z_a and Z_b on each GPU to get Z on each GPU. At this point, we could calculate the cross-entropy loss on each GPU. This requires communicating the B x S x V logits across the GPUs.

Instead, we apply the cross-entropy loss in parallel and only have to communicate the B x S matrix of losses.

In more detail: "The transformer language model has an output embedding with the dimension of hidden-size (H) times vocabularysize (v). Since the vocabulary size is on the order of tens of thousands of tokens for modern language models (for example, GPT-2 used a vocabulary size of 50,257), it is beneficial to parallelize the output embedding GEMM. However, in transformer language models, the output embedding layer shares weights with the input embedding, requiring modifications to both. We parallelize the input embedding weight matrix EH×v along the vocabulary dimension E = [E1, E2] (column-wise). Since each partition now only contains a portion of the embedding table, an all-reduce (g operator) is required after the input embedding. For the output embedding, one approach is to perform the parallel GEMM [Y1, Y2] = [XE1, XE2] to obtain the logits, add an all-gather Y = all-gather([Y1, Y2]), and send the results to the cross-entropy loss function. However, for this case, the all-gather will communicate b × s × v elements (b is the batch-size and s is the sequence length) which is huge due to vocabulary size being large. To reduce the communication size, we fuse the output of the parallel GEMM [Y1, Y2] with the cross entropy loss which reduces the dimension to b × s. Communicating scalar losses instead of logits is a huge reduction in communication that improves the efficiency of our model parallel approach."

## Sources

* [Shoeybi et al 2019](https://arxiv.org/abs/1909.08053)
* https://github.com/NVIDIA/Megatron-LM/tree/main/megatron
* https://huggingface.co/docs/transformers/perf_train_gpu_many#tensor-parallelism
* https://lilianweng.github.io/posts/2021-09-25-train-large/#tensor-parallelism

## Footnotes

[^1]: The broadcast is [here](https://github.com/NVIDIA/Megatron-LM/blob/cd2537d444792b487b1ab5a6fa685e09c9957409/pretrain_gpt.py#L46). It calls the function [here](https://github.com/NVIDIA/Megatron-LM/blob/cd2537d444792b487b1ab5a6fa685e09c9957409/megatron/core/tensor_parallel/data.py#L65).
[^2]: The weight matrix is initialized [here](https://github.com/NVIDIA/Megatron-LM/blob/main/megatron/model/transformer.py#L442). It calls the function [here](https://github.com/NVIDIA/Megatron-LM/blob/main/megatron/core/tensor_parallel/layers.py#L477).
