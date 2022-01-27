# PCA

PCA is a method for taking some data and compressing it, while preserving as much information as possible.

By "data", we mean a matrix $\textbf{X} \in \mathbb{R}^{n, p}$. By "compressing" it, we mean producing another matrix $\textbf{C} \in \mathbb{R}^{n,k}$ where $k < p$. In what sense do we try to preserve information in the original dataset? We can explain that first visually.

Take $p = 2$ and $k = 1$. A natural way to compress points in a plane is to project them onto a line. Which line? We take the line that minimizes the projection error, i.e., the sum of the distances bewteen each point and their projection. The plot below shows such a line and the projection of point $A$ onto the line.

![pca_projection](/img/pca_projection.png)

**Side note:** The line we get from minimizing the projection error is different from the line we get from least squares regression, because least squares regression tries to minimize the error in $y$, while the projection error cares about error in $x$ and $y$ equally.

In 2D, we project the data onto a line. In 3D, we project the data onto a plane ($k = 2$) or a line ($k = 1)$. In general, we project the data onto a "linear subspace". What this means is that we try to find a linear transformation $\textbf{A}$ such that $\textbf{A} \textbf{x} = \textbf{c}$ where $\textbf{x} \in \mathbb{R}^p$, $\textbf{A} \in \mathbb{R}^{k,p}$ and $\textbf{c} \in \mathbb{R}^k$ and where the projection error between $\textbf{x}$ and $\textbf{c}$ is minimized. Using $\textbf{A}$ in this way, we compress $\textbf{x}$ to $\textbf{c}$. We could imagine more complicated geometry to project data onto, but we make the assumption of linear subspaces to keep things simple.

## Sources

* Dimensionality Reduction, Machine Learning, 
* Goodfellow, Deep Learning, 2.12
* https://stats.stackexchange.com/questions/318625/why-do-the-leading-eigenvectors-of-a-maximize-texttrdtad
* https://stats.stackexchange.com/questions/32174/pca-objective-function-what-is-the-connection-between-maximizing-variance-and-m
* 3Brown1Blue, Dot products and duality