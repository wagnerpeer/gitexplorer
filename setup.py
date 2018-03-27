'''
Created on 24.08.2017

@author: Peer
'''

from setuptools import setup

setup(name='gitexplorer',
      version='0.1',
      description='Git repository analyzer',
      author='Peer Wagner',
      author_email='wagnerpeer@gmail.com',
      url='http://gitexplorer.readthedocs.io',
      packages=['gitexplorer'],
      requires=['matplotlib', 'networkx', 'pandas', 'pymongo'],
      provides=['gitexplorer'],
      download_url='https://github.com/wagnerpeer/gitexplorer',
      license='MIT',
      exclude_package_data={'gitexplorer': ['__main__.py']},
      )
