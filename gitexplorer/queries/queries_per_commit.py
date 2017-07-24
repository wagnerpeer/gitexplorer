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


def _additions_deletions_lines_files_per_commit():
    gitexplorer_database = get_gitexplorer_database()

    unwind = {'$unwind': '$details.modifications'}
    projection = {'$project': {'commit_hash': '$commit_hash',
                               'date': '$date',
                               'modifications': '$details.modifications'}}
    group = {'$group': {'_id': '$commit_hash',
                        'date': {'$first': '$date'},
                        'total_additions': {'$sum': '$modifications.additions'},
                        'total_deletions': {'$sum': '$modifications.deletions'},
                        'total_modifications': {'$sum': 1},
                        'file_paths': {'$push': '$modifications.file_path'},
                        'total_lines': {'$sum': {'$subtract': ['$modifications.additions',
                                                               '$modifications.deletions']}}}}
    out = {'$out': 'result_additions_deletions_lines_files_per_commit'}
    pipeline = [unwind, projection, group, out]

    gitexplorer_database.commit_collection.aggregate(pipeline)


def _additions_deletions_lines_commits_by_date():
    gitexplorer_database = get_gitexplorer_database()

    group = {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d',
                                                  'date': '$date'}},
                        'date': {'$first': '$date'},
                        'total_additions': {'$sum': '$total_additions'},
                        'total_deletions': {'$sum': '$total_deletions'},
                        'total_commits': {'$sum': 1}}}
    out = {'$out': 'result_additions_deletions_lines_commits_by_date'}
    pipeline = [group, out]

    gitexplorer_database.result_additions_deletions_lines_files_per_commit.aggregate(pipeline)


def main():
    _additions_deletions_lines_files_per_commit()
    _additions_deletions_lines_commits_by_date()


if(__name__ == '__main__'):
    main()
