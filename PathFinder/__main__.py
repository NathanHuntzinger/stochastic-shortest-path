import numpy as np

from . import pathfinder


def main():
    nodes = 40
    edges = 50
    travellers = 5
    reps = 100
    pathfinder.run(nodes, edges, travellers, reps)


if __name__ == '__main__':
    main()
