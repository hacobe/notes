# Checkpointing

**Checkpointing** is the process of periodically saving the state of a training run. A **checkpoint** is the object that contains this state. If training fails, we can restart it by loading the last saved checkpoint. For downstream applications, we can evaluate the performance of the model in each checkpoint and use the best one.

## What's in a checkpoint?

Take PyTorch Lightning's checkpoint as an example. The checkpoint is a Python object of type `Dict[str, Any]` ([source](https://github.com/Lightning-AI/lightning/blob/466f772e3e0ab2661329c9bca003ab7aeeccda4a/src/lightning/fabric/utilities/cloud_io.py#L63)). The keys include "epoch", "global_step", "optimizer_states", "lr_schedulers" and "state_dict" ([source](https://github.com/Lightning-AI/lightning/blob/466f772e3e0ab2661329c9bca003ab7aeeccda4a/src/lightning/pytorch/trainer/connectors/checkpoint_connector.py#L408)). The "optimizer_states" key might, for example, store the momentum and variance parameters of the AdamW optimizer. The "state_dict" key stores the model weights. In PyTorch, the `state_dict` of a `torch.nn.Module` is a Python `OrderedDict` that maps tensor names to tensor values ([source](https://web.archive.org/web/20231111180250/https://pytorch.org/tutorials/recipes/recipes/what_is_state_dict.html)).

For example:

```python
import collections
import torch

class Model(torch.nn.Module):

	def __init__(self):
		super(Model, self).__init__()
		self.linear = torch.nn.Linear(3, 2)

if __name__ == "__main__":
	torch.manual_seed(0)
	model = Model()
	expected = collections.OrderedDict([
		('linear.weight', torch.tensor([[-0.0043, 0.3097, -0.4752], [-0.4249, -0.2224,  0.1548]])),
		('linear.bias', torch.tensor([-0.0114,  0.4578]))
	])
	actual = model.state_dict()
	assert str(actual) == str(expected)
```

## How do we save and load a checkpoint?

Suppose the checkpoint only contains a model for simplicity.

We can save it as follows:

```python
torch.save(model.state_dict(), "path/to/file")
```

And later we can restore the model:

```python
model.load_state_dict(torch.load("path/to/file"))
```

Consider a tensor in the model's `state_dict` on a GPU. `torch.save` first copies this tensor to the CPU, serializes the tensor (i.e., converts the in-memory representation of the tensor to a format that can be stored), and writes the serialized bytes to disk (including the original location of the tensor).

`torch.load` reads the serialized bytes from disk, deserializes them and moves the restored tensor to its original location. The function's `map_location` argument can change this behavior. For example, if `map_location` is a dictionary, it maps each tensor's original location to a new location and moves the tensor from the CPU to this new location.

Internally, these methods use the `pickle` module. For more on the strengths and significant weaknesses of pickling, see this [blog post](https://web.archive.org/web/20231111182222/https://blog.nelhage.com/post/pickles-and-ml/).

## How do we save a checkpoint to S3 and load it from S3?

[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) (the AWS SDK for Python) provides methods for interacting with S3 (and other AWS services) in Python.

If we already have the checkpoint saved in a file, we can upload it to S3 as follows:

```python
import boto3

client = boto3.client("s3")
client.upload_file("path/to/file", "mybucket", "myobject")
```

If we have the checkpoint saved in S3, we can download it from S3:

```python
client.download_file("mybucket", "myobject", "path/to/file")
```

Alternatively, if we have the checkpoint in memory, we can upload it to S3 without first writing a file locally:

```python
client = boto3.client("s3")
fileobj = io.BytesIO()
torch.save(checkpoint, fileobj)
client.upload_fileobj(fileobj, "mybucket", "myobject")
```

And download it from S3 directly into memory:

```python
client = boto3.client("s3")
fileobj = io.BytesIO()
client.download_fileobj("mybucket", "myobject", fileobj)
fileobj.seek(0)
checkpoint = torch.load(fileobj)
```

`download_fileobj`, `download_file`, `upload_fileobj` and `upload_file` use the AWS SDK's transfer manager. The transfer manager uses multithreading for concurrency. An alternative is to use coroutines (see [here](https://github.com/pytorch/torchsnapshot/blob/0e601091d91e875f1b4ef0f79a3b6fb7b0069079/torchsnapshot/storage_plugins/s3.py#L51) for an example).

`boto3` also provides lower-level abstractions. The `get_object` method loads an S3 object into memory. It can also load a specific byte range of an object. The `put_object` method saves an object in memory to S3. We could also write our own uploader with `create_multipart_upload`, `complete_multipart_upload` and related methods.

### How do we address throttling errors?

S3 has rate limits. If we exceed those rate limits, we get 503 Slow Down errors.

Internally, S3 has an index that maps object URIs (the analogue of file paths in a file system) to the location of those objects on data servers. This index is divided into partitions, where each partition only contains object URIs that share a common prefix (note that a prefix can end at any character in the URI not just at a delimiter like '/'). S3 supports 3,500 PUT/COPY/POST/DELETE requests and 5,500 GET/HEAD requests per partition. When we create a new bucket or a new prefix within a bucket, the partition that stores our URIs may also include URIs created by other S3 users, so we have to share the request limit for the partition with those users. However, S3 monitors traffic and automatically creates new partitions for prefixes that get a lot of traffic. In this process of re-partitioning, we may see 503 errors.

There are a few [different strategies](https://web.archive.org/web/20231227235442/https://repost.aws/knowledge-center/http-5xx-errors-s3) for dealing with 503 errors. We can increase the chunk size and reduce the max concurrency we use when transferring checkpoints. We can use a retry mechanism with exponential backoff. We can also design our prefixes so that we distribute traffic evenly across the prefixes and ask S3 to create a partition for each prefix in advance.

## How do we save and load checkpoints in the distributed setting?

Consider training with data parallelism. We train with multiple processes (one for each for GPU). Each process places a copy of the model on its GPU. When we save the model, we only need to save a single copy. We could have just one of the processes save the model. Or we could distribute the work of saving the model across the processes, e.g., by having each process save a subset of the tensors that constitute the model. When we load the model, each process loads the model.

Consider training with model parallelism. Each process places a shard of the model on its GPU. Each process saves its shard, which naturally distributes the work of saving the model across processes. When we load the process, each process loads its shard. In this setting, we typically have multiple files in the checkpoint rather than a single file. For example, we could have one file for each shard. However, if the sharding strategy changes, then we either have to reorganize the checkpoint to reflect the new sharding strategy offline or do resharding online.

### TorchSnapshot

[TorchSnapshot](https://github.com/pytorch/torchsnapshot/tree/main) provides a higher-level abstraction for checkpointing with an emphasis on the distributed setting.

The `take` method takes as input a `path` to save the snapshot and the `app_state`, a dictionary that maps string keys to stateful object values. A **stateful object** is one where the state can be obtained via `.state_dict()` and restored via `.load_state_dict()`. For example:

```python
from torchsnapshot import Snapshot

class LinearModel(nn.Module):

	def __init__(self):
		super(LinearModel, self).__init__()
		self.fc = nn.Linear(4, 3, bias=False)

if __name__ == "__main__":
	torch.manual_seed(0)
	model = LinearModel()
	app_state = {
		"model": model,
	}
	snapshot = Snapshot.take(path="snapshot_dir", app_state=app_state)
```

The `restore` method takes `app_state` as an input:

```python
snapshot = Snapshot(path="/path/to/my/snapshot")
snapshot.restore(app_state=app_state)
```

Before restoring, the `app_state` might contain, for example, the model with a random initialization. The `restore` method restores "stateful objects in-place whenever possible to avoid creating unneccessary intermediate copies of the state" ([source](https://web.archive.org/web/20231228162142/https://pytorch.org/torchsnapshot/main/getting_started.html)).

Both the `take` and `restore` methods act as [collective operations](https://en.wikipedia.org/wiki/Collective_operation).

## How else can we improve the performance of checkpointing?

**Asynchronous checkpointing** does not block training when saving a checkpoint. It saves the checkpoint in another thread allowing training to proceed.

TorchSnapshot implements **zero-copy serialization** for most tensor types. Specifically, the library [serializes](https://github.com/pytorch/torchsnapshot/blob/0e601091d91e875f1b4ef0f79a3b6fb7b0069079/torchsnapshot/serialization.py#L200C12-L200C48))) a compatible tensor as `memoryview(tensor.numpy()).cast("b")`. With `memoryview`, we can write chunks of the tensor's bytes to storage without making a copy (more on `memoryview` [here](https://stackoverflow.com/questions/18655648/what-exactly-is-the-point-of-memoryview-in-python)). The library [deserializes](https://github.com/pytorch/torchsnapshot/blob/0e601091d91e875f1b4ef0f79a3b6fb7b0069079/torchsnapshot/serialization.py#L258C16-L258C71) the tensor as `torch.reshape(torch.frombuffer(memoryview(buf), dtype=dtype), shape)`. In this way, we serialize the tensor to the same format that we use to represent the tensor in memory and deserialization can then use the bytes read from disk.

**Pipelining device-to-host copy, serialization and storage I/O** speeds up checkpointing. Suppose we have 2 tensors. For each tensor, we need to perform those 3 operations. We could sequence those operations like this to complete storage of the tensors in 6 time steps:

```
                  t1 t2 t3 t4 t5 t6
DtoH copy          1        2 
Serialization         1        2      
Storage I/O              1        2
```

Or we could use pipelining to complete storage of the tensors in 4 time steps overlapping work:

```
                 t1 t2 t3 t4 t5 t6
DtoH copy         1  2      
Serialization        1  2
Storage I/O             1  2
```

**Lazy loading and layout control** gives us the ability to load individual components of a checkpoint without loading the entire checkpoint (see [here](https://github.com/huggingface/safetensors)). For example, the checkpoint format can include a small manifest that acts as a directory for the contents of the checkpoint.

Gemini recovers from **in-memory copies of the model state**: "Maintaining a high goodput3 at this scale would have been impossible using the conventional approach of periodic checkpointing of weights to persistent cluster storage. For Gemini, we instead made use of redundant in-memory copies of the model state, and on any unplanned hardware failures, we rapidly recover directly from an intact model replica. Compared to both PaLM and PaLM-2 (Anil et al., 2023), this provided a substantial speedup in recovery time, despite the significantly larger training resources being used." ([source](https://arxiv.org/pdf/2312.11805.pdf)).