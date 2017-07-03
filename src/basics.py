'''
Created on 27.06.2017

@author: Peer
'''

import datetime
import os
import pprint
import re
import subprocess


def process_details(changes):

    details_dict = {b'create': {},
                    b'delete': {},
                    b'rename': [],
                    b'change': {},
                    b'modifications': {}}

    for line in changes:
        if(line):
            line = line.strip(b' \n')
            pprint.pprint(line)

            if(line.startswith((b'create', b'delete'))):
                action, _, permission, filename = line.split(b' ', maxsplit=3)
                details_dict[action][filename] = {'permission': int(permission)}
            elif(line.startswith(b'rename')):
                action, paths_and_match = line.split(b' ', maxsplit=1)
                paths_combined, match = paths_and_match.rsplit(b' ', maxsplit=1)

                paths_match = re.search(b'(?P<prefix>.*){?(?P<old>.*) => (?P<new>.*)}?(?P<suffix>.*)', paths_combined)
                old_path = paths_match.group('prefix') + paths_match.group('old') + paths_match.group('suffix')
                new_path = paths_match.group('prefix') + paths_match.group('new') + paths_match.group('suffix')

                rename = {b'new_path': new_path,
                          b'old_path': old_path,
                          b'match': int(match.strip(b'(%)'))}
                details_dict[b'rename'].append(rename)
            elif(line.startswith(b'mode change')):
                _, action, permission_change_and_filename = line.split(b' ', maxsplit=2)
                permission_change, filename = permission_change_and_filename.rsplit(b' ', maxsplit=1)

                permission_change_match = re.search(b'(?P<old_permission>\d*) => (?P<new_permission>\d*)', permission_change)
                old_permission = permission_change_match.group('old_permission')
                new_permission = permission_change_match.group('new_permission')

                change = {b'old_permission': int(old_permission),
                          b'new_permission': int(new_permission)}

                details_dict[b'change'][filename] = change
            else:
                additions, deletions, filename = line.split(b'\t', maxsplit=2)

                if(additions == b'-'):
                    modifications = {b'additions': None,
                                     b'deletions': None}
                else:
                    modifications = {b'additions': int(additions),
                                     b'deletions': int(deletions)}
                details_dict[b'modifications'][filename] = modifications

    return details_dict


def process_commit(commit):
    commit_dict = {}

    lines = commit.split(b'\n')

    if(lines):
        pprint.pprint(lines[0])
        commit_hash, author_name, author_mail, author_time = lines[0].split(b'\t')

        commit_dict['commit_hash'] = commit_hash
        commit_dict['author'] = author_name
        commit_dict['mail'] = author_mail
        commit_dict['date'] = datetime.datetime.utcfromtimestamp(float(author_time))

        if(lines[1:]):
            commit_dict['details'] = process_details(lines[1:])

    return commit_dict


def get_log_information(directory):

    os.chdir(directory)

    git_log_process = subprocess.Popen('git log --numstat --abbrev=40 --summary --reverse --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at"',
                                       stdout=subprocess.PIPE)
    commits = git_log_process.communicate()[0]

    commit_objects = []

    for commit in commits.split(b'<gitexplorer>'):
        print()
        if(commit):
            commit_objects.append(process_commit(commit))

    return commit_objects


def main(directory):
    pprint.pprint(get_log_information(directory))


if(__name__ == '__main__'):
    directory = os.getcwd()

    main(directory)
