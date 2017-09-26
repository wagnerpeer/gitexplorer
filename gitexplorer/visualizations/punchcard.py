'''
Created on 28.08.2017

@author: Peer
'''

from itertools import chain
import matplotlib.pyplot as plt


def draw_punchcard(infos,
                   xaxis_range=24,
                   yaxis_range=7,
                   xaxis_ticks=range(24),
                   yaxis_ticks=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                   xaxis_label='Hour',
                   yaxis_label='Day'):

    # build the array which contains the values
    data = [[0.0] * xaxis_range for _ in range(yaxis_range)]
    for key, value in infos.items():
        data[key[0]][key[1]] = value

    max_value = float(max(chain.from_iterable(data)))

    # Draw the punchcard (create one circle per element)
    # Ugly normalisation allows to obtain perfect circles instead of ovals....
    for x in range(xaxis_range):
        for y in range(yaxis_range):
            circle = plt.Circle((x, y),
                                data[y][x] / 2 / max_value)
            plt.gca().add_artist(circle)

    plt.xlim(0, xaxis_range)
    plt.ylim(0, yaxis_range)

    plt.xticks(range(xaxis_range), xaxis_ticks)
    plt.yticks(range(yaxis_range), yaxis_ticks)

    plt.xlabel(xaxis_label)
    plt.ylabel(yaxis_label)
    plt.gca().invert_yaxis()

    # make sure the axes are equal, and resize the canvas to fit the plot
    plt.axis('scaled')

    margin = 0.7

    plt.axis([-margin, 23 + margin, 6 + margin, -margin])
    scale = 0.5
    plt.gcf().set_size_inches(xaxis_range * scale, yaxis_range * scale, forward=True)
    plt.tight_layout()


if(__name__ == '__main__'):
    import numpy as np
    hours = np.random.randint(0, 24, 1000)
    days = np.random.randint(0, 7, 1000)
    commits = np.random.randint(10, 100, 1000)

    infos = {key: value for key, value in zip(zip(days, hours), commits)}

    draw_punchcard(infos)
    plt.show()
