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

    graph_layout = graph.layout_auto()  # Need this here so it doesn't change every time we plot

    choices = {
        'epsilon-greedy': {},
        'mcmc': {},
        'all-information': {}
    }

    epsilongreedy.epsilon_greedy(reps, epsilon, traffic, graph, ids, paths, weight_dists)


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
