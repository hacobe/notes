# Entropy

Entropy is a function that maps a discrete probability distribution to a real number.

A discrete probability distribution is a set of probabilities $p_1, \dots, p_K$ where $p_i$ is the probability of observing event $i$.

We define the entropy of the distribution $H(p_1, \dots, p_K) = - \sum_{i = 1}^K p_i log_2 (p_i)$.

In the case of $K = 1$, the plot of entropy against $p_1$ looks like an inverted U with a minimum at 0 and a maximum at 1 when $p_1 = 0.5$.

In general, entropy attains a maximum at $\log_2(K)$ when we set all $p_i = \frac{1}{K}$.

The closer entropy is to 0, the closer the probability distribution is to putting all the probabilility mass at one of the events. The closer entropy is to $log_2(K)$, the closer the distribution is to a uniform distribution over events, or a "flat prior".

Suppose we have just two events: A and B, i.e. $K = 2$, and we sample a sequence of $N$ events where at each step in the sequence we have $p$ probability of seeing A and $1 - p$ probability of seeing B.

There are $2^N$ possible sequences we could observe. However, many of these sequences are rare. In particular, for very large $N$, the event A will occur about $N \cdot p$ times in a sequence. The number of sequences where the event A occurs $N \cdot p$ times is just the number of ways to choose $N \cdot p$ positions out of the $N$ total positions in a sequence, which using Stirling's formula, is about $2^{N \cdot H(p, 1 - p)}$. In other words, entropy determines the size of the subset of "typical" sequences for a probability distribution. If entropy is 0, there's just 1 typical sequence, because the same event happens over and over again. If entropy is 1, then the number of typical sequences is equal to the total number of possible sequences.

## Sources

* [Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding)
* [Shannon's Source Coding Theorem](https://web.archive.org/web/20180825205721/http://mat.hjg.com.ar/tic/img/Shannon%20Source%20Coding%20Theorem.pdf)
* [A Mini-Introduction To Information Theory](https://arxiv.org/pdf/1805.11965.pdf)