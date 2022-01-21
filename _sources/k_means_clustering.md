# K-means clustering

K-means is an unsupervised clustering algorithm.

It takes as input a number of clusters $k$ and a design matrix $\textbf{X} \in \mathbb{R}^{n, p}$ and returns a vector $\textbf{c} \in \{1, 2, \dots, k\}^n$ where $\textbf{c}^{(i)} \in \{1, 2, \dots, k\}$ gives the cluster assignment for each $\textbf{x}^{(i)} \in \mathbb{R}^p$ in the input.

It does this by finding $k$ means (hence the name) that minimize the sum of the squared distances between each data point and the mean closest to it. In particular, it has this optimization objective:

$\min_{\mu_1, \dots, \mu_k, \textbf{c}^{(1)}, \dots, \textbf{c}^{(n)}} \frac{1}{n} \sum_{i=1}^n \lVert \textbf{x}^{(i)} - \mu_{\textbf{c}^{(i)}} \rVert^2$

## Implementation

Lloyd's algorithm for k-means clustering proceeds as follows:

1. Init to k random points
2. Cluster assignment based on closest means
3. Estimate mean based on new clusters
4. Break when means don't change or go back to 2

We often want to run it 100s of times with different initializations. The running time for one initialization is $O(n k p t)$ where $n$, $k$, and $p$ are defined above and $t$ is the number of iterations needed for converence.

## Questions

* **How do you pick the number of clusters?** 
	* Visualize the data and pick it manually
	* Use domain knowledge
	* Try several different clusters and evaluate the performance against a downstream metric
	* Try several different clusters and evaluate the cost (though often ambiguous)
* **When does K-means work well and not so well?** "A key limitation of k-means is its cluster model. The concept is based on spherical clusters that are separable so that the mean converges towards the cluster center. The clusters are expected to be of similar size, so that the assignment to the nearest cluster center is the correct assignment."
* **Hows does K-means relate to EM?** Assigning the data points to clusters can be thought of as the E step and computing the centroids that minimize the squared distances can be thought of the M step, but the clusters are hard assignments (no probabilities).
* **How does K-means relate to GMMs?** It's a special case of Gaussian mixture models taking all covariances as diagonal, equal and small.

## Sources

* Unsupervised Learning, Machine Learning, Andrew Ng
* https://en.wikipedia.org/wiki/K-means_clustering
* https://stackoverflow.com/questions/18634149/what-is-the-time-complexity-of-k-means
* https://en.wikipedia.org/wiki/Lloyd%27s_algorithm

