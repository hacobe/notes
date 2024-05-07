# Data loading

## What is data loading?

**Data loading** is the process of preparing a batch of examples for a machine learning model to consume. It can include reading data from disk or from an object store like S3 as well as processing that data to get it into a format compatible with the model.

## Overlapping data loading and matrix multiplication

Consider training a model with gradient descent. We define the model. We move it to the accelerator. We start a training loop. At each step of the training loop, we load data, move the data to the location of the model, use the model to make a prediction for each example in the batch (the forward pass), compute the gradient of the loss with respect to the model weights for each prediction (the backward pass) and update the model weights using the computed gradients (the optimizer step).

The time to complete a training step is the sum of the time to load data and the time to complete the forward pass, backward pass and the optimizer step. However, we load the data using the CPU and execute the forward pass, the backward pass and the optimizer step on the accelerator. Because these two phases of the training step use different resources, we can overlap them.

In the code below, we benchmark a simulation of data loading overlapped with the forward pass (overlap = True) and a simulation of synchronous data loading (overlap = False). This is an approach similar to the one taken in [nanoGPT](https://github.com/karpathy/nanoGPT/blob/5156fef93c15ef7e0dcdb35b4581a1dcd9c4d72e/train.py#L302).

```python
import torch
import torch.nn.functional as F
import time

def main(overlap):
	num_steps = 100
	batch_size = 2**15
	feature_dim = 2**14
	duration_data_loading = 8/1000.
	lr = 0.1

	torch.manual_seed(0)
	device = "cuda" if torch.cuda.is_available() else "cpu"

	# If we used this block of code to simulate data loading,
	# then we wouldn't be able to illustrate overlapping, because
	# this code is executed on the GPU (assuming it's available).
	# If instead we executed this code on the CPU, it would be very
	# slow, because it's both slow to initialize a tensor on a CPU
	# and slow to do matrix multiplication on a CPU.
	w_true = torch.randn(1, feature_dim, device=device)
	X = torch.randn(batch_size, feature_dim, device=device)
	noise = 0.1 * torch.randn(batch_size, 1, device=device)
	y = X @ w_true.T + noise

	model = torch.nn.Linear(feature_dim, 1, bias=False)
	model = model.to(device)

	optimizer = torch.optim.SGD(model.parameters(), lr)

	sum_duration = 0
	sum_duration_non_data_loading = 0
	for step in range(num_steps):
		start_time = time.time()

		if overlap:
 			# We first execute the forward pass using a previously prepared batch
 			# on the GPU. This work does not block the CPU. During the forward pass
 			# on the GPU, the CPU continues on to preparing the next batch
 			# and moving it to the GPU, which we simulate with the sleep command.
 			# In this way, we overlap data loading on the CPU with matrix multiplication
 			# on the GPU.
			yhat = model(X)
			loss = F.mse_loss(yhat, y)

			# CPU work to simulate data loading.
			time.sleep(duration_data_loading)

			loss.backward()
			optimizer.step()
			optimizer.zero_grad()
			# Block until the GPU work is done.
			# We could also just print the loss here.
			torch.cuda.synchronize() 
		else:
			# CPU work to simulate data loading.
			time.sleep(duration_data_loading)

			start_time_non_data_loading = time.time()
			optimizer.zero_grad()
			yhat = model(X)
			loss = F.mse_loss(yhat, y)
			loss.backward()
			optimizer.step()
			# Block until the GPU work is done.
			# We could also just print the loss here.
			torch.cuda.synchronize()
			duration_non_data_loading += time.time() - start_time_non_data_loading

		sum_duration += time.time() - start_time

	print(f"Step time (ms) with overlap {overlap}: {1000*sum_duration/num_steps:.0f}")
	if not overlap:
		print(f"Non-data loading time (ms) with overlap {overlap}: {1000*sum_duration_non_data_loading/num_steps:.0f}")

if __name__ == "__main__":
	main(True)
	main(False)
```

Running it in a Colab with a T4 GPU yields:

```
Step time (ms) with overlap True: 17
Step time (ms) with overlap False: 24
Non-data loading time (ms) with overlap False: 16
```

The step time without overlapping is 24ms, or the sum of the data loading time (8ms) and the non-data loading time (16ms). The step time with overlapping is 17ms, which is almost equal to the non-data loading time, because most of the data loading work happens during the forward pass. As a point of comparison for these times, multiplying two 3000x3000 matrices takes ~14ms in JAX ([source](https://web.archive.org/web/20240502160147/https://jax.readthedocs.io/en/latest/notebooks/quickstart.html)).

## PyTorch's Dataset and DataLoader

Some functionality related to data loading appears in a lot of different applications. For example, many applications require **batching**, i.e., grouping individual examples together so that they can be processed by the model together. PyTorch provides the **torch.utils.data.DataLoader** class to implement some of this common functionality. At a minimum, the DataLoader is initialized with an instance of a **torch.utils.data.Dataset**. We can also specify the batch size at initialization. We can then iterate through the resulting DataLoader object.[^1] At each iteration, we get a batch of examples.

There are 2 styles of torch.utils.data.Dataset: map-style and iterable-style. We focus on the map-style dataset (for more on each style, see [here](https://web.archive.org/web/20231123052045/https://pytorch.org/docs/stable/data.html#dataset-types)). In a map-style dataset, we define a dataset by implementing `__getitem__`, which takes an index and returns an example, and `__len__`, which returns the length of the dataset. Here is an example of using the DataLoader with a map-style dataset: 

```python
import torch

class Dataset(torch.utils.data.Dataset):

	def __init__(self):
		self._data = {
			0: (1, 2),
			1: (7, 8),
			2: (14, 15),
			3: (21, 22)
		}

	def __getitem__(self, index):
		x, y = self._data[index]
		return x, y

	def __len__(self):
		return len(self._data)

if __name__ == "__main__":
	dataset = Dataset()
	dataloader = torch.utils.data.DataLoader(dataset, batch_size=2)
	# tensor([1, 7]) tensor([2, 8])
	# tensor([14, 21]) tensor([15, 22])
	for x, y in dataloader:
		print(x, y)
```

Now revisit training a model using gradient descent, using Dataset and Dataloader and simulating both the data loading and the accelerator work:

```python
import time
import torch

class SimDataset(torch.utils.data.Dataset):

	def __init__(self, num_examples, duration):
		self._num_examples = num_examples
		self._duration = duration

	def __getitem__(self, index):
		time.sleep(self._duration)

	def __len__(self):
		return self._num_examples

# local lambda function is not pickable.
def identity(x):
	return x

def main(num_workers, duration_data_loading, duration_non_data_loading):
	num_examples = 100
	dataset = SimDataset(num_examples, duration_data_loading)
	data_loader = torch.utils.data.DataLoader(dataset, collate_fn=identity, num_workers=num_workers)

	# Instead of:
	#
	# it = iter(data_loader)
	# while True:
	#	try:
	#		next(it)
	#	except StopIteration:
	#		break
	#	...
	#
	# We could just do:
	#
	# for _ in data_loader:
	#	...
	#
	# But we want to measure the time it takes to load the data.
	it = iter(data_loader)

	sum_duration_data_loading = 0
	sum_duration = 0
	num_completed_steps = 0

	while True:
		start_time = time.time()

		start_time_data_loading = time.time()
		try:
			next(it)
		except StopIteration:
			break
		sum_duration_data_loading += time.time() - start_time_data_loading

		# Simulate the accelerator work.
		time.sleep(duration_non_data_loading)

		sum_duration += time.time() - start_time

		num_completed_steps += 1

	print(f"Num workers: {num_workers}")
	print(f"Step time (ms): {1000*sum_duration/num_completed_steps:.0f}")
	print(f"Data loading time (ms): {1000*sum_duration_data_loading/num_completed_steps:.0f}")

if __name__ == "__main__":
	for num_workers in range(5):
		main(num_workers, duration_data_loading=50/1000., duration_non_data_loading=15/1000.)
		print()
```

Running it on laptop yields:

```
Num workers: 0
Step time (ms): 73
Data loading time (ms): 55

Num workers: 1
Step time (ms): 61
Data loading time (ms): 43

Num workers: 2
Step time (ms): 35
Data loading time (ms): 17

Num workers: 3
Step time (ms): 27
Data loading time (ms): 10

Num workers: 4
Step time (ms): 30
Data loading time (ms): 12
```

The step time and the data loading time decrease with the number of workers until we have 4 workers. There's some overhead to managing multiple workers. Also, this simulation of data loading is compute-bound rather than I/O bound, so the performance gains are limited by the number of cores that the machine has (my laptop has 4 performance cores and 4 efficiency cores).

When the number of workers is 0, then the step time is roughly equal to the sum of the data loading time (55ms) and the non-data loading time (15ms). It's not exactly equal, because using the DataLoader has some overhead. When the number of workers is 1 or more, the program loads data in separate threads, which means that the data loading work is overlapped with the accelerator work as in the first example. The first example uses the CPU and the GPU to overlap work, while the second example uses multithreading to overlap work.

### Tuning the DataLoader

The DataLoader has several arguments that we can tune for performance. For example:

* batch_size
* num_workers: Use multiple threads to parallelize reads and transforms.
* pin_memory: If enabled, then the DataLoader puts data into pinned memory rather than pageable memory. Pinned memory consists of virtual pages that are marked so that they do not get paged out. GPUs can only access data from pinned memory. By having the DataLoader transfer the data from pageable to pinned memory ahead of time, we avoid that blocking training. If we pin memory, we call also move the tensor to the GPU asynchronously: `x = x.pin_memory().to(device, non_blocking=True)`. Note that we do not always want to use memory pinning (see discussion [here](https://discuss.pytorch.org/t/how-to-prefetch-data-when-processing-with-gpu/548/18)).
* prefetch_factor: "Number of batches loaded in advance by each worker. 2 means there will be a total of 2 * num_workers batches prefetched across all workers" (PyTorch [docs](https://web.archive.org/web/20231123052045/https://pytorch.org/docs/stable/data.html))

## Benchmarking

The ultimate benchmark is to take the specific model of interest, determine the largest batch size using a specific set of hardware (usually we want the largest batch size that does not result in an out-of-memory error) and measure the **training time** or quantiles of the train step time over training. We could also measure how these times vary with the number of workers in order to find the best value for the number of workers.

To benchmark a generic data loader (rather than data loading for a specific application), we could repeat the benchmarks described above, but for different models on different hardware (with batch sizes tuned to the specific hardware).

A less expensive benchmark is to measure the **throughput** of the data loader, e.g., the number of examples processed per second. The downside of this benchmark is that the relationship between throughput and training time is not always straightforward. For throughput benchmarks, we can measure quantiles of the time it takes to load a batch over loading multiple batches. We can also vary the batch size and the number of workers.

If data loading requires downloading a dataset to disk, then another important metric is **start-up time**, i.e., the time it takes to start training. We can also test how this metric scales with the number of nodes used in training (does each node download the dataset to disk in parallel?).

Peak CPU **memory usage** might also be important to measure. Does each process involved in training load the entire dataset into memory? Does each process memory map the dataset? We can also test how this metric varies with the size of the dataset and the number of nodes used in training.

## Other topics

* object store vs cloud file system
	* Though we may be able to perform random access operations on a cloud file system and that cloud file system might have various caching mechanisms, we may want to stick to sequential access to have more predictable performance.
	* These systems vary in maturity. Some cloud file systems do not have the same availability and durability guarantees that e.g. S3 has. Even if a cloud file system rarely has an outage, it may have slow downs.
* shuffling and performance
	* If we don't have fast random access, then shuffling the data during training can substantially increase training time. Instead we could pre-shuffle (i.e., shuffle the data before training) and then read the data sequentially or we could read a block of data sequentially and then shuffle the samples within the block. However, it may impact model quality to shuffle the dataset in blocks rather than to shuffle the entire dataset at the example level.
* preprocessing vs processing on-the-fly
* resuming data loading from a specific step of training
* efficient file formats

## See also

* DataLoader.ipynb
* nemo_data_loading.md
* memory_mapping.md

## Sources

* https://github.com/stas00/ml-engineering/tree/23e54c136f6c85d6ec6e6e284e232efe7d33ec69/storage
* https://github.com/pytorch/examples/blob/f82f5626b6432b8d0b08d58cc91f3bdbb355a772/mnist/main.py
* https://github.com/karpathy/nanoGPT/blob/5156fef93c15ef7e0dcdb35b4581a1dcd9c4d72e/train.py
* https://discuss.pytorch.org/t/how-to-prefetch-data-when-processing-with-gpu/548/18
* https://github.com/Lightning-AI/pytorch-lightning/issues/17410
* https://discuss.pytorch.org/t/most-efficient-way-of-loading-data/42073/5
* https://discuss.pytorch.org/t/dataloader-much-slower-than-manual-batching/27014
* https://github.com/awslabs/s3-connector-for-pytorch/tree/91b36e9592eceb5ddfc0fc58c1ea1e97c5c70761/s3torchbenchmarking
* https://github.com/pytorch/data/issues/500
* https://web.archive.org/web/20240507143039/https://pytorch.org/blog/announcing-cpp/
* https://github.com/earth-mover/dataloader-demo/blob/4434ac40172668639fff83da6061ac07aee7a94f/main.py
* https://web.archive.org/web/20240507144455/https://earthmover.io/blog/cloud-native-dataloader
* https://web.archive.org/web/20240507144611/https://docs.aws.amazon.com/sagemaker/latest/dg/model-access-training-data.html
* https://web.archive.org/web/20240507144607/https://aws.amazon.com/blogs/machine-learning/speed-up-training-on-amazon-sagemaker-using-amazon-efs-or-amazon-fsx-for-lustre-file-systems/
* https://web.archive.org/web/20240507144639/https://www.tensorflow.org/guide/data_performance#best_practice_summary
* https://web.archive.org/web/20231123052045/https://pytorch.org/docs/stable/data.html
* https://web.archive.org/web/20231123051959/https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/

## Footnotes

[^1]: An instance of the DataLoader class is an **iterable**, i.e., an instance of a class that implements the `__iter__` method. The `__iter__` method returns an **iterator**, i.e., an instance of a classs that implements the `__next__` method. For more detail on the distinction between an iterable and an iterator, see https://stackoverflow.com/questions/9884132/what-are-iterator-iterable-and-iteration.
