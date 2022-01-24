# Actor-critic methods

Recall that we're trying to maximize the following expectation in reinforcement learning:

$\mathbb{E}_{\tau \sim p_{\theta} (\tau)} \left[ \sum_{t=1}^T R \left[s_t, a_t \right]  \right]$

where $\tau = \left( s_1, a_1, \dots, s_T, a_T \right)$ is a trajectory distributed according to $p_{\theta}$, which depends on the policy function $\pi_{\theta}$.

And that for the REINFORCE algorithm, we do gradient ascent to find the $\theta$ that maximizes this expectation using $N$ sample trajectories to approximate the gradient of the expectation:

$\nabla_{\theta} \left[\mathbb{E}_{\tau \sim p_{\theta} (\tau)} \left[ \sum_{t=1}^T R \left[s_t, a_t \right]  \right] \right] \approx \frac{1}{N} \sum_{i=1}^N \left[ \sum_{t=1}^T \left( \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] \left( \sum_{t'=t}^T R \left[s_t^{(i)}, a_t^{(i)} \right] \right) \right)  \right]$

$\sum_{t'=t}^T R \left[s_t^{(i)}, a_t^{(i)} \right]$ is an estimate $\hat Q_t^{(i)}$ of the expected sum of remaining rewards if we take $a_t^{(i)}$ in state $s_t^{(i)}$. It's a one sample estimate taken by summing the rewards in that particular trajectory (the $i$th trajectory).

The better our estimate of this term, the more we reduce the variance of our estimator (though we may introduce a little bias, which can be a good trade-off). We can use advantages (Q values - a baseline) instead of just Q values and also reason about the expectation of the advantage instead of just a sample of it and think about better ways to estimate $A^{\pi}$:

$\frac{1}{N} \sum_{i=1}^N \left[ \sum_{t=1}^T \left( \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] A^{\pi} \left(s_t, a_t \right) \right) \right]$

Actor-critic methods involve fitting both a policy function $\pi_{\theta}$ (the actor) and a separate critic function. The critic function can be modeled in different ways, but one common approach is to make the critic function predict values, i.e., $\hat V_{\phi}^{\pi}(s_t)$, where $\phi$ are the parameters of that function, and then calculate $\hat A^{\pi}$ from the predicted values and plug it into the sum above. The goal being to reduce the variance of the vanilla policy gradients estimator.

## Sources

* [Actor-critic algorithms, Lecture 5, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_5_actor_critic_pdf.pdf)
