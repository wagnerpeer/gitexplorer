.. gitexplorer documentation master file, created by
   sphinx-quickstart on Sun Jul 23 12:28:17 2017.

Welcome to gitexplorer's documentation!
=======================================

.. image:: img/gitexplorer_logo.svg
    :width: 300 px
    :alt: gitexplorer logo
    :align: center

This project is intended to be a tool to extract basic information from any accessible git repository, make appealing
visualizations like the GitHub graphs and therefore make exploration of repositories as easy as possible.

Being a fairly new project neither all requirements are written nor are implementation details already clear. I will
take the chance and document the process of architecture and design decisions. As an inspiration for the project I base
on the great repositories `hoxu/gitstats`_ and `adamtornhill/code-maat`_.

In the future the starting point for all interaction with the package gitexplorer will start with:

.. code-block:: python

    import gitexplorer as ge

So stay tuned ...

.. _`hoxu/gitstats`: https://github.com/hoxu/gitstats
.. _`adamtornhill/code-maat`: https://github.com/adamtornhill/code-maat

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    The Story <story>
    Architecture <architecture>
    License <license>
    Authors <authors>
    Changelog <changes>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
