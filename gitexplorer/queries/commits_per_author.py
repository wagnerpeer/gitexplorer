'''
Created on 06.07.2017

@author: Peer
'''

from . import aggregation


class CommitsPerAuthor(aggregation.AbstractAggregator):

    @classmethod
    def provides(cls):
        return 'commits_per_author'

    @classmethod
    def requires(cls):
        return 'commit_collection'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = self.requires()

        projection = {'$project': {'author': '$author',
                                   'commit_hash': '$commit_hash'}}

        group = {'$group': {'_id': '$author',
                            'total_commits': {'$sum': 1},
                            'commits': {'$push': '$commit_hash'}}}

        out = {'$out': self.output_database}

        self.pipeline = [projection, group, out]


def main():
    CommitsPerAuthor().run()


if(__name__ == '__main__'):
    main()
