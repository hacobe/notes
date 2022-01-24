# Estimating advantage from the value function

Recall that we can rewrite the reinforcement learning objective as:

$\frac{1}{N} \sum_{i=1}^N \left[ \sum_{t=1}^T \left( \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] A^{\pi} \left(s_t, a_t \right) \right) \right]$

How do we estimate $A^{\pi}$? (See the glossary for definitions of A, Q, and V.)

First we write $Q^{\pi}$ as the sum of the reward at time $t$ and the expectation of the value, i.e. the sum of the future rewards, over the state transition distribution:

$Q^{\pi} \left(s_t, a_t \right) = R \left[ s_t, a_t \right] + \mathbb{E}_{s_{t+1} \sim p \left(s_{t+1} | s_t, a_t \right)} \left[ V^{\pi} \left(s_{t+1} \right) \right]$

We approximate $\mathbb{E}_{s_{t+1} \sim p \left(s_{t+1} | s_t, a_t \right)} \left[ V^{\pi} \left(s_{t+1} \right) \right]$ with just $V^{\pi} \left(s_{t+1} \right)$ by using a single sample estimate of the next state $s_{t+1}$. Then:

$A^{\pi} \left(s_t, a_t \right) \approx R \left[ s_t, a_t \right] + V^{\pi} \left(s\_{t+1} \right) - V^{\pi} \left(s\_t \right)$

In this way, we only have to fit a function of states (and not states and actions) to estimate the advantage.

## Sources

* [Actor-critic algorithms, Lecture 5, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_5_actor_critic_pdf.pdf)

