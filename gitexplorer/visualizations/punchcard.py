'''
Created on 28.08.2017

@author: Peer
'''

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import draw


def draw_punchcard_org(infos,
                ax1=range(7),
                ax2=range(24),
                ax1_ticks=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                ax2_ticks=range(24),
                ax1_label='Day',
                ax2_label='Hour'):

    # build the array which contains the values
    data = np.zeros((len(ax1), len(ax2)))
    for key in infos:
        data[key[0], key[1]] = infos[key]
    data = data / float(np.max(data))

    # shape ratio
    ratio = float(data.shape[1]) / data.shape[0]

    # Draw the punchcard (create one circle per element)
    # Ugly normalisation allows to obtain perfect circles instead of ovals....
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            circle = plt.Circle((x / ratio, y / ratio),
                                data[y][x] / ratio / 2)
            plt.gca().add_artist(circle)

    plt.ylim(0 - 0.5, data.shape[0] - 0.5)
    plt.xlim(0, data.shape[0])
    plt.yticks(np.arange(0, len(ax1) / ratio - .1, 1 / ratio), ax1_ticks)
    plt.xticks(np.linspace(0, len(ax1), len(ax2)) + 0.5 / float(data.shape[1]), ax2_ticks)
    plt.xlabel(ax1_label)
    plt.ylabel(ax2_label)
    plt.gca().invert_yaxis()

    # make sure the axes are equal, and resize the canvas to fit the plot
    plt.axis('equal')
    plt.axis([0, 7.02, 7.5 / ratio -0.02, -.5 + 0.5/ratio])
    scale = 0.5
    plt.gcf().set_size_inches(data.shape[1] * scale, data.shape[0] * scale, forward=True)


def draw_punchcard(infos,
                   xaxis_range=24,
                   yaxis_range=7,
                   xaxis_ticks=range(24),
                   yaxis_ticks=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                   xaxis_label='Hour',
                   yaxis_label='Day'):

    # build the array which contains the values
    data = np.zeros((yaxis_range, xaxis_range))
    for key, value in infos.items():
        data[key[1], key[0]] = value
    data = data / float(np.max(data))

    # shape ratio
    ratio = float(yaxis_range) / xaxis_range

    # Draw the punchcard (create one circle per element)
    # Ugly normalisation allows to obtain perfect circles instead of ovals....
    for x in range(xaxis_range):
        for y in range(yaxis_range):
            circle = plt.Circle((x * ratio, y * ratio),
                                data[y][x] * ratio / 2)
            plt.gca().add_artist(circle)

    plt.xlim(0, data.shape[0])
    plt.ylim(0, data.shape[0])

    plt.xticks(np.linspace(ratio, yaxis_range, xaxis_range), xaxis_ticks)
    plt.yticks(np.linspace(0, xaxis_range * ratio - ratio, yaxis_range), yaxis_ticks)

    plt.xlabel(xaxis_label)
    plt.ylabel(yaxis_label)
    plt.grid()
    plt.gca().invert_yaxis()

    # make sure the axes are equal, and resize the canvas to fit the plot
    plt.axis('equal')
    plt.axis([-1, 7, 7, -1])
    scale = 0.5
    plt.gcf().set_size_inches(data.shape[1] * scale, data.shape[0] * scale, forward=True)
    plt.tight_layout()


if(__name__ == '__main__'):
    hours = np.random.randint(0, 23, 1000)
    days = np.random.randint(0, 7, 1000)
    commits = np.random.randint(10, 100, 1000)

    infos = {key: value for key, value in zip(zip(days, hours), commits)}

    draw_punchcard_org(infos)
    plt.show()
