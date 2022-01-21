# Kernel trick

Suppose we observe a training dataset $\{(\textbf{x}^{(i)}, y^{(i)})\}_{i=1}^n$ where each feature vector $\textbf{x}^{(i)} \in \mathbb{R}^p$ and each target $y^{(i)} \in \mathbb{R}$. We want to estimate a function $h(\textbf{x})$ that enables us to predict $y$ from $\textbf{x}$.

Organize the training dataset into the design matrix $\textbf{X} \in \mathbb{R}^{n \times p}$ and the target vector $\textbf{y} \in \mathbb{R}^n$. Ridge regression finds the coefficients $\textbf{w}$ that minimize $\lVert \textbf{y} - \textbf{X}w \rVert_2^2 + \lambda \lVert \textbf{w} \rVert_2^2$ where $\lambda$ controls the trade-off between the fit to the training dataset and the complexity of the model (as measured by the magnitude of its coefficients).

We solve for $\textbf{w}$ using the regularized normal equation: $\textbf{w} = (\textbf{X}^T \textbf{X} + \lambda I_p)^{-1} \textbf{X}^T y$ (supposing we fit a model without an intercept, which we can always do by mean centering each $y^{(i)}$ and $\textbf{x}^{(i)}$). Solving this $p \times p$ system of linear equations takes $O(p^3)$ time.

Suppose we want to increase the capacity of the model by adding interactions between features, e.g., we could define a new feature vector $\phi(x) = (x, x \cdot x_1, x \cdot x_2, \cdots, x \cdot x_p)^T$. The dimensionality of $\phi(\textbf{x})$ is $O(p^2)$ making solving for $\textbf{w}_{\phi}$ take at least $O(p^6)$ time. 

That's slow, but let's make it even worse. Re-define $\phi(\textbf{x}) = \exp \left(- \frac{x^2}{\sigma^2}\right) \left(1, \frac{x}{\sigma \sqrt{1!}}, \frac{x^2}{\sigma^2 \sqrt{2!}}, \frac{x^3}{\sigma^3 \sqrt{3!}}, \cdots \right)^T$. The virtue of this new representation of features is that the dot product of (think similarity between) $\textbf{x}^{(i)}$ and $\textbf{x}^{(j)}$ is given by the Gaussian function: $k(\textbf{x}^{(i)}, \textbf{x}^{(j)}) = \exp\left(-\frac{\lVert \textbf{x}^{(i)} - \textbf{x}^{(j)} \rVert_2^2}{2 \sigma^2}\right)$. It's a nice way to encode smoothness in the feature space (and we can control the amount of smoothness by varying $\sigma$). The downside is that this is an infinite dimensional feature space, which seems intractable.

Go back to the original feature representation for a moment. Define the "kernel" matrix $\textbf{K}$ to contain the dot product between each pair of training examples, i.e., $K_{i,j} = (\textbf{x}^{(i)})^T \textbf{x}^{(j)}$ or in matrix form: $\textbf{K} = \textbf{X} \textbf{X}^T \in \mathbb{R}^{n \times n}$ (notice that this is different from the covariance matrix $\textbf{X}^T \textbf{X} \in \mathbb{R}^{p \times p}$). Let $\alpha = (\textbf{K} + \lambda I_n) \textbf{y}$. With some algebra, we can show that $\textbf{w}^T \textbf{x} = \sum_{i=1}^n \alpha_i (\textbf{x}^T \textbf{x}^{(i)})$, so $\alpha$ gives the solution to the ridge regression problem, but where the features only show up in the equations for training and prediction as dot products.

We can run through the same steps for $\phi(\textbf{x})$. Even though $\phi(\textbf{x})$ is infinite dimensional, we only ever have to compute dot products and the dot product $\phi(\textbf{x}^{(i)})$ and $\phi(\textbf{x}^{(j)})$ is given by the Gaussian function. It takes $O(p)$ time to evaluate the Gaussian function. We have to compute it for every pair of points giving $O(n^2 p)$ time to construct $\textbf{K}_{\phi}$. Then it takes $O(n^3)$ time to solve the $n \times n$ system of linear equations. So we can regress $y$ on an infinite number of features.

In general, avoiding the explicit computation of $\phi(\textbf{x})$ for some feature map $\phi$ by computing dot products in that feature space is called the "kernel trick".

## Sources

* https://people.eecs.berkeley.edu/~jrs/189s19/lec/14.pdf