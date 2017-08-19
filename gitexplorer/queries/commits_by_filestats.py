'''
Created on 05.07.2017

@author: Peer
'''

from . import aggregation


class AdditionsDeletionsLinesCommitsByFilePath(aggregation.AbstractAggregator):

    @classmethod
    def provides(cls):
        return 'additions_deletions_lines_commits_by_file_path'

    @classmethod
    def requires(cls):
        return 'commit_collection'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = self.requires()

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

        out = {'$out': self.output_database}

        self.pipeline = [unwind, projection, group, out]


def main():
    AdditionsDeletionsLinesCommitsByFilePath().run()


if(__name__ == '__main__'):
    main()
