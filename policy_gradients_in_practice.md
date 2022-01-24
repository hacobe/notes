# Policy gradients in practice

The basic gradient estimator for policy gradients is a high variance estimator.

To reduce the variance:

* Take our approximation to the gradient of the objective: $\frac{1}{N} \sum_{i=1}^N \left[ \left( \sum_{t=1}^T \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] \right) \left( \sum_{t=1}^T R \left[s_t^{(i)}, a_t^{(i)} \right] \right)  \right]$ and distribute the sum of rewards (distribute in this sense: (a + b) * (c + d) = (a * (c + d) + b * (c + d))) to get: $\frac{1}{N} \sum_{i=1}^N \left[ \sum_{t=1}^T \left( \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] \left( \sum_{t'=1}^T R \left[s_t^{(i)}, a_t^{(i)} \right] \right) \right)  \right]$ then use the "reward to go" instead of the total reward: $\frac{1}{N} \sum_{i=1}^N \left[ \sum_{t=1}^T \left( \nabla_{\theta} \left[ \log \pi_{\theta} (\tau) \right] \left( \sum_{t'=t}^T R \left[s_t^{(i)}, a_t^{(i)} \right] \right) \right)  \right]$
* Use a baseline to compare the reward for a sampled trajectory to. We want to distinguish the good trajectories from the bad ones, but we might sample trajectories that are all pretty good, e.g. reward 1000 vs 1002. Instead of just comparing on the reward, we select for unusually good rewards compared to some baseline. Replace the sum of rewards term with a sum of mean centered rewards term, where the average reward plays the role of the baseline here. The reward subtracted from some baseline is called the "advantage".
* Consider larger batches.
* May require more tuning of the learning rate than in supervised learning.

## Sources

* [Policy gradients, Lecture 4, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_4_policy_gradient.pdf)
