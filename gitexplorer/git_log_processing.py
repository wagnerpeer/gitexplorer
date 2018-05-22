"""
Created on 19.08.2017

@author: Peer
"""
import datetime
import logging
import os
import pathlib
import re
import subprocess

from .basics import GitExplorerBase as ge_base

PATH_RENAME = re.compile('^(?P<prefix>[^{]*){?(?P<old>.*) => (?P<new>[^}]*)}?(?P<suffix>.*)$')
PERMISSION_CHANGE = re.compile('(?P<old_permission>\d*) => (?P<new_permission>\d*)')


class GitLogAnalyzer(object):
    logging.basicConfig(format='[%(asctime)s] [%(levelname)8s] [%(name)s] :: %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    logger = logging.getLogger('gitexplorer')

    @classmethod
    def _process_details(cls, commit_hash, changes):

        details_dict = {'create': [],
                        'delete': [],
                        'rename': [],
                        'change': {},
                        'modifications': []}

        for line in changes:
            if line:
                line = line.strip(' \n')
                if line.startswith(('create', 'delete')):
                    action, _, permission, file_path = line.split(' ', maxsplit=3)
                    create_delete = {'permission': int(permission),
                                     'file_path': ge_base._mongodb_escape(file_path),
                                     'extension': pathlib.PurePath(file_path).suffix}
                    details_dict[action].append(create_delete)
                elif line.startswith('rename'):
                    action, paths_and_match = line.split(' ', maxsplit=1)
                    paths_combined, match = paths_and_match.rsplit(' ', maxsplit=1)

                    paths_match = PATH_RENAME.search(paths_combined)

                    if paths_match is None:
                        cls.logger.warning('Unparsable rename in commit {} detected: "{}"'.format(commit_hash, line))
                        continue

                    old_file_path = paths_match.group('prefix') + paths_match.group('old') + paths_match.group('suffix')
                    new_file_path = paths_match.group('prefix') + paths_match.group('new') + paths_match.group('suffix')

                    rename = {'new_path': ge_base._mongodb_escape(new_file_path),
                              'new_extension': pathlib.PurePath(new_file_path).suffix,
                              'old_path': ge_base._mongodb_escape(old_file_path),
                              'old_extension': pathlib.PurePath(old_file_path).suffix,
                              'match': int(match.strip('(%)'))}
                    details_dict['rename'].append(rename)
                elif line.startswith('mode change'):
                    _, action, permission_change_and_filename = line.split(' ', maxsplit=2)
                    permission_change, file_path = permission_change_and_filename.rsplit(' ', maxsplit=1)

                    permission_change_match = PERMISSION_CHANGE.search(permission_change)

                    if permission_change is None:
                        cls.logger.warning(
                            'Unparsable permission change in commit {} detected: "{}"'.format(commit_hash, line))
                        continue

                    old_permission = permission_change_match.group('old_permission')
                    new_permission = permission_change_match.group('new_permission')

                    change = {'old_permission': int(old_permission),
                              'new_permission': int(new_permission)}

                    details_dict['change'][ge_base._mongodb_escape(file_path)] = change
                elif line[0] in '1234567890-':
                    additions, deletions, file_path = line.split('\t', maxsplit=2)

                    if '=>' in file_path:
                        paths_match = PATH_RENAME.search(file_path)

                        if paths_match is None:
                            cls.logger.warning(
                                'Unparsable path_rename in commit {} detected: "{}"'.format(commit_hash, line))
                            continue

                        file_path = paths_match.group('prefix') + paths_match.group('new') + paths_match.group('suffix')

                    if additions == '-':
                        modifications = {'file_path': ge_base._mongodb_escape(file_path),
                                         'extension': pathlib.PurePath(file_path).suffix,
                                         'additions': None,
                                         'deletions': None}
                    else:
                        modifications = {'file_path': ge_base._mongodb_escape(file_path),
                                         'extension': pathlib.PurePath(file_path).suffix,
                                         'additions': int(additions),
                                         'deletions': int(deletions)}
                    details_dict['modifications'].append(modifications)

        return details_dict

    @classmethod
    def _process_commit(cls, commit):
        commit_dict = {}

        lines = commit.split('\n')

        if lines:
            commit_hash, author_name, author_mail, author_time, additional_information = lines[0].split('\t')

            if additional_information:
                cls.logger.warning('Unexpected additional information: "{}"'.format(additional_information))

            commit_dict['commit_hash'] = commit_hash
            commit_dict['author'] = author_name
            commit_dict['mail'] = author_mail
            commit_dict['date'] = datetime.datetime.utcfromtimestamp(float(author_time))

            if lines[1:]:
                commit_dict['details'] = cls._process_details(commit_hash, lines[1:])

        return commit_dict


class GitLogReader(object):
    output_schema = {
        'commit_hash': {
            'type': 'string',
            'pattern': '[a-fA-F0-9]{7,40}'},
        'author': {'type': 'string'},
        'mail': {'type': 'email'},
        'date': {'type': 'date-time'},
        'details': {
            'type': 'object',
            'properties': {
                'create': {'type': 'array',
                           'uniqueItems': True,
                           'items': {
                               'type': 'object',
                               'properties': {
                                   'file_path': {
                                       'type': 'string',
                                       'pattern': '^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))'},
                                   'permission': {
                                       'type': 'integer',
                                       'minimum': 0,
                                       'maximum': 134217727},
                                   'extension': {'type': 'string'}}}},
                'delete': {'type': 'array',
                           'uniqueItems': True,
                           'items': {
                               'type': 'object',
                               'properties': {
                                   'file_path': {
                                       'type': 'string',
                                       'pattern': '^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))'},
                                   'permission': {
                                       'type': 'integer',
                                       'minimum': 0,
                                       'maximum': 134217727}}}},
                'rename': {'type': 'array',
                           'uniqueItems': True,
                           'items': {
                               'type': 'object',
                               'properties': {
                                   'new_path': {
                                       'type': 'string',
                                       'pattern': '^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))'},
                                   'extension': {'type': 'string'},
                                   'old_path': {
                                       'type': 'string',
                                       'pattern': '^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))'},
                                   'match': {
                                       'type': 'integer',
                                       'minimum': 0,
                                       'maximum': 100}}}},
                'change': {
                    'type': 'object',
                    'patternProperties': {
                        '^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))': {
                            'type': 'object',
                            'properties': {
                                'old_permission': {
                                    'type': 'integer',
                                    'minimum': 0,
                                    'maximum': 134217727},
                                'new_permission': {
                                    'type': 'integer',
                                    'minimum': 0,
                                    'maximum': 134217727}}}}},
                'modifications': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'file_path': {
                                'type': 'string',
                                'pattern': '^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))'},
                            'additions': {'type': {
                                'enum': ['null', 'integer']}},
                            'deletions': {'type': {
                                'enum': ['null', 'integer']}}}}}}}}

    def __init__(self, directory, after='', before='HEAD', analyzer=GitLogAnalyzer):
        """
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
        """
        self.directory = directory
        self.after = after
        self.before = before
        self.analyzer = analyzer()

    def get_log_information(self):
        """Runs a "git log" command in the given directory and returns the parsed information.
        """

        os.chdir(self.directory)

        if self.after:
            self.after = ' --after={}'.format(self.after)

        if self.before:
            self.before = ' --before={}'.format(self.before)

        # git log --numstat --abbrev=40 --summary --find-renames --reverse --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at\t"
        commits = subprocess.check_output('git log'
                                          ' --numstat'
                                          ' --abbrev=40'
                                          ' --summary'
                                          ' --find-renames'
                                          ' --reverse'
                                          ' --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at\t"'
                                          + self.after
                                          + self.before,
                                          stderr=subprocess.STDOUT).decode("utf-8")

        commit_objects = []

        for commit in commits.split('<gitexplorer>'):
            if commit:
                commit_objects.append(self.analyzer._process_commit(commit))

        return commit_objects
