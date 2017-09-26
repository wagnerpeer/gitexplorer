'''
Created on 06.07.2017

@author: Peer
'''

from . import aggregation


class AdditionsDeletionsLinesModificationsPerCommit(aggregation.AbstractAggregator):

    name = 'additions_deletions_lines_modifications_per_commit'

    @classmethod
    def provides(cls):
        return 'additions_deletions_lines_modifications_per_commit'

    @classmethod
    def requires(cls):
        return 'commit_collection'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = self.requires()

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
                            'total_lines': {'$sum': {'$add': ['$modifications.additions',
                                                              '$modifications.deletions']}}}}

        out = {'$out': self.output_database}

        self.pipeline = [unwind, projection, group, out]


class AverageAdditionsDeletionsLinesModificationsPerCommit(aggregation.AbstractAggregator):

    name = 'average_additions_deletions_lines_modifications_per_commit'

    @classmethod
    def provides(cls):
        return 'average_additions_deletions_lines_modifications_per_commit'

    @classmethod
    def requires(cls):
        return 'additions_deletions_lines_modifications_per_commit'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = 'result_' + self.requires()

        group = {'$group': {'_id': None,
                            'average_additions': {'$avg': '$total_additions'},
                            'average_deletions': {'$avg': '$total_deletions'},
                            'average_modifications': {'$avg': '$total_modifications'},
                            'average_lines': {'$avg': '$total_lines'}}}

        out = {'$out': self.output_database}

        self.pipeline = [group, out]


class AdditionsDeletionsLinesModificationsCommitsByDate(aggregation.AbstractAggregator):

    name = 'additions_deletions_lines_modifications_commits_by_date'

    @classmethod
    def provides(cls):
        return 'additions_deletions_lines_modifications_commits_by_date'

    @classmethod
    def requires(cls):
        return 'additions_deletions_lines_modifications_per_commit'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = 'result_' + self.requires()

        group = {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d',
                                                      'date': '$date'}},
                            'date': {'$first': '$date'},
                            'total_additions': {'$sum': '$total_additions'},
                            'total_deletions': {'$sum': '$total_deletions'},
                            'total_commits': {'$sum': 1},
                            'commits': {'$push': '$commit_hash'},
                            'total_modifications': {'$sum': '$total_modifications'}}}

        out = {'$out': self.output_database}

        self.pipeline = [group, out]


class AverageAdditionsDeletionsLinesModificationsCommitsByDate(aggregation.AbstractAggregator):

    name = 'average_additions_deletions_lines_modifications_commits_by_date'

    @classmethod
    def provides(cls):
        return 'average_additions_deletions_lines_modifications_commits_by_date'

    @classmethod
    def requires(cls):
        return 'additions_deletions_lines_modifications_commits_by_date'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = 'result_' + self.requires()

        projection = {'$project': {'_id': '$_id',
                                   'date': '$date',
                                   'average_additions': {'$divide': ['$total_additions',
                                                                     '$total_commits']},
                                   'average_deletions': {'$divide': ['$total_deletions',
                                                                     '$total_commits']},
                                   'average_lines': {'$divide': [{'$add': ['$total_additions',
                                                                           '$total_deletions']},
                                                                 '$total_commits']},
                                   'average_modifications': {'$divide': ['$total_modifications',
                                                                         '$total_commits']}}}

        out = {'$out': self.output_database}

        self.pipeline = [projection, out]


def main():
    AdditionsDeletionsLinesModificationsPerCommit().run()
    AverageAdditionsDeletionsLinesModificationsPerCommit().run()
    AdditionsDeletionsLinesModificationsCommitsByDate().run()
    AverageAdditionsDeletionsLinesModificationsCommitsByDate().run()


if(__name__ == '__main__'):
    main()
