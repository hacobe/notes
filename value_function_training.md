# Value function training

How do we estimate the value function $V^{\pi}$? (See the glossary for definitions of A, Q, and V).

1 sample estimate (sum the future rewards along one sampled trajectory):

$V^{\pi} \left( s_t \right) \approx \sum_{t' = t}^T R \left[s_{t'}, a_{t'} \right]$

Multi-sample estimate (average the future rewards along $N$ sampled trajectories, which requires resetting the simulation $N$ times):

$V^{\pi} \left( s_t \right) \approx \frac{1}{N} \sum_{i=1}^{N} \sum_{t' = t}^T R \left[s_{t'}, a_{t'} \right]$

Smooth over the 1 sample estimates by fitting a model and predicting the value based on the model. The training data is $\left \{\left(s_{i,t}, \sum_{t'=T} R \left[s_{i, t'}, a_{i, t'} \right] \right) \right \}$ and the loss is just L2 regression loss.

Use the previously fitted value function to reduce the variance of the label in the regression problem (similar trick used in the advantage from value post to write the Q function in terms of the value function). The training data becomes $\left \{\left(s_{i,t}, R \left[s_{i, t}, a_{i, t} \right] + \hat V_{\phi}^{\pi} \left(s_{i, t+1} \right) \right) \right \}$

# Sources

* [Actor-critic algorithms, Lecture 5, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_5_actor_critic_pdf.pdf)
