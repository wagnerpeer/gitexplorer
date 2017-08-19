'''
Created on 15.08.2017

@author: Peer Wagner
'''

from .. import basics


class AbstractAggregator(basics.GitExplorerBase):

    def provides(self) -> str:
        raise NotImplementedError()

    def requires(self) -> str:
        raise NotImplementedError()

    def run(self):
        gitexplorer_database = self.get_gitexplorer_database()
        gitexplorer_database[self.output_database].drop()
        gitexplorer_database[self.input_database].aggregate(self.pipeline)
