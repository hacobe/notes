def _dfs(node, graph, visited):
	if node in visited:
		return
	visited.add(node)
	for nbr in graph.get(node, []):
		_dfs(nbr, graph, visited)

def dfs(start, graph):
	visited = set()
	return _dfs(start, graph, visited)
