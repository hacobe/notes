# Overflow and Underflow

A fundamental difficulty is the **rounding error** introduced when we store real numbers on a computer with a finite number of bits. The rounding error is especially problematic when it compounds across many operations.

There are 2 types of rounding error:
1. **Overflow**: A number with large magnitude is approximated as negative or positive infinity.
2. **Underflow**: A number near 0 is rounded down to 0.

Overflow is a problem, because it can result in **not-a-number**  (NaN) values. What happens is that numbers overflow, get approximated as negative or positive **infinity** and then get used in arithmetic operations that result in NaNs. In Python, arithmetic operations that result in NaNs include but are not limited to inf/inf, inf - inf, 0 * inf.[^1]

Underflow is a problem, because:
* It can result in a **divide by 0** exception being thrown (In Python, 1/0 results in a ZeroDivisionError)
* It gets used in an operation that result in negative or positive infinity (e.g., log(0) or np.array([1.]) / np.array([0.])), which then runs into the same problems we saw with overflow.

As an example, consider the **softmax function**:

$\textrm{softmax}(\textbf{x})\_i = \frac{\textrm{exp}(x\_i)}{\sum\limits\_{j=1}^n \textrm{exp}(x\_j)}$

Suppose we set all $x_i$ to some constant $c$. The expression should evaluate to $\frac{1}{n}$. However, if $c$ is very negative, then $\textrm{exp}(c)$ will underflow, which makes both the numerator and the denominator 0 and results in all NaNs. If $c$ is very positive then $\textrm{exp}(c)$ will overflow, which makes both the numerator and the denominator infinity and results in all NaNs

```python
import numpy as np

def softmax(x):
	return np.exp(x) / np.sum(np.exp(x))

assert np.isnan(softmax(np.array([-1e3, -1e3]))).all()
assert np.isnan(softmax(np.array([1e3, 1e3]))).all()
```

We can avoid overflow in the numerator and division by 0 if we subtract out from each $x_i$ the max $m$ over all $x_i$ before exponentiation. This does not change the analytical solution to the softmax, because it amounts to multiplying the numerator and the denominator by $\textrm{exp}(-m)$. Call the transformed inputs $z_i$. We avoid overflow in the numerator, because the maximum $z_i$ is 0. And we avoid division by 0, because there is always one term in the denominator equal to 1.

```python
def stable_softmax(x):
	z = x - max(x)
	return np.exp(z) / np.sum(np.exp(z))

assert (stable_softmax(np.array([-1e3, -1e3])) == np.array([0.5, 0.5])).all()
assert (stable_softmax(np.array([1e3, 1e3])) == np.array([0.5, 0.5])).all()
```

This is basically the implementation of softmax in JAX [^2].

If we use the softmax as an output layer and we're minimizing the negative log likelihood, then we need to compute the log of the softmax outputs, i.e., the log of our predicted probabilities. Unfortunately, the numerator of even the stable softmax can still underflow:

```python
assert (stable_softmax(np.array([1, 1e3])) == np.array([0., 1.])).all()
```

The solution is to implement a numerically stable function that calculates the log softmax using the same trick.

```python
def stable_log_softmax(x):
	z = x - max(x)
	logsumexp = np.log(np.sum(np.exp(z)))
	return z - logsumexp

assert (np.log(stable_softmax(np.array([1, 1e3]))) == np.array([-np.inf, 0.])).all()
assert (stable_log_softmax(np.array([1, 1e3])) == np.array([-999., 0])).all()
```

This is basically the implementation of log_softmax in JAX.[^3]

## Sources

* Goodfellow, Deep learning, Section 4.1

[^1]: https://stackoverflow.com/questions/25506281/what-are-some-possible-calculations-with-numpy-or-scipy-that-can-return-a-nan
[^2]: https://jax.readthedocs.io/en/latest/_modules/jax/_src/nn/functions.html#softmax
[^3]: https://jax.readthedocs.io/en/latest/_modules/jax/_src/nn/functions.html#log_softmax