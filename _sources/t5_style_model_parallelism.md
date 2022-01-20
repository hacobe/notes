# T5-style model parallelism

Shallue et al 2019 defines model parallelism as "distributing parameters and computation across different processors for the same training examples".

I focus this post on a particular style of model parallelism, which I'm calling "T5-style model parallelism". It was introduced in Shazeer et al 2018 and used to train T5 in Raffel et al 2020.[^1] [Mesh-Tensorflow](https://github.com/tensorflow/mesh) is one implementation of it and [xmap](https://jax.readthedocs.io/en/latest/jax.experimental.maps.html) in JAX is another. EleutherAI released [GPT-J](https://github.com/kingoflolz/mesh-transformer-jax/#gpt-j-6b), a 6 billion parameter transformer, relying on xmap (see [here](https://github.com/kingoflolz/mesh-transformer-jax/blob/0f9b555fc1e7f8a94e77347b46dedaae5045811d/mesh_transformer/transformer_shard.py#L218)).

Suppose we want to parallelize some function applied to some input over some number of processors. For concreteness, suppose we have 8 processors and we want to parallelize the elementwise ReLU operation on a 32 x 256 matrix.

In T5-style model parallelism, we first define a "mesh", which is an array where each element is associated with a processor. In this case, our mesh will have 8 elements (one for each of the 8 processors), but we can choose its shape. We can choose a vector of length 8 or a 2 x 4 matrix or 4 x 2 matrix or a 2 x 2 x 2 tensor. The shape doesn't change the result of our computation, but it does change how the computation gets parallelized.

Suppose we choose a 2 x 4 matrix for our mesh. Conceptually, T5-style model parallelism says that to parallelize our computation we start by looping over the rows and columns of our mesh placing a slice of the input on the processor associated with row r and column c.

How do we determine which slice of the input to place on which processor? We define a mapping between axes of our input and axes of our mesh. Call the two axes of our input: "input_rows" and "input_cols" and the two axes of our mesh "mesh_rows" and "mesh_cols". If the mapping is empty, then we put X[:, :] on each processor, i.e., we copy X to each processor. If the mapping is {"input_rows": "mesh_rows"}, then we put X[(r * n):(r * n + n), :] on the r-th processor, where n is the size that evenly divides the "input_rows" axis into a slice for each of the processors in the "mesh_rows" axis. If the dictionary is {"input_rows": "mesh_rows", "input_cols": "mesh_cols"}, then we put X[(r * n):(r * n + n), (c * k):(c * k + k)] on the c-th processor, where k is the size that evenly divides the "input_cols" axis into a slice for each of the processors in the "mesh_cols" axis. In general, if an input axis is in the mapping it gets partitioned evenly over the corresponding mesh axis. Otherwise, all indices of that axis get included in the slice.

Let's say we specify the mapping {"input_rows": "mesh_rows", "input_cols": "mesh_cols"}, then a slice of shape [32/2, 256/4] = [16, 64] gets placed on each processor. We then execute the specified function in parallel on each processor's slice. In this case, the elementwise ReLU gets applied in parallel to each slice. Finally, we stitch together the slices from each processor to get the final result.

To recap, in T5-style model parallelism, we:

* Define a mesh (an array of processors) and a mapping between input axes and mesh axes
* Place a slice of the input on each processor (which slice is placed on which processor is determined by the mesh and the mapping)
* Run a specified function on each slice in parallel

## More complicated functions

It's fairly easy to see how ReLU gets parallelize in this way, but what about more complicated functions? For example, instead of ReLU, suppose we want to compute a sum of input over its "input_cols" axis in parallel. In this case, we produce 16x64 slices for each processor in the same way as described above. Then each processor applies the sum operation to its slice producing a vector of length 16. Here we arrange the shapes of each output on each processor just like our mesh:

	16	16	16	16
	16	16	16	16

We then need to apply another sum across processors on the reduced-out axis. That is we sum across the 4 columns in the mesh and we communicate the result to all the processors (this is the Allreduce collective communication primitive). Now, each processor in the same row of the mesh has a vector of length 16 with the same values. Any column can then be concatenated to get the correct output, which will be a vector of length 32 (I'm not sure of the logic for producing the correct output rather than an output of the same shape as the input but with a lot of duplicated data).

With a combination of broadcasting, elementwise operations, and reductions (e.g., sum, mean, max, etc), we can define a lot of different functions, including Einstein Summation, which includes matrix multiplication as a special case.

## Named arrays

A named array is like a NumPy array except that each axis has a name. We don't require named arrays to implement this style of parallelism, but they're natural to introduce in such an implementation and provide a lot of benefits. In fact, they're useful beyond just defining functions to be parallelized. For example, see the discussion from this [post](https://jax.readthedocs.io/en/latest/notebooks/xmap_tutorial.html) on broadcasting: "While the rule for broadcasting named axes might seem like an arbitrary extension of the NumPy model, it is actually consistent with it. Broadcasting first looks for pairs of dimensions it considers as equivalent in both operands. For all matched pairs, it asserts that both sizes are equal or one of them is 1. All unpaired dimensions are carried over to the result. Now, in the positional world the way NumPy broadcasting chooses to form the pairs is by right-aligning the shapes. But our axes are named, so there is a straightforward way of finding equivalent axes: just check their names for equality!"

## Sources

* [Shazeer et al 2018](https://arxiv.org/pdf/1811.02084.pdf)
* https://jax.readthedocs.io/en/latest/notebooks/xmap_tutorial.html
* [Raffel et al 2020](https://arxiv.org/pdf/1910.10683.pdf)
* [Xue et al 2021a](https://arxiv.org/pdf/2010.11934.pdf)
* [Xue et al 2021b](https://arxiv.org/abs/2105.13626.pdf)
* [Shallue et al 2019](https://www.jmlr.org/papers/volume20/18-789/18-789.pdf)

[^1]: I also think it was used to train mT5 ("The model architecture and training procedure that we use for mT5 closely follows that of T5." Xue et al 2021a) and ByT5 ("The design stays relatively close to mT5 ..." Xue et al 2021b).
