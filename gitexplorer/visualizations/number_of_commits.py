'''
Created on 26.09.2017

@author: Peer
'''

import datetime

import pandas as pd
import matplotlib.pyplot as plt

from gitexplorer.basics import GitExplorerBase


def draw_number_of_commits(commits):
    data = pd.DataFrame(list(commits))

    data = data.sort_values('date')

    data['total_commits'] = data['total_commits'].cumsum()

    figure = plt.figure()
    axis = figure.add_subplot(1, 1, 1)

    data.plot('date', 'total_commits', ax=axis)

    axis.set_xlabel('Date')
    axis.set_ylabel('# Commits')


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
    cursor = gitexplorer_database['result_additions_deletions_lines_modifications_commits_by_date'].find(criteria)

    if(number_of_commits is not None):
        cursor = cursor.limit(number_of_commits)

    return cursor


if(__name__ == '__main__'):
    commits = find_commits(days_before_reference=90,
                           number_of_commits=1000)

    draw_number_of_commits(commits)
    plt.show()
