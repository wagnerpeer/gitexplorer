'''
Created on 31.08.2017

@author: Peer
'''

import itertools
from collections import defaultdict

from basics import GitExplorerBase

import pandas as pd
from bokeh.charts import Chord
from bokeh.io import show


def draw_chord_diagram(data):
    '''
    Parameters
    ----------
    data: dict
        A dictionary where in "nodes" is the information to be displayed as arc segments. As values it must contain
        another dict describing the dependencies and their weights.
    '''
    source, target = zip(*data['edges'].keys())
    transformed_information = [{'source': source_val,
                                'target': target_val,
                                'value': value // 2} for source_val, target_val, value in zip(source,
                                                                                              target,
                                                                                              data['edges'].values())]

    data_frame = pd.DataFrame(transformed_information)
    chord_from_df = Chord(data_frame, source="source", target="target", value="value")
    show(chord_from_df)


def collect_data(commits):
    information = {'nodes': defaultdict(int),
                   'edges': defaultdict(int)}

    for commit in commits:

        current_nodes = []

        for modification in commit['details']['modifications']:
            current_node = modification['file_path']
            current_nodes.append(current_node)
            information['nodes'][current_node] += 1

        for combination in itertools.permutations(current_nodes, r=2):
            information['edges'][tuple(sorted(combination))] += 1

    return information


def get_commits():
    gitexplorer_database = GitExplorerBase.get_gitexplorer_database()
    return gitexplorer_database['commit_collection'].find()


if(__name__ == '__main__'):

    draw_chord_diagram(collect_data(get_commits()[:10]))
