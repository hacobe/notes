import collections

def bfs(start, graph):
	queue = collections.deque([start])
	visited = set([start])
	while queue:
		node = queue.popleft()
		for nbr in graph.get(node, []):
			if nbr not in visited:
				visited.add(nbr)
				queue.append(nbr)