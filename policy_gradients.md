# Policy gradients

Recall that we're trying to maximize the following expectation in reinforcement learning:

$\mathbb{E}_{\left( s_1, a_1, \dots, s_T, a_T \right) \sim p_{\theta} (s_1, a_1, \dots, s_T, a_T)} \left[ \sum_{t=1}^T R \left[s_t, a_t \right]  \right]$

A natural thing to do is gradient ascent on this objective. This is the REINFORCE algorithm. In particular, we follow these steps:

1. Sample a trajectory
2. Calculate the gradient for that trajectory
3. Update by adding the product of the gradient and the learning rate to $\theta$
4. Repeat

How do we calculate the gradient?

By the definition of expectation, we can write the expectation above as:

$\int p_{\theta} (\tau) R \left[\tau \right] d \tau$

where we define $R \left[\tau \right]  = \sum_{t=1}^T R \left[s_t, a_t \right]$ and $\tau = \left( s_1, a_1, \dots, s_T, a_T \right)$. This is the summation of total trajectory rewards weighted by the probability of that trajectory over the space of trajectories.

Because the derivative of $\log g(x) = \frac{g'(x)}{g(x)}$ by the chain rule, the gradient of this integral is equal to:

$\int \nabla_{\theta} \left[ p_{\theta} (\tau) \right] R \left[\tau \right] d \tau = \int  p_{\theta} (\tau) \nabla_{\theta} \left[ \log p_{\theta} (\tau) \right] R \left[\tau \right] d \tau$

We stick the log in there so we get a sum of terms in our factorization of $p_{\theta}$, some of which we can cancel out because they don't depend on $\theta$, leaving us with:

$\int  p_{\theta} (\tau) \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] R \left[\tau \right] d \tau$

Then we have an expression for the gradient of our original expectation that only depends on the policy and reward function:

$\nabla_{\theta} \left[\mathbb{E}_{\tau \sim p_{\theta} (\tau)} \left[ \sum_{t=1}^T R \left[s_t, a_t \right]  \right] \right] = \mathbb{E}_{\tau \sim p_{\theta} (\tau)} \left[ \left( \sum_{t=1}^T \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] \right) \left( \sum_{t=1}^T R \left[s_t, a_t \right] \right)  \right]$

And we can approximate this gradient by taking $N$ samples of trajectories:

$\nabla_{\theta} \left[\mathbb{E}_{\tau \sim p_{\theta} (\tau)} \left[ \sum_{t=1}^T R \left[s_t, a_t \right]  \right] \right] \approx \frac{1}{N} \sum_{i=1}^N \left[ \left( \sum_{t=1}^T \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] \right) \left( \sum_{t=1}^T R \left[s_t, a_t \right] \right)  \right]$

## Sources

* [Policy gradients, Lecture 4, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_4_policy_gradient.pdf)