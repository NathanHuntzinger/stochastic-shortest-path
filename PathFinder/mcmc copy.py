# Used this tutorial for Metropolis-Hastings algorithm: https://exowanderer.medium.com/metropolis-hastings-mcmc-from-scratch-in-python-c21e53c485b7

import numpy as np

import random


def mcmc(reps, traffic, graph, ids, paths, weight_dists):
    """Uses Metropolis-Hastings algorithm in the pathfinder game loop"""
    samples = {
        'Group 1': {t_id: [] for t_id in ids},
        'Group 2': {t_id: [] for t_id in ids}
    }

    # Regenerate edge weights, uses 0 if weight is negative
    graph.es['weight'] = [max(0, weight_func()) for weight_func in weight_dists]

    for group in samples:
        # Metropolis-Hastings algorithm for each traveller/path
        for t_id in ids:
            state_func = lambda: get_path_length(graph, np.random.choice(paths[t_id]))
            samples[group][t_id] = metropolis_hastings(paths[t_id], reps, state_func)


def metropolis_hastings(paths, reps, state_func, burnin=0.2):
    """Metropolis-Hastings algorithm"""
    samples = []

    # The number of samples in the burn in phase
    idx_burnin = int(burnin * reps)

    # Set the current state to the initial state
    current_state = state_func()
    current_likelihood = likelihood(current_state)

    for i in range(reps):
        # Sampling and comparison occur within the mcmc_updater
        current_state, current_likelihood = mcmc_updater(current_state, current_likelihood)

        if i >= idx_burnin:
            samples.append(current_state)

    return samples


def mcmc_updater(current_state, current_likelihood, state_func):
    """Propose a new state and compare the likelihoods

    Given the current state (initially random) and current likelihood
    the `mcmc_updater` generates a new proposal, evaluate its likelihood,
    compares that to the current likelihood with a uniformly samples threshold,
    then it returns new or current state in the MCMC chain.
    """
    # Generate a proposal state using the proposal distribution
    new_state = state_func(current_state)

    # Calculate the acceptance criterion
    new_likelihood = likelihood(new_state)
    accept_crit = new_likelihood / current_likelihood

    # If the acceptance criterion is greater than the random number,
    # accept the proposal state as the current state
    accept_threshold = np.random.uniform(0, 1)
    if accept_crit > accept_threshold:
        return new_state, new_likelihood

    return current_state, current_likelihood


def likelihood(x):
    """tbh I don't know why this is the likelihood function"""
    return np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)


# def proposal_distribution(x, stepsize=0.5):
#     """Select the proposed state (new guess) from a Gaussian distribution
#     centered at the current state, within a Guassian of width `stepsize`
#     """
#     return np.random.normal(x, stepsize)


def consecutive_pairs(items):
    return zip(items, items[1:])


def get_path_length(graph, path):
    """Gets the length of the given path."""
    length = 0
    pairs = consecutive_pairs(path)
    for pair in pairs:
        length += graph.es['weight'][graph.get_eid(pair[0], pair[1])]

    return length
