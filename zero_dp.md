# ZeRO-DP

[Rajbhandari et al 2020](https://arxiv.org/pdf/1910.02054.pdf) introduces ZeRO-DP and ZeRO-R. This post focuses on ZeRO-DP.

We start with the same setup as data parallelism.

ZeRO-DP then applies 3 optimizations:
* Optimizer state partitioning
* Gradient partitioning
* Parameter partitioning

This [HuggingFace post](http://web.archive.org/web/20221214174255/https://huggingface.co/docs/transformers/perf_train_gpu_many) explains ZeRO-DP with all the optimizations applied.

We partition the parameters horizontally across the parallel processes (vertical partitioning places a single layer on each node, while horizontal partitioning places some parameters from each layer on each node).

We bring the parameters from all the nodes together to compute the forward pass and remove the parameters from other nodes when we no longer need them. An analogous communication and computation happens in the backward pass.

The HuggingFace post makes the following analogy:

*To me this sounds like an efficient group backpacking weight distribution strategy:*

*1. person A carries the tent
2. person B carries the stove
3. person C carries the axe*

*Now each night they all share what they have with others and get from others what they don’t have, and in the morning they pack up their allocated type of gear and continue on their way*

Another way to sum it up is that ZeRO-DP is "just the usual DataParallel (DP), except, instead of replicating the full model params, gradients and optimizer states, each GPU stores only a slice of it. And then at run-time when the full layer params are needed just for the given layer, all GPUs synchronize to give each other parts that they miss".