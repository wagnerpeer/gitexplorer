'''
Created on 05.07.2017

@author: Peer
'''

import pymongo
import calendar


def get_gitexplorer_database():
    '''Returns the MongoDB for gitexplorer.

    The collections inside the database can be used as basis for specialized collections
    from which one can derive elevated statistics. Results can also be written into the
    database to be accessible by visualization routines.
    '''
    client = pymongo.MongoClient()
    return client.gitexplorer_database


def _commits_by_weekday():
    gitexplorer_database = get_gitexplorer_database()

    projection = {'$project': {'day_of_week': {'$isoDayOfWeek': '$date'}}}
    group = {'$group': {'_id': '$day_of_week',
                        'total_commits': {'$sum': 1}}}

    pipeline = [projection, group]

    result = gitexplorer_database.commit_collection.aggregate(pipeline)

    document = {'commits_by_day': [{'weekday': calendar.day_name[item['_id'] - 1],
                                    'total_commits': item['total_commits']}
                                   for item in result]}

    gitexplorer_database.result_commits_by_weekday.drop()
    gitexplorer_database.result_commits_by_weekday.insert_one(document)


def _commits_by_hour_of_day():
    gitexplorer_database = get_gitexplorer_database()

    projection = {'$project': {'hour_of_day': {'$hour': '$date'}}}
    group = {'$group': {'_id': '$hour_of_day',
                        'total_commits': {'$sum': 1}}}

    pipeline = [projection, group]

    result = gitexplorer_database.commit_collection.aggregate(pipeline)

    document = {'commits_by_hour_of_day': [{'hour_of_day': item['_id'],
                                            'total_commits': item['total_commits']}
                                           for item in result]}

    gitexplorer_database.result_commits_by_hour_of_day.drop()
    gitexplorer_database.result_commits_by_hour_of_day.insert_one(document)


def _commits_by_date():
    gitexplorer_database = get_gitexplorer_database()

    projection = {'$project': {'date': '$date'}}
    group = {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d',
                                                  'date': '$date'}},
                        'total_commits': {'$sum': 1}}}

    pipeline = [projection, group]

    result = gitexplorer_database.commit_collection.aggregate(pipeline)

    document = {'commits_by_date': [{'date': item['_id'],
                                     'total_commits': item['total_commits']}
                                    for item in result]}

    gitexplorer_database.result_commits_by_date.drop()
    gitexplorer_database.result_commits_by_date.insert_one(document)


def main():
    _commits_by_weekday()
    _commits_by_hour_of_day()
    _commits_by_date()


if(__name__ == '__main__'):
    main()
