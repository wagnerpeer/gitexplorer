'''
Created on 27.06.2017

@author: Peer
'''

import os
import pprint
import subprocess


def get_log_information(directory):

    os.chdir(directory)

    git_log_process = subprocess.Popen('git log --numstat --abbrev=40 --summary --reverse --pretty=format:"<gitexplorer>%H\t%aN\t%aE\t%at"',
                                       stdout=subprocess.PIPE)
    commits = git_log_process.communicate()[0]

    return commits


def main(directory):
    pprint.pprint(get_log_information(directory))


if(__name__ == '__main__'):
    directory = os.getcwd()

    main(directory)
