"""MapReduce.

# Background

MapReduce is (1) a programming model and (2) a runtime system for executing
programs expressed in the programming model on distributed systems.

The programming model has a user specify a **map** function,
which takes a key-value pair as input and returns a list of key-value
pairs as output, and a **reduce** function, which takes a key and a list
of values associated with that key as input and returns a list of new values
(typically 0 or 1 values) associated with that key.

# Problem

The user has some input files stored in a distributed file system.

The user also has access to a cluster of `N+1` machines (1 machine will run
the leader and the remaining `N` machines will run the worker).

We assume that the distributed file system has divided the input files into
`M` chunks (`M >> N`) and evenly distributed those chunks across the `N`
worker machines.[^1]

The user provides the M chunks (where each chunk has a machine and a path):[^2]

```
[
	{
		"path": "path/to/some/file",
		"machine": 0
	},
	{
		"path": "path/to/some/other/file",
		"machine": 0
	},
	{
		"path": "path/to/another/file",
		"machine": 1
	},
	...
]
```

The user also provides the `map` function, the `reduce` function and `R`, i.e.,
the number of reduce partitions, which we'll discuss later.

The runtime system starts a copy of the program on each machine
(in a multiprocessing simulation, each process spawned corresponds to one machine). One of those copies runs as the leader and the rest run as workers.

The leader creates a map task for each of the `M` input files and a reduce task
for the `R` reduce partitions.

The leader runs an RPC server that exposes a `heartbeat` method.

Each worker runs a loop that repeatedly calls the `heartbeat` method and
executes the task returned in the response. Note that the worker only calls
the `heartbeat` method when it is idle.[^3]

For example, the worker sends:

```
{
	"machine": "some/machine/id",
	"completed_tasks_since_last_heartbeat": []
}
```

The leader responds with a task:

```
{
	"id": "some/task/id",
	"type": "MAP",
	"status": IN_PROGRESS,
	"chunk": {
		"machine": "some/machine/id",
		"path": ""path/to/the/chunk/on/the/machine""
	},
	"num_reduce_partitions": R
}
```

We assume that the leader always provides an input file stored on the worker
machine, so the worker can just read the file from its local disk.[^4]

The worker applies the `map` function to produce intermediate key-value pairs.
It then writes each intermediate key-value pair to a file on local disk based
on the task ID and `hash(key) % R`, where `R` is the number of reduce partitions
provided by the user.[^5] Because the filename includes the task ID, it will not
get overwritten by another map task.

In the next heartbeat, the worker can send a request like:

```
{
	"machine": "some/machine/id",
	"completed_tasks_since_last_heartbeat": [
		"some/task/id"
	]
}
```

Once all the map tasks finish, the leader starts responding to the next worker
heartbeat with a reduce task.[^6] For example:

```
{
	"id": "another/task/id",
	"type": "REDUCE",
	"status": IN_PROGRESS,
	"partition": "some/partition/id",
	"input_files": [
		{
			"uri": "http://localhost:someport",
			"path": path/to/first/file/in/reduce/partion",
		},
		{
			"uri": "http://localhost:someport",
			"path": path/to/second/file/in/reduce/partion",
		},
		...
		{
			"uri": "http://localhost:anotherport",
			"path": path/to/last/file/in/reduce/partion",
		}
	]
}
```

Each worker runs an RPC server that exposes a `read_file` method. A worker
assigned a reduce task calls this `read_file` method to read each reduce
file for a partition (the  "shuffle" phase).[^7] In a simulation, we can
just read from disk with a comment to think of the read like a RPC call.

Once it has all the data, it sorts by key either in-memory or using an
external sort (the "sort" phase). In a simulation, we can just read all
the data into memory and group by key.

It then iterates over the sorted intermediate key-value pairs
applying the `reduce` function to the values associated with each key.
It then writes out the final output file for the partition to the
distributed file system.

When all the reduce tasks finish, the leader sends an "exit" task to
each worker on the next heartbeat. Once it has sent all the exit tasks,
then the leader exits and control flow is returned to the user.

Footnotes:

[^1]: In reality, the distributed file system divides each input file
      into chunks and the runtime system organizes all of those chunks into
      M logical partitions based on a user-specified partition size.

[^2]: In reality, the distributed file system has the metadata about which
      machine stores which chunk. The user just provides the maximum number of
      machines to use. The leader runs an RPC server that exposes a `register`
      method. Each worker runs an RPC client that calls the `register` method
      when it starts up. In this way, the leader discovers the worker machines.

[^3]: If a task takes a long time, then it might delay the heartbeat.
      It might be ok with small enough tasks to just assume that if the tasks
      takes a long time then we want to mark the machine as unresponsive.
      Instead, we could have a separate heartbeat thread.

[^4]: In reality, the input files are in a distributed file system and the
      leader tries to pick a worker machine close to where the file is stored.

[^5]: In reality, the worker buffers the intermediate key-value pairs in memory
      and writes them out when the buffer limit has been reached.

[^6]: In reality, the shuffle phase can be overlapped with the map phase.

[^7]: Another option might be to just write the intermediate key-value pairs
      to the distributed file system, but that's slower than the RPC approach.

# Notes

* We overlap the map and shuffle phase by splitting the REDUCE
  task into a REDUCE_READ and REDUCE_GROUP.
* Do we need a locking mechanism? No, because everything is going through the
  leader and the SimpleXMLRPCServer is single-threaded.
* If we use extra memory instead of looping through all the tasks in the tasks dict,
  then we have to be careful to update that state every time we change the tasks dict.
* ConnectionRefusedError: [Errno 61] Connection refused: Wait for the leader to
  start
* Check loops from yield vs return
* It's a little tricky to start the leader before the worker if the leader is
  not in a separate process


# Sources

* https://pdos.csail.mit.edu/6.824/papers/mapreduce.pdf
* https://web.stanford.edu/class/cs345d-01/rl/MRvsPDBMS.pdf
* https://web.archive.org/web/20241217161758/https://cs162.org/static/hw/hw-map-reduce-rs/docs/example/
* https://mrjob.readthedocs.io/en/latest/job.html#mrjob.job.MRJob.__init__
* https://stackoverflow.com/questions/30893970/reducer-starts-before-mapper-has-finished
"""
import collections
import hashlib
import jsonlines
import multiprocessing
import time
import xmlrpc.server

BASE_DIR = "tmp"
INTERMEDIATE_KV_TEMPLATE = "tmp/{task_id}-{partition}.jsonl"
OUTPUT_SPLIT_TEMPLATE = "tmp/out_{partition}.jsonl"
OUTPUT_FILE = "tmp/out.jsonl"

MAP = "MAP"
REDUCE_READ = "REDUCE_READ"
REDUCE_GROUP = "REDUCE_GROUP"
SLEEP = "SLEEP"
EXIT = "EXIT"

IDLE = "IDLE"
IN_PROGRESS = "IN_PROGRESS"
COMPLETED = "COMPLETED"

def _identity_combiner(key, values):
	yield values

class Leader:

	def __init__(self, chunks, num_reduce_partitions):
		self._task_id_to_task = {}
		for chunk in chunks:
			map_task_id = len(self._task_id_to_task)
			self._task_id_to_task[map_task_id] = {
				"id": map_task_id,
				"type": MAP,
				"status": IDLE,
				"chunk": chunk,
				"num_reduce_partitions": num_reduce_partitions
			}
			for partition in range(num_reduce_partitions):
				task_id = len(self._task_id_to_task)
				self._task_id_to_task[task_id] = {
					"id": task_id,
					"type": REDUCE_READ,
					"status": IDLE,
					"map_task_id": map_task_id,
					"partition": partition,
					"input_file": "",
					"machine": -1
				}
		for partition in range(num_reduce_partitions):
			task_id = len(self._task_id_to_task)
			self._task_id_to_task[task_id] = {
				"id": task_id,
				"type": REDUCE_GROUP,
				"status": IDLE,
				"partition": partition,
				"machine": -1
			}

		self._completed = False
		self._num_workers = len(set([c["machine"] for c in chunks]))
		self._num_reduce_partitions = num_reduce_partitions

	def heartbeat(self, machine, completed_tasks):
		for task_id in completed_tasks:
			task = self._task_id_to_task[task_id]
			task["status"] = COMPLETED
			if task["type"] != MAP:
				continue
			# Update all the partitions for that map task with the path
			# to the intermediate KV file.
			for partition in range(self._num_reduce_partitions):
				for t in self._task_id_to_task.values():
					if t["type"] == REDUCE_READ and \
						t["map_task_id"] == task["id"] and \
						t["partition"] == partition and \
						(not t["input_file"]):
						input_file = INTERMEDIATE_KV_TEMPLATE.format(
							task_id=task["id"], partition=partition)
						t["input_file"] = input_file

		all_tasks_completed = True
		for task in self._task_id_to_task.values():
			if task["status"] != COMPLETED:
				all_tasks_completed = False
				break

		if all_tasks_completed:
			self._num_workers -= 1
			if self._num_workers == 0:
				self._completed = True
			return {"type": EXIT}

		map_tasks_completed = True
		for task in self._task_id_to_task.values():
			if task["type"] == MAP and task["status"] != COMPLETED:
				map_tasks_completed = False
				break

		partition_to_reduce_reads_completed = {}
		for partition in range(self._num_reduce_partitions):
			partition_to_reduce_reads_completed[partition] = True
		for task in self._task_id_to_task.values():
			if task["type"] == REDUCE_READ and task["status"] != COMPLETED:
				partition_to_reduce_reads_completed[task["partition"]] = False

		for task in self._task_id_to_task.values():
			if task["status"] != IDLE:
				continue
			if task["type"] == MAP and task["chunk"]["machine"] != machine:
				continue
			if task["type"] == REDUCE_GROUP and \
				(not partition_to_reduce_reads_completed[task["partition"]]):
				continue
			if task["type"] == REDUCE_GROUP and task["machine"] != machine:
				continue
			if task["type"] == REDUCE_READ and (not task["input_file"]):
				continue

			if task["type"] == REDUCE_READ and task["machine"] == -1:
				# Now that this reduce task is getting a machine,
				# we have to assign the same machine to
				# all the other reduce tasks in the partition.
				task["machine"] = machine
				for t in self._task_id_to_task.values():
					if t["id"] == task["id"]:
						continue
					if t["type"] in (REDUCE_READ, REDUCE_GROUP) and t["partition"] == task["partition"]:
						assert t["machine"] == -1
						t["machine"] = machine
			elif task["type"] == REDUCE_READ and task["machine"] != machine:
				continue

			task["status"] = IN_PROGRESS
			return task

		return {"type": SLEEP}

	def run(self):
		server = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), logRequests=False)
		server.register_function(self.heartbeat)
		while not self._completed:
			server.handle_request()

class Worker:

	def __init__(self, machine, mapper, reducer, combiner):
		self._machine = machine
		self._mapper = mapper
		self._reducer = reducer
		if combiner:
			self._combiner = combiner
		else:
			self._combiner = _identity_combiner

	def run(self):
		partition_to_key_to_values = {}
		completed_tasks = []
		while True:
			with xmlrpc.client.ServerProxy("http://localhost:8000") as proxy:
				task = proxy.heartbeat(self._machine, completed_tasks)
			completed_tasks = []
			print(task)
			if task["type"] == EXIT:
				break
			elif task["type"] == SLEEP:
				time.sleep(2)
			elif task["type"] == MAP:
				assert task["chunk"]["machine"] == self._machine

				key_to_values = collections.defaultdict(list)
				with open(task["chunk"]["path"], 'r') as fin:
					for line in fin:
						for key, value in self._mapper(task["chunk"]["path"], line):
							key_to_values[key].append(value)

				# Write out a file even if it's empty.
				partition_to_intermediate_kvs = {}
				for partition in range(task["num_reduce_partitions"]):
					partition_to_intermediate_kvs[partition] = []

				for key, values in key_to_values.items():
					for new_values in self._combiner(key, values):
						h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
						partition = h % task["num_reduce_partitions"]
						for new_value in new_values:
							partition_to_intermediate_kvs[partition].append(
								[key, new_value])

				for partition, intermediate_kvs in partition_to_intermediate_kvs.items():
					path = INTERMEDIATE_KV_TEMPLATE.format(
						task_id=task["id"], partition=partition)
					with jsonlines.open(path, 'w') as fout:
						for kv in intermediate_kvs:
							fout.write(kv)

				completed_tasks.append(task["id"])
			elif task["type"] == REDUCE_READ:
				if task["partition"] not in partition_to_key_to_values:
					partition_to_key_to_values[task["partition"]] = collections.defaultdict(list)
				# Simulate RPC.
				with jsonlines.open(task["input_file"], 'r') as fin:
					for key, value in fin:
						partition_to_key_to_values[task["partition"]][key].append(value)

				completed_tasks.append(task["id"])
			elif task["type"] == REDUCE_GROUP:
				path = OUTPUT_SPLIT_TEMPLATE.format(partition=task["partition"])
				with jsonlines.open(path, 'w') as fout:
					for key, values in partition_to_key_to_values[task["partition"]].items():
						for new_values in self._reducer(key, values):
							for new_value in new_values:
								fout.write([key, new_value])

				completed_tasks.append(task["id"])

def mapreduce(chunks, mapper, reducer, num_reduce_partitions, combiner=None):
	leader = Leader(chunks, num_reduce_partitions)
	leader_process = multiprocessing.Process(target=leader.run)
	leader_process.start()
	time.sleep(1)

	worker_machines = set([c["machine"] for c in chunks])
	worker_processes = []
	for machine in worker_machines:
		worker = Worker(machine, mapper, reducer, combiner)
		p = multiprocessing.Process(target=worker.run)
		p.start()
		worker_processes.append(p)

	for p in worker_processes:
		p.join()

	leader_process.join()

	output_kvs = []
	for partition in range(num_reduce_partitions):
		path = OUTPUT_SPLIT_TEMPLATE.format(partition=partition)
		with jsonlines.open(path, 'r') as fin:
			for line in fin:
				output_kvs.append(line)
	output_kvs.sort(key=lambda x: x[0])

	with jsonlines.open(OUTPUT_FILE, 'w') as fout:
		for kv in output_kvs:
			fout.write(kv)
