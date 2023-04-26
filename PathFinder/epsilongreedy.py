import numpy as np
from matplotlib import pyplot as plt


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


def epsilon_greedy(reps, epsilon, traffic, graph, ids, paths, weight_dists):
    actions1 = {}
    rewards1 = {}
    actions2 = {}
    rewards2 = {}
    actions3 = {}
    rewards3 = {}
    for t_id in ids:
        actions1[t_id] = []
        rewards1[t_id] = []
        actions2[t_id] = []
        rewards2[t_id] = []
        actions3[t_id] = []
        rewards3[t_id] = []

    agent1 = {t_id: Agent(len(paths[t_id]), epsilon) for t_id in ids}
    agent2 = {t_id: Agent(len(paths[t_id]), epsilon) for t_id in ids}

    # Main Game Loop
    for _ in range(reps):
        # Regenerate edge weights
        graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]  # Uses 0 if weight is negative

        # Get Actions/Rewards
        get_actions(traffic, graph, ids, paths, actions1, actions2, actions3, agent1, agent2)
        get_rewards(graph, ids, paths, actions1, rewards1, actions2, rewards2, actions3, rewards3, agent1, agent2)

    plot_results(reps, ids, rewards1, rewards2, rewards3)


def get_actions(traffic, graph, ids, paths, actions1, actions2, actions3, agent1, agent2):
    """Gets actions for each group. Does not return anything, but appends actions
    to actions1, actions2, and actions3.
    """
    for t_id in ids:
        # Group 1 (Only knows start, end, and results of past runs)
        action = agent1[t_id].get_action()
        actions1[t_id].append(action)
        add_traffic_to_path(graph, paths[t_id][action], traffic)

        # Group 2 (Gets all information from group 1, basically update this Q from group 1)
        action = agent2[t_id].get_action()
        actions2[t_id].append(action)
        add_traffic_to_path(graph, paths[t_id][action], traffic)

    # Group 3 (Knows edge weights, so it doesn't need to explore)
    for t_id in ids:
        shortest_path = min(paths[t_id], key=lambda path: get_path_length(graph, path))
        add_traffic_to_path(graph, shortest_path, traffic)

        action = paths[t_id].index(shortest_path)
        actions3[t_id].append(action)


def get_rewards(graph, ids, paths, actions1, rewards1, actions2, rewards2, actions3, rewards3, agent1, agent2):
    """Gets rewards for each group. Does not return anything, but appends rewards
    to rewards1, rewards2, and rewards3.
    """
    for t_id in ids:
        action = actions1[t_id][-1]
        reward1 = get_path_length(graph, paths[t_id][action])

        action = actions2[t_id][-1]
        reward2 = get_path_length(graph, paths[t_id][action])

        action = actions3[t_id][-1]
        reward3 = get_path_length(graph, paths[t_id][action])

        agent1[t_id].update(actions1[t_id][-1], reward1)
        agent2[t_id].update(actions2[t_id][-1], reward2)
        agent2[t_id].update(actions1[t_id][-1], reward1)  # Update group 2's Q with group 1's results

        rewards1[t_id].append(reward1)
        rewards2[t_id].append(reward2)
        rewards3[t_id].append(reward3)


def add_traffic_to_path(graph, path, traffic):
    """Adds traffic to the given path."""
    pairs = consecutive_pairs(path)
    for pair in pairs:
        graph.es['weight'][graph.get_eid(pair[0], pair[1])] += traffic


def consecutive_pairs(items):
    return zip(items, items[1:])


def get_path_length(graph, path):
    """Gets the length of the given path."""
    length = 0
    pairs = consecutive_pairs(path)
    for pair in pairs:
        length += graph.es['weight'][graph.get_eid(pair[0], pair[1])]

    return length


def get_running_avg(data, window):
    """Returns a list of the running averages of the given data."""
    running_avg = []
    for _ in range(window):
        running_avg.append(None)

    for i in range(len(data)):
        if i < window:
            continue
        else:
            running_avg.append(sum(data[i - window + 1:i + 1]) / window)

    return running_avg


def plot_results(reps, ids, rewards1, rewards2, rewards3):
    """Plots results as running average so it is easy to see trends"""
    avg_rewards1 = []
    avg_rewards2 = []
    avg_rewards3 = []

    for rep in range(reps):
        avg_rewards1.append(np.mean([rewards1[t_id][rep] for t_id in ids]))
        avg_rewards2.append(np.mean([rewards2[t_id][rep] for t_id in ids]))
        avg_rewards3.append(np.mean([rewards3[t_id][rep] for t_id in ids]))

    plt.subplot(1, 2, 1)
    plt.plot(avg_rewards1, label='Group 1')
    plt.plot(avg_rewards2, label='Group 2')
    plt.plot(avg_rewards3, label='Group 3')
    plt.title('Epsilon Greedy: Cost/Rep')
    plt.xlabel('Repetition')
    plt.ylabel('Cost')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(get_running_avg(avg_rewards1, 25), label='Group 1')
    plt.plot(get_running_avg(avg_rewards2, 25), label='Group 2')
    plt.plot(get_running_avg(avg_rewards3, 25), label='Group 3')
    plt.title('Epsilon Greedy: Running Average Cost/Rep')
    plt.xlabel('Repetition')
    plt.ylabel('Cost')
    plt.legend()

    plt.show()
