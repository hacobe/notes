"""Word count on disk.

# Problem

Given a text file, write out a jsonl file with a line
for each unique word in the text file and where the line
has the form [word, count]. Sort the lines by word.

Assume that neither the input file nor the output file
fit into memory.

# Notes

* Don't forget about the last split
* Don't write the last word twice if the last word happens to be different than
  penultimate word
* Sorting the lines by count requires 2 external sorts in total
* Write the prev_word, not word

# Usage

```bash
> wget https://www.gutenberg.org/files/84/84-0.txt
> mkdir tmp
> python word_count_on_disk.py 84-0.txt tmp/split_ 50000 out.jsonl
```
"""
import collections
import heapq
import jsonlines
import re
import sys

def _tokenize(text):
	return re.findall(r"(\w+|[^\w\s])", text)

def _write_split(items, split_files):
	items.sort()
	split_file = f"{split_prefix}{len(split_files)}.txt"
	with open(split_file, 'w') as fout:
		for item in items:
			fout.write(item + "\n")
	split_files.append(split_file)

def _external_sort(input_files, output_file):
	fins = [open(input_file, 'r') for input_file in input_files]

	heap = []
	for i, fin in enumerate(fins):
		heapq.heappush(heap, (fin.readline(), i))

	fout = open(output_file, 'w')
	fout.close()
	fout = open(output_file, 'a')
	while heap:
		line, i = heapq.heappop(heap)

		if not line:
			fins[i].close()
			continue

		fout.write(line)
		heapq.heappush(heap, (fins[i].readline(), i))
	fout.close()

def word_count(input_file, split_prefix, split_size, output_file):
	assert split_size >= 1

	split_files = []
	words = []
	with open(input_file, 'r') as fin:
		for line in fin:
			for word in _tokenize(line):
				words.append(word)
				if len(words) == split_size:
					_write_split(words, split_files)
					words.clear()
	if words:
		_write_split(words, split_files)

	combined_split_file = f"{split_prefix}combined.txt"
	_external_sort(split_files, combined_split_file)

	fout = jsonlines.open(output_file, 'w')
	fout.close()
	fout = jsonlines.open(output_file, 'a')
	with open(combined_split_file, 'r') as fin:
		count = 0
		prev_word = None
		prev_word_written = None
		for line in fin:
			word = line.strip()
			if prev_word is None or word == prev_word:
				count += 1
			else:
				fout.write([prev_word, count])
				prev_word_written = prev_word
				count = 1
			prev_word = word
		if word != prev_word_written:
			fout.write([word, count])
	fout.close()

if __name__ == "__main__":
	assert len(sys.argv) == 5
	input_file = sys.argv[1]
	split_prefix = sys.argv[2]
	split_size = int(sys.argv[3])
	output_file = sys.argv[4]
	word_count(input_file, split_prefix, split_size, output_file)