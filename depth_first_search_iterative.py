def dfs(start, graph):
	stack = [start]
	visited = set()
	while stack:
		node = stack.pop()
		if node in visited:
			continue
		print(node)
		visited.add(node)
		for nbr in graph.get(node, []):
			stack.append(nbr)

