'''
Created on 28.08.2017

@author: Peer
'''

from collections import defaultdict
import datetime
from itertools import chain

import matplotlib.pyplot as plt

from gitexplorer.basics import GitExplorerBase


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


def collect_data(commits):
    '''
    '''

    information = defaultdict(int)

    for commit in commits:
        information[(commit['date'].isoweekday() - 1, commit['date'].hour)] += 1

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
        cursor = cursor.limit(number_of_commits)

    return cursor


if(__name__ == '__main__'):
    infos = collect_data(find_commits(days_before_reference=90,
                                      number_of_commits=None))

    draw_punchcard(infos)
    plt.show()
