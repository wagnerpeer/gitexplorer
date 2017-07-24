'''
Created on 24.07.2017

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


def _authors_per_file_path():
    gitexplorer_database = get_gitexplorer_database()

    unwind = {'$unwind': '$details.modifications'}
    projection = {'$project': {'file_path': '$details.modifications.file_path',
                               'author': '$author',
                               'date': '$date',
                               'additions': '$details.modifications.additions',
                               'deletions': '$details.modifications.deletions'}}
    group = {'$group': {'_id': '$file_path',
                        'modifications': {'$push': {"author": "$author",
                                                    "date": "$date",
                                                    "additions": "$additions",
                                                    "deletions": "$deletions"}}}}
    projection2 = {'$project': {'_id': False,
                                'file_path': '$_id',
                                'modifications': '$modifications'}}

    out = {'$out': 'result_authors_per_file_path'}

    pipeline = [unwind, projection, group, projection2, out]

    gitexplorer_database.commit_collection.aggregate(pipeline)


def main():
    _authors_per_file_path()


if(__name__ == '__main__'):
    main()
