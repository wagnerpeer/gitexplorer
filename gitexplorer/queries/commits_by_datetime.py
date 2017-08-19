'''
Created on 05.07.2017

@author: Peer
'''

from . import aggregation


class CommitsByDayOfWeek(aggregation.AbstractAggregator):

    @classmethod
    def provides(cls):
        return 'commits_by_day_of_week'

    @classmethod
    def requires(cls):
        return 'commit_collection'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = self.requires()

        projection = {'$project': {'day_of_week': {'$isoDayOfWeek': '$date'}}}

        group = {'$group': {'_id': '$day_of_week',
                            'total_commits': {'$sum': 1}}}

        out = {'$out': self.output_database}

        self.pipeline = [projection, group, out]


class CommitsByHourOfDay(aggregation.AbstractAggregator):

    @classmethod
    def provides(cls):
        return 'commits_by_hour_of_day'

    @classmethod
    def requires(cls):
        return 'commit_collection'

    def __init__(self):

        self.output_database = 'result_' + self.provides()
        self.input_database = self.requires()

        projection = {'$project': {'hour_of_day': {'$hour': '$date'}}}

        group = {'$group': {'_id': '$hour_of_day',
                            'total_commits': {'$sum': 1}}}

        out = {'$out': 'result_commits_by_hour_of_day'}

        self.pipeline = [projection, group, out]


def main():
    CommitsByDayOfWeek().run()
    CommitsByHourOfDay().run()


if(__name__ == '__main__'):
    main()
