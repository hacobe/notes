"""External merge sort.

The implementation below is based on:
http://web.archive.org/web/20230202171450/https://www.geeksforgeeks.org/external-sorting/

```bash
python external_merge_sort.py
sort input.txt > expected.txt
cmp expected.txt output.txt
```

Sources:
* http://web.archive.org/web/20230202171450/https://www.geeksforgeeks.org/external-sorting/
* http://web.archive.org/web/20230202171737/https://www.geeksforgeeks.org/internal-implementation-of-linux-sort-command/
* https://github.com/coreutils/coreutils/blob/master/src/sort.c
* https://en.wikipedia.org/wiki/External_sorting#External_merge_sort
* http://web.archive.org/web/20230202171847/http://vkundeti.blogspot.com/2008/03/tech-algorithmic-details-of-unix-sort.html
* http://web.archive.org/web/20230202172221/https://www.geeksforgeeks.org/merge-sort-using-multi-threading/
"""
import heapq
import psutil
import string
import numpy as np


def _get_partition_file(idx):
	return "partition{idx}.txt".format(idx=idx)


def partition_and_sort(input_file, partition_size, num_partitions):
	fin = open(input_file, "r")

	fout = []
	for i in range(num_partitions):
		partition_file = _get_partition_file(i)
		fout.append(open(partition_file, "w"))

	fidx = 0
	lines = []
	for line in fin:
		lines.append(line.strip() + "\n")
		if len(lines) == partition_size:
			lines.sort()
			for line in lines:
				fout[fidx].write(line)
			fidx += 1
			lines = []
	if len(lines) > 0:
		lines.sort()
		for line in lines:
			fout[fidx].write(line)

	for i in range(len(fout)):
		fout[i].close()

	fin.close()


def merge(output_file, num_partitions):
	fin = []
	for i in range(num_partitions):
		partition_file = _get_partition_file(i)
		fin.append(open(partition_file, "r"))

	fout = open(output_file, "w")
	
	heap = []
	for i in range(len(fin)):
		line = fin[i].readline()
		if not line:
			break
		heapq.heappush(heap, (line, i))

	count = 0
	while count <= i:
		root = heapq.heappop(heap)
		fout.write(root[0])
		line = fin[root[1]].readline()
		if line:
			heapq.heappush(heap, (line, root[1]))
		else:
			count += 1

	for i in range(len(fin)):
		fin[i].close()

	fout.close()


def external_sort(input_file, output_file, partition_size, num_partitions):
	partition_and_sort(input_file, partition_size, num_partitions)
	merge(output_file, num_partitions)


if __name__ == "__main__":
	num_partitions = 10
	partition_size = 1000
	input_file = "input.txt"
	output_file = "output.txt"

	rng = np.random.default_rng(seed=0)
	words = []
	alphabet = [s for s in string.ascii_lowercase]
	for _ in range(num_partitions * partition_size):
		words.append("".join(rng.choice(alphabet, size=10)))

	with open(input_file, "w") as fin:
		fin.write("\n".join(words))

	external_sort(input_file, output_file, partition_size, num_partitions)
