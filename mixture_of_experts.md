# Mixture of Experts

A Mixture of Experts layer has the following form:

$y = \sum_{i=1}^n G(x)_i E_i(x)$

where $y$ is the output of the layer, $x$ is the input, $G$ is a gating network, and $E_1, \dots, E_n$ are the expert networks.

A natural choice is "Softmax Gating", which is to set $G(x) = \mathrm{softmax}(Wx)$ where $W$ is a trainable weight matrix. However, one motivation for introducing expert networks is to have a network with a large number of parameters, but where only a few experts are involved in the computation for each input. The softmax involves all the experts in the computation for each input albeit with different weights placed on each expert.

Noisy Top-K Gating, an alternative to softmax gating, is introduced in Shazeer et al 2017:

$G(x) = \mathrm{softmax}(\mathrm{KeepTopK}(H(x), k))$

$H(x)_i = (Wx)_i + \mathrm{StandardNormal()} \cdot \mathrm{softplus}((Wx)_i)$

$\mathrm{KeepTopK}(v, k)_i = \begin{cases}v_i & \text{if } v_i \text{ is in the top } k \text{ elements of } v \\\\ -\infty & \text{otherwise } \end{cases}$

If we ignore the random noise term in $H(x)_i$, which helps with load balancing between experts (see Appendix A of Shazeer et al 2017), then this is just like "Softmax Gating" except that we only allow $k$ non-zero entries of $G(x)$. In other words, only $k$ experts are involved in the computation for each input and which experts are determined based on the input using trainable weights.

One potential issue with Noisy Top-K Gating is that it introduces "some theoretically scary discontinuities in the output of gating function", which Shazeer et al 2017 does to be a problem in practice. More recent work (Hazimeh et al 2021) has tried to address this issue by introducing a differentiable mechanism for gating ("DSelect-k"). I haven't looked closely at that paper, but note that "During inference, DSelect-k only needs to evaluate a subset of the experts, which can lead to computational savings. However, DSelect-k supports conditional training only partially. At the start of training, it uses all the available experts, so conditional training is not possible."

Fedus et al 2021 introduces the Switch Transformer, which uses a variant of the Mixture of Experts layer with Noisy Top-K Gating, K = 1 and an expert placed on each device: "We design models based off T5-Base and T5-Large (Raffel et al., 2019) to obtain up to 7x increases in pre-training speed with the same computational resources. These improvements extend into multilingual settings where we measure gains over the mT5-Base version across all 101 languages. Finally, we advance the current scale of language models by pre-training up to trillion parameter models on the 'Colossal Clean Crawled Corpus', and achieve a 4x speedup over the T5-XXL model."

They also perform some analysis of the scaling properties of experts in the style of the scaling laws work and include a section on "Future Work", which discusses some of the research challenges that remain for these models, e.g., "1. A significant challenge is further improving training stability for the largest models...2. Generally we find that improved pre-training quality leads to better downstream results (Appendix E), though we sometimes encounter striking anomalies...3. Perform a comprehensive study of scaling relationships to guide the design of architectures blending data, model and expert-parallelism...".

## Sources

* [Shazeer et al 2017](https://arxiv.org/pdf/1701.06538.pdf)
* [Hazimeh et al 2021](https://arxiv.org/pdf/2106.03760.pdf)
* [Fedus et al 2021](https://arxiv.org/pdf/2101.03961.pdf)