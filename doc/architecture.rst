Building the architecture which meets the requirements
======================================================

Where do we start? The first try of a design fulfilling some of the architectural requirements
could look like visualized in **Figure 1**. A script will read out the git information and
put it into a persistent storage. This storage will be read out from a script generating the
visualization with respect to some configuration options.

.. figure:: https://github.com/wagnerpeer/gitexplorer/blob/master/img/gitexplorer.png
    :alt: gitexplorer possible basic architecture.
    :width: 100%
    :align: center
    
    **Figure 1:** Basic architecture for gitexplorer.

However if we think about supporting the extensibility requirement, it is clear
that this architecture can be improved. 

.. figure:: https://github.com/wagnerpeer/gitexplorer/blob/master/img/gitexplorer_extension.png
    :alt: gitexplorer possible architecture designed for extensibility.
    :width: 100%
    :align: center
    
    **Figure 2:** Architecture for gitexplorer having extensibility as a basic design element.