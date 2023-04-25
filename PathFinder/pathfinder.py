import random

import igraph as ig
import numpy as np


random.seed(42)


def create_graph(nodes, edges):
    graph = ig.Graph.Erdos_Renyi(n=nodes, m=edges, directed=False, loops=False)

    # Set node labels
    graph.vs['label'] = [i for i in range(nodes)]

    # Set edge weights
    weight_dists = [getRandomDist() for _ in range(edges)]
    graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]  # Max 0 to prevent negative weights

    max_weight = max(graph.es['weight'])
    edge_widths = [w / max_weight * 3 for w in graph.es['weight']]  # Scale edge widths by max weight

    # Find paths from node 0 to node 1
    # paths = graph.get_k_shortest_paths(7, 11, 20)  # Maybe not the best way to do this because it goes off a single iteration's random weights
    paths = graph.get_all_simple_paths(7, 11, cutoff=10)  # Cutoff is set to 10 to prevent overwhelming the program

    # Sort paths by length
    paths.sort(key=len)

    # print(paths)

    # Print cost of each path
    for path in paths:
        cost = 0
        for i in range(len(path) - 1):
            cost += graph.es.find(_source=path[i], _target=path[i + 1])['weight']
        print(f'{len(path)} - Cost: {cost:.2f}')

    print(f'# of paths: {len(paths)}')

    # Plot the graph
    ig.config['plotting.backend'] = 'matplotlib'
    ig.plot(
        graph,
        target='figures/graph.png',
        bbox=(0, 0, 1024, 1024),
        margin=10,
        layout='auto',
        vertex_color="lightblue",
        vertex_size=.5,
        vertex_label_size=6,
        edge_width=edge_widths,
    )

    # Export graph to a .gml file
    graph.save("figures/graph.gml")


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
        std_dev = random.randint(1, 25)
        dist = lambda: dist_type(loc=mean, scale=std_dev)
        # print(f'normal distribution: {dist():.0f}, {dist():.0f}, {dist():.0f}')

    elif dist_type == np.random.beta:
        alpha = random.randint(1, 25)
        beta = random.randint(1, 25)
        dist = lambda: dist_type(a=alpha, b=beta) * 100
        # print(f'beta distribution: {dist():.0f}, {dist():.0f}, {dist():.0f}')

    return dist
