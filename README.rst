gitexplorer
===========

This project is intended to be a tool to extract basic information from any accessible git repository, make appealing visualizations like the GitHub graphs and therefore make exploration of repositories as easy as possible.

Being a fairly new project neither all requirements are written nor are implementation details already clear. I will take the chance and document the process of architecture and design decisions. As an inspiration for the project I base on the great repositories `hoxu/gitstats`_ and `adamtornhill/code-maat`_.

In the future the starting point for all interaction with the package gitexplorer will start with:

.. code-block:: python

    import gitexplorer as ge

So stay tuned ...

.. _`hoxu/gitstats`: https://github.com/hoxu/gitstats
.. _`adamtornhill/code-maat`: https://github.com/adamtornhill/code-maat