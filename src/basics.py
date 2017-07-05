'''
Created on 27.06.2017

@author: Peer
'''

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


def _mongodb_escape(input_string):
    return input_string.translate(TRANSLATION_TABLE)


def _process_details(changes):

    details_dict = {'create': {},
                    'delete': {},
                    'rename': [],
                    'change': {},
                    'modifications': {}}

    for line in changes:
        if(line):
            line = line.strip(' \n')
            if(line.startswith(('create', 'delete'))):
                action, _, permission, file_path = line.split(' ', maxsplit=3)
                create_delete = {'permission': int(permission)}
                if(action == 'create'):
                    create_delete['extension'] = pathlib.PurePath(file_path).suffix
                details_dict[action][_mongodb_escape(file_path)] = create_delete
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
                    modifications = {'additions': int(additions),
                                     'deletions': int(deletions)}
                details_dict['modifications'][_mongodb_escape(file_path)] = modifications

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

    commits = subprocess.check_output('git log --numstat --abbrev=40 --summary --reverse --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at"' + after + before,
                                      stderr=subprocess.STDOUT).decode("utf-8")

    commit_objects = []

    for commit in commits.split('<gitexplorer>'):
        if(commit):
            commit_objects.append(_process_commit(commit))

    return commit_objects


def get_basic_collection():
    '''Returns the MongoDB collection to derive most statistics from.

    The collection can be used as basis for specialized collections from which one can derive elevated statistics.
    '''
    client = pymongo.MongoClient()
    ge_database = client.gitexplorer_database
    return ge_database.commit_collection


def main(directory):
    commit_collection = get_basic_collection()
    commit_collection.insert_many(get_log_information(directory))


if(__name__ == '__main__'):
    directory = os.getcwd()

    main(directory)
