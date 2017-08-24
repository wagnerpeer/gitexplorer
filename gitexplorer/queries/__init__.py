'''
Created on 21.08.2017

@author: Peer Wagner
'''

import importlib
import pathlib
import os
import warnings


def find_all():
    dynamically_imported_modules = []

    file_path = pathlib.PurePath(__file__)

    for name in os.listdir(file_path.parent.as_posix()):
        if name not in ['__init__', 'aggregation.py']:
            name = os.path.splitext(name)[0]
            try:
                module = importlib.import_module('.'.join(list(file_path.parts[-3:-1]) + [name]))
                dynamically_imported_modules.append(module)
            except ImportError as ie:
                warnings.warn('Failed to load module: {}'.format(name))
    del name, module

    return dynamically_imported_modules
