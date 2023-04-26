import random
import uuid

import igraph as ig
import numpy as np
from matplotlib import pyplot as plt

from . import epsilongreedy


random.seed(42)


def run(nodes, edges, travellers, reps, epsilon, traffic):
    """Runs the program."""
    graph = create_graph(nodes, edges)

    ids = [uuid.uuid4() for _ in range(travellers)]
    traveller_goals = {t_id: create_goal(nodes, graph) for t_id in ids}
    paths = {t_id: get_paths(graph, traveller_goals[t_id]) for t_id in ids}
    weight_dists = [getRandomDist() for _ in range(edges)]

    graph_layout = graph.layout_auto()

    choices = {
        'epsilon-greedy': {},
        'mcmc': {},
        'all-information': {}
    }

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

    agent1 = {t_id: epsilongreedy.Agent(len(paths[t_id]), epsilon) for t_id in ids}
    agent2 = {t_id: epsilongreedy.Agent(len(paths[t_id]), epsilon) for t_id in ids}

    # Main Game Loop
    for rep in range(reps):
        # Regenerate edge weights
        graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]  # Uses 0 if weight is negative
        # plot_graph(graph, rep, graph_layout)

        # Strategy 1 (Epsilon Greedy)

        # Get Actions
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

        # Get Rewards
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

    avg_rewards1 = []
    avg_rewards2 = []
    avg_rewards3 = []

    for rep in range(reps):
        avg_rewards1.append(np.mean([rewards1[t_id][rep] for t_id in ids]))
        avg_rewards2.append(np.mean([rewards2[t_id][rep] for t_id in ids]))
        avg_rewards3.append(np.mean([rewards3[t_id][rep] for t_id in ids]))

    plt.close()
    plt.plot(get_running_avg(avg_rewards1, 25), label='Group 1')
    plt.plot(get_running_avg(avg_rewards2, 25), label='Group 2')
    plt.plot(get_running_avg(avg_rewards3, 25), label='Group 3')
    plt.title('Running Average of Cost Per Repetition')
    plt.xlabel('Repetition')
    plt.ylabel('Cost')
    plt.legend()
    plt.show()


def get_paths(graph, goal):
    """Get a shortened list of paths from start to end."""
    goal = graph.get_all_simple_paths(goal['start'], goal['end'])
    goal.sort(key=len)

    if len(goal) > 25:
        goal = goal[:25]

    return goal


def create_goal(nodes, graph):
    goal = {'start': random.randint(0, nodes - 1), 'end': random.randint(0, nodes - 1)}

    while goal['start'] == goal['end']:
        goal['end'] = random.randint(0, nodes - 1)  # Don't want start and end to be the same

    if not graph.are_connected(goal['start'], goal['end']):
        goal = create_goal(nodes, graph)  # Don't want start and end to be disconnected

    return goal


def create_graph(nodes, edges):
    graph = ig.Graph.Erdos_Renyi(n=nodes, m=edges, directed=False, loops=False)
    graph.vs['label'] = [i for i in range(nodes)]
    return graph


def plot_graph(graph, rep, layout):
    """Plots the graph and saves it to a .png file and a .gml file."""
    max_weight = max(graph.es['weight'])
    scale = 3
    edge_widths = [weight / max_weight * scale for weight in graph.es['weight']]  # Scale edge widths by max weight

    ig.config['plotting.backend'] = 'matplotlib'
    ig.plot(
        graph,
        target=f'figures/graph{rep}.png',
        bbox=(0, 0, 1024, 1024),
        margin=10,
        layout=layout,
        vertex_color="lightblue",
        vertex_size=.6,
        vertex_label_size=6,
        edge_width=edge_widths,
    )

    # Export graph to a .gml file
    # graph.save("figures/graph.gml")


def getRandomDist():
    """Returns a random distribution function. Values should be between 0 and
    100, but this is not tested. May need to protect against negative values.
    """
    dists = [
        np.random.uniform,
        np.random.normal,
        np.random.beta,
    ]

    dist_type = random.choice(dists)

    if dist_type == np.random.uniform:
        dist_range = [random.randint(1, 100), random.randint(1, 100)]
        dist_range.sort()
        dist = lambda: dist_type(low=dist_range[0], high=dist_range[1])
        # print(f'Uniform distribution: {dist():.0f}, {dist():.0f}, {dist():.0f}')

    elif dist_type == np.random.normal:
        mean = random.randint(25, 75)
        std_dev = random.randint(5, 30)
        dist = lambda: dist_type(loc=mean, scale=std_dev)
        # print(f'normal distribution: {dist():.0f}, {dist():.0f}, {dist():.0f}')

    elif dist_type == np.random.beta:
        alpha = random.randint(2, 20)
        beta = random.randint(2, 20)
        dist = lambda: dist_type(a=alpha, b=beta) * 100
        # print(f'beta distribution: {dist():.0f}, {dist():.0f}, {dist():.0f}')

    return dist


def consecutive_pairs(items):
    return zip(items, items[1:])


def get_path_length(graph, path):
    """Gets the length of the given path."""
    length = 0
    pairs = consecutive_pairs(path)
    for pair in pairs:
        length += graph.es['weight'][graph.get_eid(pair[0], pair[1])]

    return length


def add_traffic_to_path(graph, path, traffic):
    """Adds traffic to the given path."""
    pairs = consecutive_pairs(path)
    for pair in pairs:
        graph.es['weight'][graph.get_eid(pair[0], pair[1])] += traffic


def get_running_avg(data, window):
    """Returns a list of the running averages of the given data."""
    running_avg = []
    for i in range(len(data)):
        if i < window:
            continue
        else:
            running_avg.append(sum(data[i - window + 1:i + 1]) / window)

    return running_avg
