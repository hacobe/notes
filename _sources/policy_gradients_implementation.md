# Policy gradients implementation

* Before the training loop, build a policy network mapping from a state to a distribution over actions and randomly initialize its weights.
* There are 2 loops in the training loop. The outer loop iterates through multiple episodes and the inner loop through multiple time steps in an episode until the episode is terminated (e.g. by the environment).
* At the start of the inner loop, we reset the environment and get the initial state.
* How do we choose an action? By sampling from the probabilities outputted by the policy network plugging in the current state.
* During the inner loop simulating an episode, we collect (state, action, reward) experience tuples for training on later.
* We update the policy network parameters via training after each episode is terminated.
* Each training update uses only the experience tuples that we collected during the last episode.
* In training, the inputs to the model are a batch of states and the outputs of the model are the standardized sum of discounted rewards where the mean and standard deviation are taken from that episode, i.e., advantages, because we're using the mean as a baseline. In particular, outputs[t, a] = the sum of all future rewards starting at and including time t, discounted as the rewards get further away from time t, for the action a taken, and standardized.
* The loss is categorical cross-entropy loss, which is equivalent in this context to maximizing the sum of the product of the advantages and log policy network outputs, which results in gradient ascent on the sum of rewards.

Sketch of training loop:

    env = gym.make("CartPole-v1")

    for _ in range(num_episodes):
        state = env.reset()
        done = False   
        while not done:
            action = agent.get_action(state)
            next_state, reward, done, _ = env.step(action)
            agent.add_sample(state, action, reward)
            state = next_state

            if done:
                agent.train_model()
                agent.drop_samples()

## Sources

* [rlcode, CartPole REINFORCE](https://github.com/rlcode/reinforcement-learning/blob/master/2-cartpole/3-reinforce/cartpole_reinforce.py)