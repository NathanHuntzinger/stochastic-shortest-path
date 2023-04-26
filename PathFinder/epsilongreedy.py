import numpy as np


class Environment:
    def __init__(self, paths, graph):
        self.paths = paths
        self.graph = graph

    def step(self, action):
        """Returns cost given action"""
        cost = 0
        for edge in self.paths[action]:
            cost += self.graph.es['weight'][edge]



class Agent:
    def __init__(self, n_actions, epsilon):
        self.n_actions = n_actions
        self.epsilon = epsilon

        self.actions = np.zeros(n_actions)
        self.Q = np.zeros(n_actions)

    def update(self, action, reward):
        """Update Q value and epsilon given action and reward"""
        self.actions[action] += 1
        self.Q[action] += (reward - self.Q[action]) / self.actions[action]
        self.epsilon *= 0.99

    def get_action(self):
        """Epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            # explore
            return np.random.randint(self.n_actions)
        else:
            # exploit
            return np.random.choice(np.flatnonzero(self.Q == self.Q.min()))


# Start multi-armed bandit simulation
def epsilon_greedy(probs, N_episodes, eps):
    env = Environment(probs) # initialize arm probabilities
    agent = Agent(len(env.probs), eps)  # initialize agent
    actions, rewards = [], []
    for episode in range(N_episodes):
        action = agent.get_action() # sample policy
        reward = env.step(action) # take step + get reward
        if reward > max(0, np.random.normal(1.5, 3)):
            agent.update(action, reward) # update Q
            actions.append(action)
            rewards.append(reward)
        else:
            actions.append(0)
            rewards.append(0)
    return np.array(actions), np.array(rewards)
