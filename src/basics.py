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


def mongodb_escape(input_string):
    return input_string.translate(TRANSLATION_TABLE)


def process_details(changes):

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
                details_dict[action][mongodb_escape(file_path)] = create_delete
            elif(line.startswith('rename')):
                action, paths_and_match = line.split(' ', maxsplit=1)
                paths_combined, match = paths_and_match.rsplit(' ', maxsplit=1)

                paths_match = PATH_RENAME.search(paths_combined)
                old_file_path = paths_match.group('prefix') + paths_match.group('old') + paths_match.group('suffix')
                new_file_path = paths_match.group('prefix') + paths_match.group('new') + paths_match.group('suffix')

                rename = {'new_path': mongodb_escape(new_file_path),
                          'extension': pathlib.PurePath(new_file_path).suffix,
                          'old_path': mongodb_escape(old_file_path),
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

                details_dict['change'][mongodb_escape(file_path)] = change
            else:
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
                details_dict['modifications'][mongodb_escape(file_path)] = modifications

    return details_dict


def process_commit(commit):
    commit_dict = {}

    lines = commit.split('\n')

    if(lines):
        commit_hash, author_name, author_mail, author_time = lines[0].split('\t')

        commit_dict['commit_hash'] = commit_hash
        commit_dict['author'] = author_name
        commit_dict['mail'] = author_mail
        commit_dict['date'] = datetime.datetime.utcfromtimestamp(float(author_time))

        if(lines[1:]):
            commit_dict['details'] = process_details(lines[1:])

    return commit_dict


def get_log_information(directory):

    os.chdir(directory)

    commits = subprocess.check_output('git log --numstat --abbrev=40 --summary --reverse --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at"',
                                      stderr=subprocess.STDOUT).decode("utf-8")

    commit_objects = []

    for commit in commits.split('<gitexplorer>'):
        if(commit):
            commit_objects.append(process_commit(commit))

    return commit_objects


def main(directory):
#     pp(get_log_information(directory))
    client = pymongo.MongoClient()
    ge_database = client.gitexplorer_database
    commit_collection = ge_database.commit_collection
    commit_collection.insert_many(get_log_information(directory))


if(__name__ == '__main__'):
    directory = os.getcwd()

    main(directory)
