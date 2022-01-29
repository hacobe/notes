# Critical points

Suppose we have a function $y = f(x)$ with $x, y \in \mathbb{R}$.

A point $x$ where the derivative $f'(x) = 0$ is called a **critical point**. A critical point may be a **maximum**, a **minimum** or a **saddle point**. See Figure 4.2 from Goodfellow:

![goodfellow_figure4.2](img/goodfellow_figure4.2.png)

The second derivative $f''(x)$ measures **curvature**.

If the second derivative at the point $f''(x) \gt 0$, then the point is a minimum. If $f''(x) \lt 0$, then point is a maximum. If $f''(x) = 0$, then the **second derivative test** is inconclusive.

For a function $f(\textbf{x})$ that takes a vector $\textbf{x}$ as an input, we can compute the gradient $\nabla f(\textbf{x})$ with respect to $\textbf{x}$. Then, $\textbf{x}$ is a critical point if $\nabla f(\textbf{x}) = 0$.

## Sources

* * Goodfellow, Deep learning, Section 4.3