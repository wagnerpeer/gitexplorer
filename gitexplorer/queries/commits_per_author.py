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


def _commits_per_author():
    gitexplorer_database = get_gitexplorer_database()

    projection = {'$project': {'author': '$author',
                               'commit_hash': '$commit_hash'}}
    group = {'$group': {'_id': '$author',
                        'total_commits': {'$sum': 1},
                        'commits': {'$push': '$commit_hash'}}}
    out = {'$out': 'result_commits_per_author'}
    pipeline = [projection, group, out]

    gitexplorer_database.commit_collection.aggregate(pipeline)


def main():
    _commits_per_author()


if(__name__ == '__main__'):
    main()
