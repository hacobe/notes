"""Word count in memory.

# Problem

Given a text file, write out a jsonl file with a line
for each unique word in the text file and where the line
has the form [word, count]. Sort the lines by word.

Assume that the input file does not fit into memory, but
the output file does.

# Notes

* We stream the input file in line-by-line and accumulate
  the counts with an in-memory dictionary.
* We treat each punctuation character has its own token.\

# Usage

```bash
> wget https://www.gutenberg.org/files/84/84-0.txt
> python word_count_in_memory.py 84-0.txt out.jsonl
```
"""
import collections
import jsonlines
import re
import sys

def _tokenize(text):
	return re.findall(r"(\w+|[^\s\w])", text)

def word_count(input_file, output_file):
	word_to_count = collections.defaultdict(int)
	with open(input_file, 'r') as fin:
		for line in fin:
			for word in _tokenize(line):
				word_to_count[word] += 1

	word_and_counts = list(word_to_count.items())
	word_and_counts.sort()

	with jsonlines.open(output_file, 'w') as fout:
		for word, count in word_and_counts:
			fout.write([word, count])

if __name__ == "__main__":
	assert len(sys.argv) == 3
	input_file = sys.argv[1]
	output_file = sys.argv[2]
	word_count(input_file, output_file)