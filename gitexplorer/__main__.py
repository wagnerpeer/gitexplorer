'''
Created on 24.08.2017

@author: Peer
'''

import argparse

import matplotlib.pyplot as plt
import networkx as nx

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

    queries.AggregatorRegistry.load('gitexplorer.queries.authors_per_file',
                                    'gitexplorer.queries.commits_by_datetime',
                                    'gitexplorer.queries.commits_by_filestats',
                                    'gitexplorer.queries.commits_per_author',
                                    'gitexplorer.queries.queries_per_commit')

    aggregations = list(map(queries.AggregatorRegistry.get,
                            ['authors_per_file_path',
                             'commits_by_day_of_week',
                             'commits_by_hour_of_day',
                             'additions_deletions_lines_commits_by_file_path',
                             'commits_per_author',
                             'additions_deletions_lines_modifications_per_commit',
                             'average_additions_deletions_lines_modifications_per_commit',
                             'additions_deletions_lines_modifications_commits_by_date',
                             'average_additions_deletions_lines_modifications_commits_by_date',
                             ]))
    dependencies = nx.DiGraph()

    for aggregation in aggregations:
        provides = aggregation.provides()
        dependencies.add_edge(provides, aggregation.requires())

    sorted_dependencies = nx.topological_sort(dependencies, reverse=True)

    print(sorted_dependencies)

    for dependency in sorted_dependencies:
        for aggregation in aggregations:
            if(aggregation.name == dependency):
                aggregation().run()

    nx.draw(dependencies, with_labels=True)

    plt.show()


if(__name__ == '__main__'):

    args = _get_arguments()

    main(args.directory)
