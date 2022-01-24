# Reinforcement learning glossary

* Policy: A function from a state or an observation to a distribution over actions, i.e. $p \left(a_t | o_t \right) = \pi_{\theta} \left(a_t | o_t \right)$ where $\pi_{\theta}$ is the policy.
* State: State fully encapsulates the environment and has the Markov property that $P(s_t | s_{t-1}, a_t) = P(s_t | s_{t-1}, s_{t-2}, \dots, s_{0}, a_t)$, i.e. it's what enables you to decouple the future from the past.
* Observation: Fully or partially observed state. If partially observed, it doesn't necessarily have the Markov property.
* Q function: Total expected reward through all remaining time steps from taking $a_t$ in $s_t$. $Q^{\pi} \left(s_t, a_t \right) = \sum_{t'=t}^T \mathbb{E}_{\pi_{\theta}} \left[R\left[s_{t'}, a_{t'} \right] | s_t, a_t \right]$
* Value function: Total expected reward through all remaining time steps from $s\_t$. $V^{\pi} \left(s\_t \right) = \mathbb{E}_{a_t \sim \pi_{\theta}(a_t | s_t)} \left[Q^{\pi} \left(s_t, a_t \right) \right]$
* Advantage function: How much better is $a_t$ from we expect on average? $A^{\pi} \left(s_t, a_t \right) = Q^{\pi} \left(s_t, a_t \right) - V^{\pi} \left(s_t \right)$

