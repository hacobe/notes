# Imitation learning

Let $\tau$ be a trajectory $\{s_t, a_t \}_{t=1}^T$ consisting of $T$ time steps, $p_{\psi}$ be the joint distribution over states and actions using the expert policy function $\pi_{\psi}$, and $\pi_{\theta}$ be the policy function we're trying to learn.

We find $\theta$ that maximizes:

$\mathbb{E}_{\tau \sim p_{\psi} (\tau)} \sum_{t=1}^T \log \pi_{\theta} \left(a_t | s_t \right)$

We approximate the expectation by sampling from $p_{\psi}$, i.e., collecting $N$ trajectories $\{ \tau_i \}_{i=1}^N$ from the expert taking actions in a fully observed environment:

$\sum_{i=1}^N \sum_{t=1}^T \left[ \log \pi_{\theta} \left(a_t^{(i)} | s_t^{(i)} \right) \right]$

## Sources

* [Supervised Learning of Behaviors, Lecture 2, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_2_behavior_cloning.pdf)

