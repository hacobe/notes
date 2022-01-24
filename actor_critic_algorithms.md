# Actor-critic algorithms

Batch algorithm:

1. Sample trajectories from $\pi_{\theta}$ 
2. Train $\hat V_{\phi}^{\pi}$ on $\left\{ s_{i,t}, R \left[s_{i, t}, a_{i, t} \right] + \hat V_{\phi}^{\pi} \left(s_{i, t+1}\right) \right\}$
3. Evaluate $\hat A^{\pi}$
4. Estimate the policy gradient
5. Perform the policy gradient step on $\theta$

Online algorithm:

1. Take action $a \sim \pi_{\theta} \left(a | s \right)$, get $\left(s, a, s', R\left[s, a\right] \right)$
2. Update $\hat V_{\phi}^{\pi}$ with $\left \{ s, R\left[s, a\right] + \hat V_{\phi}^{\pi} \left(s' \right) \right \}$
3. Evaluate $\hat A^{\pi}$
4. Estimate the policy gradient
5. Perform the policy gradient step on $\theta$

## Sources

* [Actor-critic algorithms, Lecture 5, Sergey Levine](http://rll.berkeley.edu/deeprlcourse/f17docs/lecture_5_actor_critic_pdf.pdf)




