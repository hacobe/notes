# Bias-Variance trade-off

The bias-variance trade-off is the trade-off between overfitting and underfitting.

If we have high bias and low variance, then the model is very simple and the model's prediction does not change much across samples of the training dataset. The model's prediction is either much larger or much lower than the truth (high bias), but it makes that prediction consistently (low variance).

If we have low bias and high variance, then the model is very complex and the model's prediction changes a lot across samples of the training dataset, because it has the capacity to fit the training dataset to a high resolution. The model's prediction is close to each sample of the training dataset (low bias), but it varies wildly between samples of the training dataset (high variance).

## Example

Decomposing the expected square error loss gives us one example of a bias-variance trade-off.

Suppose the truth is given by $f(x)$ and we sample $y = f(x) + \epsilon$ where $\mathbb{E}[\epsilon] = 0$ and it has fixed, independent variance $\mathrm{Var}[\epsilon] = \sigma^2$.

We then sample a training data and fit a model $\hat f (x)$.

$\mathbb{E}\left[\left(y - \hat f(x)\right)^2\right] = \left(f(x) - \mathbb{E}[\hat f(x)]\right)^2 + \mathrm{Var}\left[\hat f(x)\right] + \sigma^2$

The first term is the bias of $\hat f(x)$ squared, the second term is the variance of $\hat f(x)$ and the last term is the irreducible error.

## Sources

* https://en.wikipedia.org/wiki/Bias%E2%80%93variance_tradeoff
