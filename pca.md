# PCA

Suppose we have $n$ points $\{\textbf{x}^{(1)}, \dots, \textbf{x}^{(n)}\}$. For each point $\textbf{x}^{(i)} \in \mathbb{R}^p$, we want to produce a compressed version $\textbf{c}^{(i)} \in \mathbb{R}^k$ where $k < p$. We produce a compressed point via an encoding function $f(\textbf{x}) = \textbf{c}$ and we recover the original point using a decoding function $g$, where $\textbf{x} \approx g(f(\textbf{x}))$. 

PCA assumes that:

1. $g(\textbf{c}) = \textbf{D} \textbf{c}$, where $\textbf{D} \in \mathbb{R}^{p \times k}$
2. $\textbf{D}^T \textbf{D} = \textbf{I}$, i.e., the columns of $\textbf{D}$ are orthogonal to each other and have unit norm.

Under those assumptions, setting $f(\textbf{x}) = \textbf{D}^T \textbf{x}$ minimizes the reconstruction error (I temporarily drop the bolding below for convenience):

$$
\begin{align}
\min_c \lVert x - Dc \rVert_2 &= \min_c [ (x - Dc)^T (x - Dc) ] \nonumber \\
&= \min_c [ (x - Dc)^T x - (x - Dc)^T Dc ] \nonumber \\
&= \min_c [ x^T (x - Dc) - (Dc)^T (x - Dc) ] \nonumber \\
&= \min_c [ x^T x - x^T Dc - (Dc)^T x + (Dc)^T (Dc) ] \nonumber \\
&= \min_c [ - 2 x^T Dc + c^T D^T Dc ] \nonumber \\
&= \min_c [ - 2 x^T Dc + c^T c ] \nonumber \\
\end{align}
$$

The gradient of the last line is:

$\nabla_{c} \left( - 2 x^T Dc + c^T c \right) = -2D^T x + 2c$

Setting it equal to 0 to find the minimum yields $c = D^T x$.

So now we have $f(\textbf{x}) = \textbf{D}^T \textbf{x}$ and $g(\textbf{c}) = \textbf{D} \textbf{c}$. How do we find $\textbf{D}$? We solve the following optimization problem:

$\textbf{D}^* = \textrm{argmin}_{\textbf{D}} \sqrt{\sum_{i,j} \left(x_j^{(i)} - g(f(\textbf{x}^{(i)}))_j \right)^2} \textrm{ subject to } \textbf{D}^T \textbf{D} = \textbf{I}_l$ 

## Example

Take $p = 2$ and $k = 1$. Then, $\textbf{D}$ is just the column vector $\textbf{d}$ in $\mathbb{R}^2$. It corresponds to a direction in the plane (imagine a vector centered at the origin with its head on the point ($d_0$, $d_1$)). Then, $f(\textbf{x}) = \textbf{d}^T \textbf{x}^{(i)}$ is just the dot product of $\textbf{d}$ and $\textbf{x}^{(i)}$, which is the projection of $\textbf{x}^{(i)}$ onto $\textbf{d}$. The plot below shows a point in the plane projected onto the axis defined by $\textbf{d}$ that minimizes the reconstruction error:

![pca_projection](/img/pca_projection.png)

**Side note:** The line we get from minimizing the projection error is different from the line we get from least squares regression, because least squares regression tries to minimize the error in $y$, while the projection error cares about error in $x$ and $y$ equally.

## Sources

* Goodfellow, Deep Learning, Chapter 2.12
* Dimensionality Reduction, Machine Learning, Andrew Ng
* https://stats.stackexchange.com/questions/318625/why-do-the-leading-eigenvectors-of-a-maximize-texttrdtad
* https://stats.stackexchange.com/questions/32174/pca-objective-function-what-is-the-connection-between-maximizing-variance-and-m
* 3Brown1Blue, Dot products and duality