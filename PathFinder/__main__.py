import numpy as np

from . import pathfinder


def main():
    kwargs = {
        'nodes': 40,
        'edges': 50,
        'travellers': 10,
        'reps': 150,
        'epsilon': 0.2,
        'traffic': 5
    }

    pathfinder.run(**kwargs)


if __name__ == '__main__':
    main()
