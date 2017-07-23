'''
Created on 06.07.2017

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


def _additions_deletions_lines_per_commit():
    gitexplorer_database = get_gitexplorer_database()

    unwind = {'$unwind': '$details.modifications'}
    projection = {'$project': {'commit_hash': '$commit_hash',
                               'date': '$date',
                               'additions': '$details.modifications.additions',
                               'deletions': '$details.modifications.deletions'}}
    group = {'$group': {'_id': '$commit_hash',
                        'date': {'$first': '$date'},
                        'additions': {'$sum': '$additions'},
                        'deletions': {'$sum': '$deletions'},
                        'total_modifications': {'$sum': 1}}}

    pipeline = [unwind, projection, group]

    result = gitexplorer_database.commit_collection.aggregate(pipeline)

    document = {'additions_deletions_lines_per_commit': [{'commit_hash': item['_id'],
                                                          'date': item['date'],
                                                          'additions': item['additions'],
                                                          'deletions': item['deletions'],
                                                          'lines': item['additions'] - item['deletions'],
                                                          'total_modifications': item['total_modifications']}
                                                         for item in result]}

#     print(document)
    gitexplorer_database.result_additions_deletions_lines_per_commit.drop()
    gitexplorer_database.result_additions_deletions_lines_per_commit.insert_one(document)


def _additions_deletions_lines_by_date():
    gitexplorer_database = get_gitexplorer_database()

    unwind = {'$unwind': '$additions_deletions_lines_per_commit'}
    projection = {'$project': {'date': '$additions_deletions_lines_per_commit.date',
                               'additions': '$additions_deletions_lines_per_commit.additions',
                               'deletions': '$additions_deletions_lines_per_commit.deletions'}}
    group = {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d',
                                                  'date': '$date'}},
                        'total_additions': {'$sum': '$additions'},
                        'total_deletions': {'$sum': '$deletions'}}}

    pipeline = [unwind, projection, group]

    result = gitexplorer_database.result_additions_deletions_lines_per_commit.aggregate(pipeline)

    document = {'lines_by_date': [{'date': item['_id'],
                                   'total_additions': item['total_additions'],
                                   'total_deletions': item['total_deletions'],
                                   'total_lines': item['total_additions'] - item['total_deletions']}
                                  for item in result]}

    gitexplorer_database.result_lines_by_date.drop()
    gitexplorer_database.result_lines_by_date.insert_one(document)


def main():
    _additions_deletions_lines_per_commit()
    _additions_deletions_lines_by_date()


if(__name__ == '__main__'):
    main()
