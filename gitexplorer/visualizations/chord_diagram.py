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

        return nodes, edges


class MinimumLengthSorter(AbstractSorter):

    @staticmethod
    def sort(nodes, edges):

        import numpy as np

        combinations = itertools.combinations(range(len(nodes)), r=len(nodes))
        index_to_node = {idx: edge for idx, edge in enumerate(nodes.keys())}

        min_combination = None
        min_combination_weight = 2e32

        node_pos = np.arange(1.0 * len(nodes)) / len(nodes)

        for combination in combinations:
            combination_weight = 0.0

            for source in combination:
                for target in combination:
                    edge_weight = edges.get((index_to_node[source], index_to_node[target]))
                    if(edge_weight is not None):
                        combination_weight += ((node_pos[source] - node_pos[target]) % 1.0)# * edge_weight

            if(combination_weight <= min_combination_weight):
                min_combination_weight = combination_weight
                min_combination = combination

        new_nodes = OrderedDict()
        for node_idx in min_combination:
            new_nodes[index_to_node[node_idx]] = nodes[index_to_node[node_idx]]

        return new_nodes, edges


class MinimizeCrossingsSorter(AbstractSorter):

    @staticmethod
    def sort(nodes, edges):
        import numpy as np

        def find_nearest(array, value):
            idx = (np.abs(array - value)).argmin()
            return idx

        size = len(nodes)

        node_order = {node_name: idx for idx, node_name in enumerate(nodes.keys())}

        relationship_matrix = np.zeros((size, size))

        for (source, target), weight in edges.items():
            relationship_matrix[node_order[source], node_order[target]] = 1

        lstsq_relationship = -np.linalg.lstsq(relationship_matrix,
                                              np.ones((size,)))[0]

        lstsq_relationship -= lstsq_relationship.min()
        lstsq_relationship /= lstsq_relationship.max()
        lstsq_relationship *= size

        sorting_indices = list(range(size))
        inverse_node_order = {idx: node_name for idx, node_name in zip(node_order.values(), node_order.keys())}
        new_nodes = OrderedDict()

        for value in lstsq_relationship:
            idx = sorting_indices.pop(find_nearest(sorting_indices, value))
            node_name = inverse_node_order[idx]
            new_nodes[node_name] = nodes[node_name]

        return new_nodes, edges


class MinimizeCrossingsSorterPinv(AbstractSorter):

    @staticmethod
    def sort(nodes, edges):
        import numpy as np

        def find_nearest(array, value):
            idx = (np.abs(array - value)).argmin()
            return idx

        size = len(nodes)

        node_order = {node_name: idx for idx, node_name in enumerate(nodes.keys())}

        relationship_matrix = np.zeros((size, size))

        for (source, target), weight in edges.items():
            relationship_matrix[node_order[source], node_order[target]] = 1

        pseudo_inverse = np.linalg.pinv(relationship_matrix)

        lstsq_relationship = np.dot(pseudo_inverse, np.ones((size,)))

        sorting_indices = list(range(size))
        inverse_node_order = {idx: node_name for idx, node_name in zip(node_order.values(), node_order.keys())}
        new_nodes = OrderedDict()

        for value in lstsq_relationship:
            idx = sorting_indices.pop(find_nearest(sorting_indices, value))
            node_name = inverse_node_order[idx]
            new_nodes[node_name] = nodes[node_name]

        return new_nodes, edges


def draw_chord_diagram(data, sorter=LexicographicSorter, aggregate_below=1):
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

    new_edges = {}
    for edge, value in data['edges'].items():
        if(value > aggregate_below):
            new_edges[edge] = value

    data['edges'] = new_edges

    active_nodes = set()
    for source, target in data['edges'].keys():
        active_nodes.add(source)
        active_nodes.add(target)

    new_nodes = {}
    for node, value in data['nodes'].items():
        if(node in active_nodes):
            new_nodes[node] = value

    data['nodes'] = new_nodes

    data['nodes'], data['edges'] = sorter.sort(data['nodes'], data['edges'])

    figure = plt.figure()
    axes = figure.add_subplot(111, aspect='equal')

    linspace = [float(idx) / (len(data['nodes']) - 1.0) for idx in range(len(data['nodes']))]

    color = iter(cm.rainbow(linspace))

    node_value_sum = float(sum(data['nodes'].values()))
    start = 0.0
    radius = 50

    inner_margin = 0.15
    outer_margin = 0.15

    node_position = {}

    for node_name, node_value in data['nodes'].items():

        end = start + node_value / node_value_sum * 360

        arc = matplotlib.patches.Arc(xy=(0, 0),
                                     height=2 * radius,
                                     width=2 * radius,
                                     angle=0.0,
                                     theta1=start + 1.0,
                                     theta2=end - 1.0,
                                     linewidth=8,
                                     color=next(color))

        axes.add_artist(arc)

        position = ((start + end) / 2.0) % 360.0

        if(position < 90):
            halignment = 'left'
            valignment = 'bottom'
            rotation = position
        elif(position < 180):
            halignment = 'right'
            valignment = 'bottom'
            rotation = position + 180
        elif(position < 270):
            halignment = 'right'
            valignment = 'top'
            rotation = position + 180
        elif(position < 360):
            halignment = 'left'
            valignment = 'top'
            rotation = position

        axes.annotate(node_name,
                      xy=(math.radians(position), radius * (1.0 + outer_margin)),
                      xycoords='polar',
                      rotation=rotation,
                      horizontalalignment=halignment,
                      verticalalignment=valignment,
                      )

        axes.axis('off')

        node_position[node_name] = math.radians(position)
        start = end

    max_edge_weight = float(max(data['edges'].values()))

    for (source, target), weight in data['edges'].items():
        if(node_position[source] >= node_position[target]):
            node_position[source], node_position[target] = node_position[target], node_position[source]
        source_x = math.cos(node_position[source]) * radius * (1.0 - inner_margin)
        source_y = math.sin(node_position[source]) * radius * (1.0 - inner_margin)

        target_x = math.cos(node_position[target]) * radius * (1.0 - inner_margin)
        target_y = math.sin(node_position[target]) * radius * (1.0 - inner_margin)

        distance = math.sqrt((source_x - target_x) ** 2 + (source_y - target_y) ** 2)

        value = abs(node_position[source] - node_position[target]) - math.pi
        sign = value / abs(value)

        connection_style = matplotlib.patches.ConnectionStyle('Arc3', rad=sign * (1.0 - distance / (2.0 * radius)))

        connection = matplotlib.patches.ConnectionPatch(xyA=(source_x, source_y),
                                                        xyB=(target_x, target_y),
                                                        coordsA='data',
                                                        connectionstyle=connection_style,
                                                        linewidth=8.0 * weight / max_edge_weight,
                                                        color='grey',
                                                        alpha=0.6,
                                                        capstyle='butt')

        axes.add_artist(connection)

    margin = 100
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
#                                                  reference_day=datetime.datetime(day=1, month=1, year=2012),
                                                 number_of_commits=150)),
#                         sorter=MinimumLengthSorter,
                        sorter=MinimizeCrossingsSorterPinv,
#                         sorter=MinimizeCrossingsSorter,
                       aggregate_below=2)
