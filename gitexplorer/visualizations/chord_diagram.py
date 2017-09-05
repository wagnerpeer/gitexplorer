'''
Created on 31.08.2017

@author: Peer
'''

import itertools
from collections import defaultdict
import datetime

from basics import GitExplorerBase

import pandas as pd
from bokeh.charts import Chord
from bokeh.io import show


def _calculate_distance(data):
    return data


def _minimize_overlap(data):
    return data.sort_values(['source', 'target'])


def draw_chord_diagram(data, aggregate_below=0):
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

    source, target = zip(*data['edges'].keys())
    transformed_information = [{'source': source_name,
                                'target': target_name,
                                'value': value // 2} for source_name, target_name, value in zip(source,
                                                                                                target,
                                                                                                data['edges'].values())]

    data_frame = pd.DataFrame(transformed_information)
    data_frame = _minimize_overlap(data_frame[data_frame['value'] > aggregate_below])

    if not data_frame.empty:
        chord_from_df = Chord(data_frame, source="source", target="target", value="value")
        show(chord_from_df)


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

        for combination in itertools.permutations(current_nodes, r=2):
            information['edges'][tuple(sorted(combination))] += 1

    return information


def find_commits(days_before_today=30, number_of_commits=None):
    '''Load commits from database meeting certain conditions.

    Parameters
    ----------
    days_before_today: int (>=0), optional
        Limit commits to number of days before today
    number_of_commits: int (>=0), optional
        Limit the number of commits. If given it takes precedence before days_before_today.

    Returns
    -------
    Documents meeting criteria defined through parameters
    '''
    criteria = {}

    if(number_of_commits is None):
        datetime_limit = datetime.datetime.today() - datetime.timedelta(days=days_before_today)
        criteria = {'date': {'$gte': datetime_limit}}

    gitexplorer_database = GitExplorerBase.get_gitexplorer_database()
    cursor = gitexplorer_database['commit_collection'].find(criteria)

    if(number_of_commits is not None):
        cursor = cursor.sort('date', -1).limit(number_of_commits)

    return cursor


if(__name__ == '__main__'):

    draw_chord_diagram(collect_data(find_commits(days_before_today=30,
                                                 number_of_commits=100)),
                       aggregate_below=0)
