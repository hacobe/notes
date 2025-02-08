"""Word count using MapReduce.

# Problem

Use `mapreduce.py` to write out a jsonl file with a line for each
unique word in all the text files and where the line has the
form [word, count]. Sort the lines by word.

# Usage

```bash
> wget https://www.gutenberg.org/files/84/84-0.txt
> mkdir tmp
> split -l 409 84-0.txt tmp/split_
> python word_count_mapreduce.py
"""
import os
import re

import mapreduce

def _tokenize(text):
	return re.findall(r"(\w+|[^\w\s])", text)

def mapper(key, value):
	for word in _tokenize(value):
		yield word, 1

def combiner(key, values):
	yield [len(values)]

def reducer(key, values):
	s = 0
	for value in values:
		s += value
	yield [s]

if __name__ == "__main__":
	chunks = []
	for i, f in enumerate(os.listdir(mapreduce.BASE_DIR)):
		chunks.append(
			{"path": os.path.join(mapreduce.BASE_DIR, f), "machine": i % 2})

	num_reduce_partitions = 4

	mapreduce.mapreduce(
		chunks,
		mapper,
		reducer,
		num_reduce_partitions,
		combiner=combiner
	)