'''
Created on 05.07.2017

@author: Peer
'''

import pymongo

INVERSE_TRANSLATION_TABLE = str.maketrans({'\uff0e': '.',
                                           '\uff04': '$'})


def _mongodb_unescape(input_string):
    return input_string.translate(INVERSE_TRANSLATION_TABLE)


def get_gitexplorer_database():
    '''Returns the MongoDB for gitexplorer.

    The collections inside the database can be used as basis for specialized collections
    from which one can derive elevated statistics. Results can also be written into the
    database to be accessible by visualization routines.
    '''
    client = pymongo.MongoClient()
    return client.gitexplorer_database


def _additions_deletions_lines_commits_by_file_path():
    gitexplorer_database = get_gitexplorer_database()

    unwind = {'$unwind': '$details.modifications'}
    projection = {'$project': {'file_path': '$details.modifications.file_path',
                               'additions': '$details.modifications.additions',
                               'deletions': '$details.modifications.deletions'}}
    group = {'$group': {'_id': '$file_path',
                        'total_commits': {'$sum': 1},
                        'total_additions': {'$sum': '$additions'},
                        'total_deletions': {'$sum': '$deletions'},
                        'total_lines': {'$sum': {'$add': ['$additions',
                                                          '$deletions']}}}}
    out = {'$out': 'result_additions_deletions_lines_commits_by_file_path'}
    pipeline = [unwind, projection, group, out]

    gitexplorer_database.commit_collection.aggregate(pipeline)


def main():
    _additions_deletions_lines_commits_by_file_path()


if(__name__ == '__main__'):
    main()
