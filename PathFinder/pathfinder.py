import random

import igraph as ig
import matplotlib.pyplot as plt
import numpy as np


random.seed(42)


def create_graph(nodes, edges):
    g = ig.Graph.Erdos_Renyi(n=nodes, m=edges, directed=False, loops=False)
    print(f'Type: {type(g)}')

    # Set node labels
    g.vs['label'] = [i for i in range(nodes)]

    # Set edge weights
    weights = [np.random.normal(np.random.uniform(10, 15), np.random.uniform(.5, 3)) for _ in range(edges)]
    g.es['weight'] = weights
    # print(weights)

    max_weight = max(weights)
    edge_width = [w / max_weight * 3 for w in weights]
    # print(edge_width)

    # Find paths from node 0 to node 1
    paths = g.get_k_shortest_paths(0, 1, 10)
    # paths = g.get_all_paths(0, 1, weights='weight')
    print(paths)

    # Plot the graph
    ig.config['plotting.backend'] = 'matplotlib'
    ig.plot(
        g,
        target='figures/graph.png',
        bbox=(0, 0, 1024, 1024),
        margin=10,
        layout='auto',

        vertex_color="lightblue",
        vertex_size=.5,
        vertex_label_size=6,
        edge_width=edge_width,
        # edge_label=[f'{weight:.1f}' for weight in weights],
        # edge_align_label=True,
        # edge_label_size=6,
    )

    # Export and import a graph as a GML file.
    g.save("figures/graph.gml")
    # g = ig.load("social_network.gml")
