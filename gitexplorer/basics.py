'''
Created on 27.06.2017

@author: Peer
'''

import argparse
from bson.code import Code
import os
import pathlib

import pymongo
from git_log_processing import GitLogReader

TRANSLATION_TABLE = str.maketrans({'.': '\uff0e',
                                   '$': '\uff04'})
INVERSE_TRANSLATION_TABLE = str.maketrans({'\uff0e': '.',
                                           '\uff04': '$'})


class GitExplorerBase(object):

    @staticmethod
    def get_gitexplorer_database():
        '''Returns the MongoDB for gitexplorer.

        The collections inside the database can be used as basis for specialized collections
        from which one can derive elevated statistics. Results can also be written into the
        database to be accessible by visualization routines.
        '''
        client = pymongo.MongoClient()
        return client.gitexplorer_database

    @staticmethod
    def _mongodb_escape(input_string):
        return input_string.translate(TRANSLATION_TABLE)

    @staticmethod
    def _mongodb_unescape(input_string):
        return input_string.translate(INVERSE_TRANSLATION_TABLE)

    @staticmethod
    def _get_code(file_name):
        current_working_directory = pathlib.Path(os.getcwd())

        with (current_working_directory / file_name).open(mode='r') as fid:
            code = fid.read()

        return Code(code)


def main(directory):
    log = GitLogReader.get_log_information(directory)

    gitexplorer_database = GitExplorerBase.get_gitexplorer_database()
    gitexplorer_database.commit_collection.drop()
    gitexplorer_database.commit_collection.insert_many(log)


def _get_arguments():
    parser = argparse.ArgumentParser(description='Parse configuration parameters for gitexplorer from command line arguments.')
    parser.add_argument('directory',
                        metavar='DIR',
                        type=str,
                        help='The repository to run gitexplorer in.')

    return parser.parse_args()


if(__name__ == '__main__'):

    args = _get_arguments()

    main(args.directory)
