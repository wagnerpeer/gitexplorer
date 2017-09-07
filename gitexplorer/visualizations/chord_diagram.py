'''
Created on 31.08.2017

@author: Peer
'''

import itertools
from collections import defaultdict, OrderedDict
import datetime
import math

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches

from gitexplorer.basics import GitExplorerBase


class AbstractSorter(object):

    @staticmethod
    def sort(nodes, edges):
        raise NotImplemented()


class LexicographicSorter(AbstractSorter):

    @staticmethod
    def sort(nodes, edges):
        nodes = OrderedDict(sorted(nodes.items(), key=lambda node: node[0]))
        edges = OrderedDict(sorted(edges.items(), key=lambda edge: edge[0][0]))

#         for items in zip(nodes.items(), edges.items()):
#             print(items)

        return nodes, edges


def draw_chord_diagram(data, sorter=LexicographicSorter, aggregate_below=0):
    '''Draw chord diagram [1]_ from input data.

    Parameters
    ----------
    data: dict
        A dictionary where in "nodes" is the information to be displayed as arc segments. It must contain another key
        called "edges" which is a dict describing the dependencies and their weights.

    References
    -----
    .. [1] https://en.wikipedia.org/wiki/Chord_diagram
    '''
    if len(data['nodes']) == 0:
        return

    data['nodes'], data['edges'] = sorter.sort(data['nodes'], data['edges'])

    figure = plt.figure()
    axes = figure.add_subplot(111, aspect='equal')

    linspace = [float(idx) / (len(data['nodes']) - 1.0) for idx in range(len(data['nodes']))]

    color = iter(cm.rainbow(linspace))

    node_value_sum = float(sum(data['nodes'].values()))
    start = 0.0
    radius = 50

    node_position = {}

    for node_name, node_value in data['nodes'].items():

        end = start + node_value / node_value_sum * 360

        arc = matplotlib.patches.Arc(xy=(0, 0),
                                     height=2 * radius,
                                     width=2 * radius,
                                     angle=0.0,
                                     theta1=start,
                                     theta2=end - 2.0,
                                     linewidth=8,
                                     color=next(color))

        axes.add_artist(arc)

        node_position[node_name] = math.radians((start + end) / 2.0)
        start = end

    max_edge_weight = float(max(data['edges'].values()))

    for (source, target), weight in data['edges'].items():
        source_x = math.cos(node_position[source]) * radius * 0.92
        source_y = math.sin(node_position[source]) * radius * 0.92

        target_x = math.cos(node_position[target]) * radius * 0.92
        target_y = math.sin(node_position[target]) * radius * 0.92

        distance = math.sqrt((source_x - target_x) ** 2 + (source_y - target_y) ** 2)

        value = abs(node_position[source] - node_position[target]) - math.pi
        sign = value / abs(value)

        connection_style = matplotlib.patches.ConnectionStyle('Arc3', rad=sign * (1.0 - distance / (2.0 * radius)))

        connection = matplotlib.patches.ConnectionPatch(xyA=(source_x, source_y),
                                                        xyB=(target_x, target_y),
                                                        coordsA='data',
                                                        connectionstyle=connection_style,
                                                        linewidth=16 * weight / max_edge_weight,
                                                        color='grey',
                                                        alpha=0.6,
                                                        capstyle='butt')

        axes.add_artist(connection)

    margin = 10
    axes.set_xlim([-radius - margin, radius + margin])
    axes.set_ylim([-radius - margin, radius + margin])

    plt.show()


def collect_data(commits):
    '''
    '''
    information = {'nodes': defaultdict(int),
                   'edges': defaultdict(int)}

    for commit in commits:

        current_nodes = []

        for modification in commit['details']['modifications']:
            current_node = modification['file_path']
            current_nodes.append(current_node)
            information['nodes'][current_node] += 1

        for combination in itertools.combinations(current_nodes, r=2):
            information['edges'][tuple(sorted(combination))] += 1

    return information


def find_commits(reference_day=datetime.datetime.today(),
                 days_before_reference=30,
                 number_of_commits=None):
    '''Load commits from database meeting certain conditions.

    Parameters
    ----------
    days_before_reference: int (>=0), optional
        Limit commits to number of days before reference_day
    number_of_commits: int (>=0), optional
        Limit the number of commits. If given it takes precedence before days_before_today.

    Returns
    -------
    Documents meeting criteria defined through parameters
    '''
    criteria = {}

    if(number_of_commits is None):
        datetime_limit = reference_day - datetime.timedelta(days=days_before_reference)
        criteria = {'date': {'$lte': reference_day, '$gte': datetime_limit}}

    gitexplorer_database = GitExplorerBase.get_gitexplorer_database()
    cursor = gitexplorer_database['commit_collection'].find(criteria)

    if(number_of_commits is not None):
        cursor = cursor.sort('date', -1).limit(number_of_commits)

    return cursor


if(__name__ == '__main__'):

    draw_chord_diagram(collect_data(find_commits(days_before_reference=30,
                                                 number_of_commits=None)),
                       aggregate_below=0)
