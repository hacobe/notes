"""Top K words using MapReduce.

# Problem

Use `mapreduce.py` to write out a jsonl file with a line for each
of the top K most frequently occurring words in all the text files.

# Usage

```bash
> wget https://www.gutenberg.org/files/84/84-0.txt
> mkdir tmp
> split -l 409 84-0.txt tmp/split_
> python word_count_mapreduce.py
> rm tmp/*-*.jsonl tmp/split_* tmp/out.jsonl
> python top_k_words_mapreduce.py
"""
import heapq
import jsonlines
import os

import mapreduce

def mapper(key, value):
	# group all by the same key
	kv = jsonlines.Reader([value]).read()
	yield "ONE_KEY", kv

def reducer(key, values):
	del key
	top_k = 5
	min_heap = []
	for word, count in values:
		heapq.heappush(min_heap, (count, word))
		if len(min_heap) > top_k:
			heapq.heappop(min_heap)	

	while min_heap:
		count, word = heapq.heappop(min_heap)
		yield [(word, count)]

if __name__ == "__main__":
	chunks = []
	for i, f in enumerate(os.listdir(mapreduce.BASE_DIR)):
		chunks.append(
			{"path": os.path.join(mapreduce.BASE_DIR, f), "machine": i % 2})

	num_reduce_partitions = 1

	mapreduce.mapreduce(
		chunks,
		mapper,
		reducer,
		num_reduce_partitions,
		combiner=None
	)