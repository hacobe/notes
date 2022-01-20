# ZeRO-Offload

ZeRO-Offload is a strategy for training large language models on a single GPU (up to around 13 billion parameters on a single NVIDIA V100). It can get near linear speedups with multiple GPUs (up to 128 GPUs) and with some additional model parallelism can train larger models as well (up to 70 billion parameters on 16 V100s).

I first describe how it works on a single GPU (see "4.1 Single GPU Schedule" and Figure 5 in Ren et al 2021)

The main problem we have training a large model on a single GPU is that we run out of memory.[^1] For each parameter in our model, we need to store its weight and its gradient. If we're training with ADAM, we also need to store a momentum scalar and variance scalar for each parameter. If we use float32 precision, then we need 4 * 4 bytes = 16 bytes for each parameter. For a 10 billion parameter model, we need 160GB of memory, which far exceeds the 80GB available on e.g. a NVIDIA A100 GPU.

We have enough memory for a 10 billion parameter model if we train on CPU, but CPU is a lot slower than GPU. The idea of ZeRO-Offload is to store the weights, momentums and variances on the CPU and a copy of the weights on the CPU and then each training step to:

* Execute the forward and backward pass on the GPU to get the gradients (the most expensive part of the computation)
* Copy those gradients to the CPU and delete them from the GPU to free up memory
* Perform the ADAM update on the CPU
* Replace the old weights on the GPU with the new ones from the CPU

Before deleting the gradients, we need 2 * 4 bytes = 8 bytes for each parameter on the GPU. A 10 billion parameter model is right at the memory capacity for a single GPU. We can use mixed precision training and instead use float16 for the weights and gradients on the GPU, which cuts the memory in half.

See the "ZeRO-Offload colab" for a simple implementation in JAX. This implementation does include the additional optimizations the authors include for speeding up CPU execution time: "First, we implement a fast CPU Adam optimizer using high performance computing techniques offering significant speedup over state-of-art Pytorch implementation. Second, we develop a one-step delayed parameter update schedule that overlaps the CPU parameter update computation with the forward and backward computation on the GPU, hiding the CPU execution time when enabled."

## Sources

* [ZeRO-Offload colab](https://colab.research.google.com/drive/178-XgMkUShVn0MYoCde-IyPl1S3MDqqV#scrollTo=ZOMhIyPi4zDy)
* [Ren et al 2021](https://arxiv.org/pdf/2101.06840.pdf)

[^1]: "We consider the memory consumption due to model states for large transformer models such as Megatron-LM (8 billion) [28], T5 (11 billion) [20], and Turing-NLG [25] (17.2 billion). They are trained with float-16 mixed precision training [16] and Adam optimizer [13]. Mixed precision training often keeps two copies of the parameters, one in float-16 (fp16) and the other in float-32 (fp32). The gradients are stored in fp16. In addition to the parameters and gradients, the Adam optimizer keeps track of the momentum and variance of the gradients. These optimizer states are stored in fp32. Therefore, training a model in mixed precision with the Adam optimizer requires at least 2 bytes of memory for each fp16 parameter and gradient, and 4 byte of memory for each fp32 parameter, and the moementum and variance of each gradient. In total, a model with M parameters requires 16 x M bytes of memory. Therefore, the model states for Megatron-LM, T5 and Turing-NLG require 128 GB, 176 GB and 284 GB, respectively, which are clearly beyond the memory capacity of even the current flagship NVIDIA A100 GPU with 80 GB of memory."
