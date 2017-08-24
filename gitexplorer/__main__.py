'''
Created on 24.08.2017

@author: Peer
'''

import argparse

from gitexplorer import queries, git_log_processing
from gitexplorer.basics import GitExplorerBase


def _get_arguments():
    parser = argparse.ArgumentParser(description='Parse configuration parameters for gitexplorer from command line arguments.')
    parser.add_argument('directory',
                        metavar='DIR',
                        type=str,
                        help='The repository to run gitexplorer in.')

    return parser.parse_args()


def main(directory):

    log_reader = git_log_processing.GitLogReader(directory)

    log = log_reader.get_log_information()

    gitexplorer_database = GitExplorerBase.get_gitexplorer_database()
    gitexplorer_database.commit_collection.drop()
    gitexplorer_database.commit_collection.insert_many(log)


if(__name__ == '__main__'):

    args = _get_arguments()

    main(args.directory)
