# Attention

What is attention in the context of deep learning? We use attention as a layer in a neural network in the same way that we use convolution or matrix multiplication. The attention operation takes as input a query and a dictionary (a collection of key-value pairs) and returns the value in the dictionary with the key with most similar to the query. Another variant is to return an average of the values in the dictionary weighted by the similarity ("soft" attention) instead of returning one value ("hard" attention). Soft attention is probably more common, because it makes the attention operation differentiable and easier to optimize.

More concretely, consider a query vector $\textbf{q} \in \mathbb{R}^{d_q}$ and $n$ key-value pairs $(\textbf{k}_1, \textbf{v}_1), \dots, (\textbf{k}_n, \textbf{v}_n)$ with $\textbf{k}_i \in \mathbb{R}^{d_k}$ and $\textbf{v}_i \in \mathbb{R}^{d_v}$ (borrowing the notation from [here](https://classic.d2l.ai/chapter_attention-mechanism/attention.html)). The output $\textbf{o} \in \mathbb{R}^{d_v}$ has the same dimension as the value vectors and is computed for soft attention as follows: $\textbf{o} = \sum_{i=1}^n b_i \textbf{v}_i$, where $b_1, \dots, b_n = \mathrm{softmax}(a_1, \dots, a_n)$ and $a_i = f(\textbf{q}, \textbf{k}_i)$ for some similarity function $f$. We use the softmax function in order to force the scores sum to 1.

One common similarity function used is the dot product. In this case, we can write the attention operation for multiple queries succinctly as $\mathrm{softmax}(\textbf{Q} \textbf{K}^T) \textbf{V}$ where $\textbf{Q}$ is a $n_q \times d_{qk}$ matrix of queries, $\textbf{K}$ is a $n_{kv} \times d_{qk}$ matrix of the keys and $\textbf{V}$ is a $n_{kv} \times d_v$ matrix of the values. A variant of this dot product attention is used for the [Transformer](https://arxiv.org/pdf/1706.03762.pdf) architecture.

## Sources

* https://classic.d2l.ai/chapter_attention-mechanism/attention.html
* https://keras.io/api/layers/attention_layers/attention/
* https://www.tensorflow.org/tutorials/text/transformer#scaled_dot_product_attention
