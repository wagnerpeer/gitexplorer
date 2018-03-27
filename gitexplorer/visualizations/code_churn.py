"""
Created on 28.08.2017

@author: Peer
"""

import datetime

import matplotlib.pyplot as plt
import pandas
import pymongo

from gitexplorer.basics import GitExplorerBase


def _align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    _adjust_yaxis(ax2,(y1-y2)/2,v2)
    _adjust_yaxis(ax1,(y2-y1)/2,v1)


def _adjust_yaxis(ax, ydif, v):
    """Shift axis ax by ydiff, maintaining point v at the same location"""
    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
    miny, maxy = ax.get_ylim()
    miny, maxy = miny - v, maxy - v
    if -miny>maxy or (-miny==maxy and dy > 0):
        nminy = miny
        nmaxy = miny*(maxy+dy)/(miny+dy)
    else:
        nmaxy = maxy
        nminy = maxy*(miny+dy)/(maxy+dy)
    ax.set_ylim(nminy+v, nmaxy+v)


def draw_code_churn(commits):
    data = pandas.DataFrame(commits)

    data['lines'] = data['total_additions'] - data['total_deletions']
    data['lines'] = data['lines'].cumsum()

    data['total_deletions'] = -1 * data['total_deletions']

    figure = plt.figure()
    axis = figure.add_subplot(1, 1, 1)
    second_axis = axis.twinx()

    data.plot('date', 'lines', ax=axis)
    data.plot('date', 'total_additions', color='g', ax=second_axis)
    data.plot('date', 'total_deletions', color='r', ax=second_axis)

    second_axis.legend(loc='center right')

    _align_yaxis(axis, 0, second_axis, 0)

    axis.set_ylabel('LOC')
    second_axis.set_ylabel('Additions / Deletions')
    axis.set_xlabel('Date')

    axis.grid()
    plt.show()


def draw_number_of_commits(commits):
    data = pandas.DataFrame(commits)

    data['total_commits'] = data['total_commits'].cumsum()

    figure = plt.figure()
    axis = figure.add_subplot(1, 1, 1)

    data.plot('date', 'total_commits', ax=axis)

    axis.set_ylabel('# commits')
    axis.set_xlabel('Date')

    axis.grid()
    plt.show()


def find_commits(reference_day=datetime.datetime.today(),
                 days_before_reference=30,
                 number_of_commits=None,
                 authors=None):
    """Load commits from database meeting certain conditions.

    Parameters
    ----------
    reference_day: datetime
        Reference date
    days_before_reference: int (>=0), optional
        Limit commits to number of days before reference_day
    number_of_commits: int (>=0), optional
        Limit the number of commits. If given it takes precedence before days_before_reference.
    author: tuple of str
        Filter by names of authors

    Returns
    -------
    Documents meeting criteria defined through parameters
    """
    criteria = {}

    if number_of_commits is None:
        datetime_limit = reference_day - datetime.timedelta(days=days_before_reference)
        criteria['date'] = {'$lte': reference_day, '$gte': datetime_limit}

    # if authors is not None:
    #     criteria['author'] = {'$in': list(authors)}

    gitexplorer_database = GitExplorerBase.get_gitexplorer_database()
    cursor = gitexplorer_database['result_additions_deletions_lines_modifications_commits_by_date'].find(criteria)

    if number_of_commits is not None:
        cursor = cursor.sort('date', pymongo.ASCENDING).limit(number_of_commits)

    return cursor


if __name__ == '__main__':
    commits = list(find_commits(days_before_reference=90,
                                # reference_day=datetime.datetime(day=1, month=1, year=2012),
                                number_of_commits=1500,
                                authors=("Peer Wagner",)),)
    draw_code_churn(commits)
    draw_number_of_commits(commits)
