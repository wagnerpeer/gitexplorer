'''
Created on 15.08.2017

@author: Peer Wagner
'''

from .. import basics


class AggregatorRegistry(type):

    aggregator_classes = []

    def __init__(cls, name, _bases, _attributes):
        if name != 'AbstractAggregator':
            AggregatorRegistry.aggregator_classes.append(cls)


class AbstractAggregator(basics.GitExplorerBase, metaclass=AggregatorRegistry):

    @property
    def name(self):
        raise NotImplementedError()

    def provides(self) -> str:
        raise NotImplementedError()

    def requires(self) -> str:
        raise NotImplementedError()

    def run(self):
        gitexplorer_database = self.get_gitexplorer_database()
        gitexplorer_database[self.output_database].drop()
        gitexplorer_database[self.input_database].aggregate(self.pipeline)
