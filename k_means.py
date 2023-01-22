"""K-means clustering."""
import numpy as np


def k_means_clustering(X, k, rng, max_iter):
	n, p = X.shape
	sample_indices = rng.choice(n, k, replace=False)
	centroids = X[sample_indices, :]
	prev_cluster_indices = np.zeros(n)
	for _ in range(max_iter):
		cluster_indices = np.zeros(n)
		for i in range(n):
			min_dist = float('inf')
			for j in range(k):
				dist = sum((X[i,:] - centroids[j,:])**2)
				if dist < min_dist:
					min_dist = dist
					cluster_indices[i] = j

		if (prev_cluster_indices == cluster_indices).all():
			break

		for j in range(k):
			centroids[j, : ] = np.mean(X[cluster_indices == j, :])

		prev_cluster_indices = cluster_indices
	return cluster_indices


if __name__ == "__main__":
	rng = np.random.default_rng(seed=0)
	n = 1000
	p = 10
	X = rng.normal(size=(n, p))
	k = 3
	cluster_indices = k_means_clustering(X, k, rng, max_iter=100)
