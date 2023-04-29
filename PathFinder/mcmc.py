import random

import numpy as np
import matplotlib.pyplot as plt

from . import graphtools


def mcmc(reps, traffic, graph, ids, paths, weight_dists):
    """Uses an adjusted MCMC algorithm in the pathfinder game loop"""
    shortest_paths = {
        'Group 1': {t_id: [] for t_id in ids},
        'Group 2': {t_id: [] for t_id in ids},
        'Group 3': {t_id: [] for t_id in ids},
    }

    graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]

    # Find the MCMC shortest path for each traveller in Groups 1 and 2
    for t_id in ids:
        # Start Group 1 from a random path
        initial_path1 = random.choice(paths[t_id])
        shortest_paths['Group 1'][t_id] = mcmc_shortest_path(initial_path1, reps, weight_dists, paths[t_id], graph)

        # Start Group 2 from the shortest path of Group 1
        initial_path2 = shortest_paths['Group 1'][t_id]
        shortest_paths['Group 2'][t_id] = mcmc_shortest_path(initial_path2, reps, weight_dists, paths[t_id], graph)

    # Generate the actual values for the experiment
    graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]

    # Add traffic to the shortest paths
    for t_id in ids:
        graphtools.add_traffic_to_path(shortest_paths['Group 1'][t_id], graph, traffic)
        graphtools.add_traffic_to_path(shortest_paths['Group 2'][t_id], graph, traffic)

    # Group 3 (Knows edge weights, so it doesn't need to explore)
    for t_id in ids:
        shortest_path = min(paths[t_id], key=lambda path: graphtools.get_path_length(path, graph))
        graphtools.add_traffic_to_path(shortest_path, graph, traffic)
        shortest_paths['Group 3'][t_id] = shortest_path

    # Plot the results
    group_names = ['Group 1', 'Group 2', 'Group 3']
    traveller_names = [f'Traveller {i}' for i in range(len(ids))]
    width = 0.25
    x = np.arange(len(ids))

    fig, ax = plt.subplots(layout='constrained', figsize=(10, 5))

    for i, group in enumerate(group_names):
        offset = i * width
        lengths = [
            round(graphtools.get_path_length(shortest_paths[group][t_id], graph), 1) for t_id in ids
        ]
        rects = ax.bar(x + offset, lengths, width, label=group)
        ax.bar_label(rects, padding=3)

    ax.set_ylabel('Path Length')
    ax.set_title('Path Lengths for Each Traveller')
    ax.set_xticks(x + width, traveller_names)
    ax.legend()

    plt.savefig('figures/mcmc_results.png')


def mcmc_shortest_path(initial_path, reps, weight_dists, paths, graph):
    """Markov chain Monte Carlo algorithm to find the shortest path in a
    stochastic graph.
    """
    current_path = initial_path
    best_path = current_path
    best_path_length = graphtools.get_path_length(best_path, graph)

    for _ in range(reps * 2):
        graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]

        candidate_path = random.choice(paths)
        acceptance_prob = calculate_acceptance_probability(candidate_path, current_path, graph)

        if np.random.uniform() < acceptance_prob:
            current_path = candidate_path

        path_length = graphtools.get_path_length(current_path, graph)
        if path_length < best_path_length:
            best_path = current_path
            best_path_length = path_length

    return best_path


def calculate_acceptance_probability(candidate_path, current_path, graph):
    """Calculate the acceptance probability for the candidate path."""
    current_cost = graphtools.get_path_length(current_path, graph)
    candidate_cost = graphtools.get_path_length(candidate_path, graph)

    acceptance_prob = min(1, np.exp(current_cost - candidate_cost))

    return acceptance_prob
