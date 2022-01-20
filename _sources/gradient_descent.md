# Gradient desecent

**Gradient descent** is an algorithm for finding a minimum of a function.

It works as follows. Given a function $f: \mathbb{R}^p \mapsto \mathbb{R}$ and a **learning rate** $\lambda \in \mathbb{R}^{+}$, choose a random starting point $\textbf{w}^{(0)} \in \mathbb{R}^p$ and apply the following update iteratively: $\textbf{w}^{(t)} = \textbf{w}^{(t-1)} - \lambda \nabla f(\textbf{w}^{(t-1)})$ for $t = 1, 2, 3, \dots$ Stop when $\textbf{w}^{(t)} \approx \textbf{w}^{(t-1)}$ or when $f(\textbf{w}^{(t)})$ is less than some threshold or using some other heuristic. Take the last $\textbf{w}^{(t)}$ as a minimizer of the function.

$\nabla f(\textbf{w}^{(t-1)})$ is the **gradient** of $f$ evaluated at $\textbf{w}^{(t-1)}$. In general, $\nabla f(\textbf{w}) = \begin{bmatrix} \frac{\partial f}{w\_1} (\textbf{w}) \\ \cdots \\ \frac{\partial f}{\partial w_p}(\textbf{w}) \end{bmatrix}^T$. The $i$-th component tells us how much the function changes when we move $w_i$ a little bit while keeping the other components fixed. Computing $\nabla f(\textbf{w}) \cdot \textbf{u}$ tells us how much the function changes when we move $\textbf{w}$ a little bit in the direction of some vector $\textbf{u}$. Which direction will most decrease the function? The dot product is minimized when the two vectors point in the opposite directions, i.e., when $\textbf{u} = - \nabla f(\textbf{w})$. Therefore, gradient descent is a greedy algorithm that at each point takes a step in the direction (the negative of the gradient) that most decreases the function near the point.

**Example:** Let $f: \mathbb{R} \mapsto \mathbb{R}$. In particular, let $f(w) = w^2$, then $\nabla f(w) = 2w$. The update rule is then $w^{(t)} = w^{(t-1)} - 2 \lambda w^{(t-1)} = (1 - 2 \lambda) w^{(t-1)}$. In this unusual case, we can write down a closed form solution: $w^{(t)} = (1 - 2 \lambda)^{-t} w^{(0)}$. If $\lambda \in (0, \frac{1}{2})$, then as $t$ gets larger, $w^{(t)}$ approaches 0, which is the minimum of the function. What happens if we choose $\lambda > \frac{1}{2}$? Then $w^{(t)}$ will be positive for even $t$ and negative for odd $t$ never approaching the minimum. If we make $\lambda$ very small, then it will get closer and closer to 0, but it might take a while before our stopping criterion kicks in. In practice, we try several different values of $\lambda$ and pick one based on plots of $f(w^{(t)})$ against $t$.

## Sources

* http://web.archive.org/save/https://www.khanacademy.org/math/multivariable-calculus/multivariable-derivatives/partial-derivative-and-gradient-articles/a/directional-derivatives-going-deeper
* https://math.stackexchange.com/questions/223252/why-is-gradient-the-direction-of-steepest-ascent
* Gradient descent, how neural networks learn, 3Blue1Brown (https://www.youtube.com/watch?v=IHZwWFHWa-w)
* https://www.stat.cmu.edu/~ryantibs/convexopt-F15/lectures/05-grad-descent.pdf