# Data parallelism

Shallue et al 2019 gives the following definition of data parallelism: "For our purposes, data parallelism refers to distributing training examples across multiple processors to compute gradient updates (or higher-order derivative information) and then aggregating these locally computed updates".

I focus on synchronous stochastic gradient descent (a particular example of data parallelism).[^1] Synchronous SGD works as follows:

* It divides a batch of training examples across processors
* Computes the gradient for the partial batch on each processor
* Sums those gradients across processors to get the gradient for the entire batch
* Uses the gradient for the entire batch to update the weights on each processor

**Data parallelism reduces training time by enabling larger batch sizes.** How does this form of data parallelism change the cost required to achieve a given level of out-of-sample error? Section 1.1 of Shallue et al 2019 has a good discussion of how to think about this question, which I lean on here. A natural way to measure cost is in terms of training time. We can decompose training time into the product of the number of training steps and the average time per step. If the time it takes to communicate gradients between processors is negligible (e.g., in a TPU), then we can increase the batch size (the number of examples processed per training step) by adding more processors while keeping the average time per step constant.[^2] In this case, the batch size is determined by the number of processors and the differences in training time as we increase the batch size is determined only by differences in the number of steps. The key question then becomes: what is the relationship between batch size and the number of steps required to achieve a given level of out-of-sample error? This is not an obvious question. For example, smaller batch sizes may provide a regularizing effect that improves out-of-sample error (see pg. 276 of Goodfellow et al 2016 for a discussion of factors going into choice of batch size). With a wide range of experiments, Shallue et al 2019 shows empirically that "...for each workload (model, training algorithm, and data set), increasing the batch size initially decreases the required number of training steps proportionally, but eventually there are diminishing returns until finally increasing the batch size no longer changes the required number of training steps." [^3] Note that they retune the learning rate whenever they change the batch size.

Here's a simple implementation in JAX that can run in a colab connected to a TPU (note that I explicitly put data on different devices to highlight the transfer of data even though pmap handles this automatically).

	import jax.tools.colab_tpu
	jax.tools.colab_tpu.setup_tpu()

	import jax
	import jax.numpy as jnp
	import numpy as np

	np.random.seed(0)
	p = 32
	w = np.random.random((p, 1))
	# Send a copy of the weights to each of the 8 TPU cores.
	# (we could also create the same weights on each device). 
	w = jax.device_put_replicated(w, devices=jax.devices())

	def loss(w, x, y):
	  yhat = jnp.dot(x, w)
	  return jnp.mean((yhat - y)**2)

	def update(w, x, y):
	  grads = jax.grad(loss)(w, x, y)
	  # This operation sums the grads on each device, stores the result on the host,
	  # and then broadcasts that result to all devices.
	  # The next command doesn't execute until each device has the new grads.
	  grads = jax.lax.psum(grads, axis_name='num_devices')
	  step_size = 0.1
	  return w - step_size * grads

	n_steps = 4
	batch_size_per_device = 16
	for _ in range(n_steps):
	  # Simulate reading in a batch for each device.
	  x_shards = []
	  y_shards = []
	  for _ in range(len(jax.devices())):
	  	x_shards.append(np.random.random((batch_size_per_device, p)))
	  	y_shards.append(np.random.random((batch_size_per_device, 1)))

	  # Send a different batch to each device.
	  x = jax.device_put_sharded(x_shards, devices=jax.devices())
	  y = jax.device_put_sharded(y_shards, devices=jax.devices())

	  # Run the update operation on each device in parallel.
	  # In particular, device i calls update(w[i], x[i], y[i])
	  w = jax.pmap(update, axis_name='num_devices', in_axes=0, out_axes=0)(w, x, y)

## Sources

* [Shallue et al 2019](https://www.jmlr.org/papers/volume20/18-789/18-789.pdf)
* [Mao 2019](https://leimao.github.io/blog/Data-Parallelism-vs-Model-Paralelism/)
* [Goodfellow et al 2016](https://www.deeplearningbook.org/contents/optimization.html)
* [Nado et al 2021](https://arxiv.org/pdf/2102.06356.pdf)
* https://github.com/google/jax/blob/main/examples/spmd_mnist_classifier_fromscratch.py
* https://jax.readthedocs.io/en/latest/jax-101/06-parallelism.html

[^1]: I follow Shallue et al 2019 in this: "We restrict our attention to synchronous SGD because of its popularity and advantages over asynchronous SGD (Chen et al., 2016)."

[^2]: Alternatively, we can keep the number of steps constant by fixing the batch size and using the additional processors to decrease the average time per step. However, then we may divide the batch so finely that we don't fully use each processor. Also, average time per step depends on hardware where number of steps does not.

[^3]: A more recent paper (Nado et al 2021) by some of the same authors maintains the same conclusion: "See Shallue et al. 2019 for a survey of the effects of data parallelism on neural network training. Once these effects are taken into account, there is no strong evidence that increasing the batch size degrades the maximum achievable performance on any workload."