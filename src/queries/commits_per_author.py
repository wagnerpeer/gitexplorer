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
                        'total_commits': {'$sum': 1}}}

    pipeline = [projection, group]

    result = gitexplorer_database.commit_collection.aggregate(pipeline)

    document = {'additions_deletions_commits_by_file_path': [{'author': item['_id'],
                                                              'total_commits': item['total_commits']}
                                                             for item in result]}

#     print(document)
    gitexplorer_database.result_commits_per_author.drop()
    gitexplorer_database.result_commits_per_author.insert_one(document)



def main():
    _commits_per_author()


if(__name__ == '__main__'):
    main()
