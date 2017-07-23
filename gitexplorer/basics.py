'''
Created on 27.06.2017

@author: Peer
'''

import argparse
import datetime
import os
import pathlib
from pprint import pprint as pp
import re
import subprocess

import pymongo

PATH_RENAME = re.compile('^(?P<prefix>[^{]*){?(?P<old>.*) => (?P<new>[^}]*)}?(?P<suffix>.*)$')
TRANSLATION_TABLE = str.maketrans({'.': '\uff0e',
                                   '$': '\uff04'})
INVERSE_TRANSLATION_TABLE = str.maketrans({'\uff0e': '.',
                                           '\uff04': '$'})


def _mongodb_escape(input_string):
    return input_string.translate(TRANSLATION_TABLE)


def _mongodb_unescape(input_string):
    return input_string.translate(INVERSE_TRANSLATION_TABLE)


def _process_details(changes):

    details_dict = {'create': [],
                    'delete': [],
                    'rename': [],
                    'change': {},
                    'modifications': []}

    for line in changes:
        if(line):
            line = line.strip(' \n')
            if(line.startswith(('create', 'delete'))):
                action, _, permission, file_path = line.split(' ', maxsplit=3)
                create_delete = {'permission': int(permission),
                                 'file_path': _mongodb_escape(file_path)}
                if(action == 'create'):
                    create_delete['extension'] = pathlib.PurePath(file_path).suffix
                details_dict[action].append(create_delete)
            elif(line.startswith('rename')):
                action, paths_and_match = line.split(' ', maxsplit=1)
                paths_combined, match = paths_and_match.rsplit(' ', maxsplit=1)

                paths_match = PATH_RENAME.search(paths_combined)
                old_file_path = paths_match.group('prefix') + paths_match.group('old') + paths_match.group('suffix')
                new_file_path = paths_match.group('prefix') + paths_match.group('new') + paths_match.group('suffix')

                rename = {'new_path': _mongodb_escape(new_file_path),
                          'extension': pathlib.PurePath(new_file_path).suffix,
                          'old_path': _mongodb_escape(old_file_path),
                          'match': int(match.strip('(%)'))}
                details_dict['rename'].append(rename)
            elif(line.startswith('mode change')):
                _, action, permission_change_and_filename = line.split(' ', maxsplit=2)
                permission_change, file_path = permission_change_and_filename.rsplit(' ', maxsplit=1)

                permission_change_match = re.search('(?P<old_permission>\d*) => (?P<new_permission>\d*)', permission_change)
                old_permission = permission_change_match.group('old_permission')
                new_permission = permission_change_match.group('new_permission')

                change = {'old_permission': int(old_permission),
                          'new_permission': int(new_permission)}

                details_dict['change'][_mongodb_escape(file_path)] = change
            elif(line[0] in '1234567890-'):
                additions, deletions, file_path = line.split('\t', maxsplit=2)

                if('=>' in file_path):
                    paths_match = PATH_RENAME.search(file_path)
                    file_path = paths_match.group('prefix') + paths_match.group('new') + paths_match.group('suffix')

                if(additions == '-'):
                    modifications = {'additions': None,
                                     'deletions': None}
                else:
                    modifications = {'file_path': _mongodb_escape(file_path),
                                     'additions': int(additions),
                                     'deletions': int(deletions)}
                details_dict['modifications'].append(modifications)

    return details_dict


def _process_commit(commit):
    commit_dict = {}

    lines = commit.split('\n')

    if(lines):
        commit_hash, author_name, author_mail, author_time = lines[0].split('\t')

        commit_dict['commit_hash'] = commit_hash
        commit_dict['author'] = author_name
        commit_dict['mail'] = author_mail
        commit_dict['date'] = datetime.datetime.utcfromtimestamp(float(author_time))

        if(lines[1:]):
            commit_dict['details'] = _process_details(lines[1:])

    return commit_dict


def get_log_information(directory, after='', before='HEAD'):
    '''Runs a "git log" command in the given directory and returns the parsed information.

    Parameters
    ----------
    directory : str
        Path to git repository
    after : str, optional
        Valid git date format
    before : str, optional
        Valid git date format

    Returns
    -------
    commit_objects : list

    Notes
    -----
    For a detailed description of the return format please refer to the documentation of gitexplorer.
    '''
    os.chdir(directory)

    if(after):
        after = ' --after={after}'.format(**locals())

    if(before):
        before = ' --before={before}'.format(**locals())

    commits = subprocess.check_output('git log --all --numstat --abbrev=40 --summary --reverse --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at"' + after + before,
                                      stderr=subprocess.STDOUT).decode("utf-8")

    commit_objects = []

    for commit in commits.split('<gitexplorer>'):
        if(commit):
            commit_objects.append(_process_commit(commit))

    return commit_objects


def get_gitexplorer_database():
    '''Returns the MongoDB for gitexplorer.

    The collections inside the database can be used as basis for specialized collections
    from which one can derive elevated statistics. Results can also be written into the
    database to be accessible by visualization routines.
    '''
    client = pymongo.MongoClient()
    return client.gitexplorer_database


def main(directory):
    gitexplorer_database = get_gitexplorer_database()
    gitexplorer_database.commit_collection.drop()
    gitexplorer_database.commit_collection.insert_many(get_log_information(directory))


if(__name__ == '__main__'):
    directory = os.getcwd()
    directory = r'C:\Users\Peer\workspace\Pydev'

    main(directory)
