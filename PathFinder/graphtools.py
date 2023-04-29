def add_traffic_to_path(path, graph, traffic):
    """Adds traffic to the given path."""
    pairs = consecutive_pairs(path)
    for pair in pairs:
        graph.es['weight'][graph.get_eid(pair[0], pair[1])] += traffic


def consecutive_pairs(items):
    return zip(items, items[1:])


def get_path_length(path, graph):
    """Gets the length of the given path."""
    length = 0
    pairs = consecutive_pairs(path)
    for pair in pairs:
        length += graph.es['weight'][graph.get_eid(pair[0], pair[1])]

    return length
