'''
Created on 05.07.2017

@author: Peer
'''

import pymongo


def get_gitexplorer_database():
    '''Returns the MongoDB for gitexplorer.

    The collections inside the database can be used as basis for specialized collections
    from which one can derive elevated statistics. Results can also be written into the
    database to be accessible by visualization routines.
    '''
    client = pymongo.MongoClient()
    return client.gitexplorer_database


def _commits_by_day_of_week():
    gitexplorer_database = get_gitexplorer_database()

    projection = {'$project': {'day_of_week': {'$isoDayOfWeek': '$date'}}}
    group = {'$group': {'_id': '$day_of_week',
                        'total_commits': {'$sum': 1}}}
    out = {'$out': 'result_commits_by_day_of_week'}
    pipeline = [projection, group, out]

    gitexplorer_database.commit_collection.aggregate(pipeline)


def _commits_by_hour_of_day():
    gitexplorer_database = get_gitexplorer_database()

    projection = {'$project': {'hour_of_day': {'$hour': '$date'}}}
    group = {'$group': {'_id': '$hour_of_day',
                        'total_commits': {'$sum': 1}}}
    out = {'$out': 'result_commits_by_hour_of_day'}
    pipeline = [projection, group, out]

    gitexplorer_database.commit_collection.aggregate(pipeline)


def main():
    _commits_by_day_of_week()
    _commits_by_hour_of_day()


if(__name__ == '__main__'):
    main()
