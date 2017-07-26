The story behind gitexplorer or the What, Why and for Whom!
===========================================================
As a computer scientist working with many different kinds of software and in various teams, I was always curious on how
to improve my work and the software I am working with. Almost naturally, as it comes to bigger applications and bigger
teams, me and my team always used a version control system. Therefore I was always interested in how to use those
systems to get information about the past; sometimes by reverting bugs some of us introduced, to retrace ideas or to
get an overview on what is going on with our source code, not to say who is doing what and where are those changes
located.

Reading a lot about refactoring (especially [Torn15]_), I have an emerging interest in analyzing my repositories
in a more structured way. Hopefully this will enable me to refactor the code which needs it most to simplify my daily
work.

Being a Python programmer I searched the internet for a Python application fullfilling my wish for a way to analyze
git repositories to get the information I was looking for. As I formerly worked with SVN and remembered the tool
`StatSVN`_ which generated a lot of statistics about a repository, I immediately found `GitStats`_. To my displeasure it
had a strong coupling to gnuplot and after contacting the maintainer it was clear that the project was no longer under
active development despite lots of pull requests to improve it. A look at the source code and a few modifications later
I decided to start a project on my own. An application capable to generate all the statistics I wish for, combined with
an appealing output.

Requirements
------------
I formulated the following few non specific requirements for myself:

1. An application which can be used to analyze and visualize arbitrary git repositories. The data and visualization artifacts can then be used to get a deeper insight into usage and content of the analyzed repository.
2. The result of the analysis shall be persisted to be efficiently accessible for visualization and reevaluation as well as future extension.
3. Extending the application shall be possible by writing additional visualizations and/or additional data analysis which can result in extra information to be stored in conformity to #2.
4. The style of visualizations shall be easily changeable by programmers and non programmers to support separation of concerns.
5. The analysis of the repository shall be as effective as possible whereas the resulting information storage shall be partially updatable and upgradable.

Achivements & Goals
-------------------
This documentation should be an up to date source of information which statistics are already available in the basic
package and which are soon likely to be available.

Done
^^^^
1. Total number of additions, deletions, lines and modifications per commit
2. Total number of additions, deletions, lines and modifications per commit, grouped by date
3. Number of commits grouped by iso day of the week
4. Number of commits grouped by hour of day
5. Authors and corresponding date of commits, additions, deletions and lines grouped by file path
6. Additions, deletions, lines and commits grouped by file path
7. Average number of additions, deletions, lines and modifications per commit
8. Average number of additions, deletions, lines and modifications grouped by date

To Be Done
^^^^^^^^^^
1. List of file extensions
2. Total number of additions, deletions, lines and modifications per author
3. Average number of additions, deletions, lines and modifications per commit, grouped by author
4. Every other statistic limited to the last 30 days
5. Every other statistic limited to the last half year
6. Every other statistic limited to the last year
7. Total number of commits per file path
8. Author of the month rated by 'TBD'
9. Author of the year rated by 'TBD'
10. Every statistic respecting renames
11. Total number of additions, deletions, lines and modifications per extension
12. Size per file
13. Update frequency per file
14. Coupling of files
15. Python specific file statistics like cyclomatic complexity
16. Visualization of all statistics


.. [Torn15] `Tornhill, A. (2015). Your code as a Crime Scene - Use Forensic Techniques to Arrest Defects, Bottlenecks and Bad Design in Your Programs. Dallas, TX: The Pragmatic Bookshelf <https://books.google.de/books?id=vFjRrQEACAAJ>`_

.. _`StatSVN` : http://statsvn.org/
.. _`GitStats` : http://gitstats.sourceforge.net/