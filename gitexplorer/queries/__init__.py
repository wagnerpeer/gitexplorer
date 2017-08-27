'''
Created on 21.08.2017

@author: Peer Wagner
'''

import importlib
import pathlib
import os
import warnings

from .aggregation import AggregatorRegistry


def discover_queries():
    file_path = pathlib.PurePath(__file__)

    for name in os.listdir(file_path.parent.as_posix()):
        if name not in ['__init__', 'aggregation.py']:
            name = os.path.splitext(name)[0]
            try:
                module = importlib.import_module('.'.join(list(file_path.parts[-3:-1]) + [name]))
            except ImportError as ie:
                warnings.warn('Failed to load module: {}'.format(name))
    del name, module

    return AggregatorRegistry.aggregator_classes
