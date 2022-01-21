# James-Stein estimation

## What is James-Stein estimation?

Suppose we observe $\textbf{x} \in \mathbb{R}^p$, where $x_i = \theta_i + \epsilon_i$ for some unobserved $\theta \in \mathbb{R}^p$ and $\epsilon_i \sim N(0, 1)$, and our goal is to find a function $f(\textbf{x}) = \hat \theta$ that minimizes $E\left[\lVert \theta - \hat \theta \rVert^2\right]$.

Because the distributions that generate each $x_i$ are independent, it seems like all we can do is use each $x_i$ as our estimate of $\theta_i$ by choosing $f(\textbf{x}) = \textbf{x}$. Also, $\textbf{x}$ is the Maximum Likelihood estimate of $\theta$.

The James-Stein estimate instead chooses $f(\textbf{x}) = (1 - \frac{p - 2}{\rVert \textbf{x} \lVert^2}) \textbf{x}$.[^1] The surprising result is that this estimate does better (according to our evaluation criteria) than the Maximum Likelihood estimate for any $\theta$ when $p \ge 2$.

## Why is it so surprising?

The James-Stein estimate uses all the samples to make a guess for each mean even though the distributions the samples come from are independent. It seems to suggest that we are improving our guess for a particular mean by using information from completely unrelated distributions. As described on the Wikipedia page for [Stein's example](https://web.archive.org/web/20200601224707/https://en.wikipedia.org/wiki/Stein%27s_example): "To demonstrate the unintuitive nature of Stein's example, consider the following real-world example. Suppose we are to estimate three unrelated parameters, such as the US wheat yield for 1993, the number of spectators at the Wimbledon tennis tournament in 2001, and the weight of a randomly chosen candy bar from the supermarket...At first sight it appears that somehow we get a better estimator for US wheat yield by measuring some other unrelated statistics such as the number of spectators at Wimbledon and the weight of a candy bar."

## What's the trick?

At a high level, the Wikipedia page explains that "This is of course absurd; we have not obtained a better estimator for US wheat yield by itself, but we have produced an estimator for the vector of the means of all three random variables, which has a reduced total risk. This occurs because the cost of a bad estimate in one component of the vector is compensated by a better estimate in another component. Also, a specific set of the three estimated mean values obtained with the new estimator will not necessarily be better than the ordinary set (the measured values). It is only on average that the new estimator is better."

## How does it work?

Each $x_i$ has some probability of being an outlier and misleading us about the value of $\theta_i$. But it's much less likely for all the $x_i$ to be outliers, because the distributions are independent. Similarly, a fair coin has a 50% chance of landing on heads, but the chance of 10 coins all landing on heads is 1 in 1024. Relatedly, estimating a metric that summarizes $\theta$ (like its mean $\bar{\theta}$) is an easier task than estimating each component of $\theta$. If $\theta_1, \dots, \theta_p$ are similar enough, then $\bar{\textbf{x}}$ will give a better estimate of $\theta$ than $\textbf{x}$ (we see this clearly in the extreme case of $\theta_1 = \dots = \theta_p$, where the mean just uses more data to estimate the same quantity).

On the other hand, if the variance of $\theta$ is large, i.e., $\theta_1, \dots, \theta_p$ are very different from each other, then $\bar{\textbf{x}}$ will be a very poor estimate of $\theta$. In this case, getting a good estimate of $\bar{\theta}$ doesn't help us.

There is a trade-off between estimating $\theta$ based on a more reliable, but less relevant estimate of the global behavior and estimating it based on a less reliable, but more relevant estimate of its local behavior. This trade-off depends on the variance of $\theta$, i.e., the consistency of its local behavior. We don't know the variance of $\theta$, but we can estimate it based on the variance of $\textbf{x}$. We can then construct an estimator for $\theta_i$ that is an average between $x_i$ and $\bar{\textbf{x}}$ weighted by the inverse variance of $\textbf{x}$. The greater the variance, the more weight we put on $x_i$ for our estimate of $\theta_i$. The smaller the variance, the more weight we put on $\bar{\textbf{x}}$.

This is an instance of a Bias-Variance trade-off. A special feature of the mean squared error is that we can think of it as the sum of the squared bias of the estimator (how close is $\theta$ to $E[\hat \theta]$?) and the variance of the estimator (how close is $E[\hat \theta]$ to $\hat \theta$ on average?). In this context, we're weighing the increased bias of using information from other distributions with the decreased variance from using more data.

To connect this back to the James-Stein estimate, consider $\lVert \theta \rVert$, i.e. the distance of $\theta$ from the origin, as our summary metric of $\theta$ instead of $\bar{\theta}$. We can get a reliable estimate of $\lVert \theta \rVert$ based on all of the data we observe. If $\lVert \theta \rVert$ is small, then a reasonable guess of $\theta$ is 0 and the increase in bias is worth the decrease in variance from this "smoothed" guess. Otherwise, $\textbf{x}$ is better: the increase in variance is offset by the decrease in bias from not guessing 0 for a vector with large magnitude.

We can construct an estimator for $\theta_i$ that is an average between $x_i$ and 0 weighted by the inverse of our estimate of $\lVert \theta \rVert$. The greater the magnitude, the more weight we put on $x_i$. The smaller the magnitude, the more weight we put on 0. The James-Stein estimate is this weighted average when the weight we put on $x_i$ is $1 - \frac{p - 2}{\lVert x \rVert^2}$.

Why this particular function of the inverse magnitude for the weight? For one, $E[\lVert (1 - \frac{p - 2}{\lVert x \rVert^2}) \textbf{x} \rVert^2] \approx E[\lVert \theta \rVert^2]$ when $p$ is large.[^2]. In another surprising twist, it's also an estimate of the slope of the line through the origin that we get from regressing $\theta$ on $\textbf{x}$.[^3] We can't run this regression, because we don't observe $\theta$, but we can still construct an estimate of the slope using $\textbf{x}$ alone. Under this interpretation, we use all the data to characterize a global relationship between $\theta$ and $\textbf{x}$ and then exploit that to make a local prediction for each $\theta_i$. If we don't require the line to go through the origin, then our estimate for the equation of the line becomes: $\frac{1}{\hat{\mathrm{Var}[\theta]}} \bar{\textbf{x}} + (1 - \frac{1}{\hat{\mathrm{Var}[\theta]}}) x_i$ or an average of $\bar{\textbf{x}}$ and $x_i$ weighted by our estimate of the inverse variance of $\theta$.[^4]

[^1]: We can also replace $p - 2$ with any $c \in (0, 2p - 4)$ and the result still holds ([Stigler 1990](https://projecteuclid.org/download/pdf_1/euclid.ss/1177012274), Pg. 1)

[^2]: [Hoff 2013](https://www.stat.washington.edu/~pdhoff/courses/581/LectureNotes/Static/shrinkage.pdf), Pg. 12

[^3]: [Stigler 1990](https://projecteuclid.org/download/pdf_1/euclid.ss/1177012274)

[^4]: [Jordan 2014](https://piazza.com/class_profile/get_resource/hzdbtb6jdr56q1/i2kz4qj4x102b1), Pg. 7