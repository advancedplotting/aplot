.. _guide_polar:

Making Polar Plots
==================

Unlike other plotting libraries, there is no special "polar" version of
VIs like :ref:`vi_line` or :ref:`vi_scatter`.  Rather, when you create a new
plot using :ref:`vi_new`, you can specify whether to use rectangular (default)
axes, or polar axes.  Then use the ordinary 1D plotting VIs to populate the
plot.

.. only:: html

    Example
    -------

    Download :download:`Polar Plots.vi </examples/Polar Plots.vi>`,
    or see :ref:`guide_examples` for a complete list of examples.
    
    .. image:: PolarExample.png
    
Radians or Degrees?
-------------------

Radians.

The 1D plotting VIs which can be used with polar plots (:ref:`vi_line`, 
:ref:`vi_scatter`, and :ref:`vi_bar`) all take two input arrays: X and Y.
On a rectangular plot, the X array gives the location of points along the
horizontal axis, and the Y array gives the location of points along the
vertical axis.

When plotting to polar axes, the X array gives the *angular* locations of
points, in *radians*.  The Y array gives the locations of the points in the
radial direction.

This is also the case for all other VIs which interact with the plot; for
example, when placing text on the plot using :ref:`vi_text`, the X position
is interpreted as an angle, in radians.

The zero angle is on the right horizontal axis, as is common in mathematics and
the physical sciences.  Negative angle values are fully supported, as are
values greater than 2 :math:`\pi`.


Gotchas
-------

The X input for :ref:`vi_line` and friends is optional; if N data points are
provided to the Y input, it defaults to 0..N-1.  This may have unexpected
effects on a polar plot; the points will appear at 0, 1, 2, etc., *radians*,
which is probably not what you want.  To avoid this, always specify X and Y
explicitly when using polar plots.

Although points are placed in *radians*, the default human-readable tick
labels are given in *degrees* (0, 90, 180, 270).  You can re-label these, 
if desired, using :ref:`vi_xticks`.  Check out :ref:`guide_latex` if you
want to use the :math:`\pi` symbol for this!


VIs Supporting Polar Plots
--------------------------

Not all VIs can cope with the polar coordinate system.  At present, the 1D
plotting routines work well, along with VIs for annotation, like
:ref:`vi_legend`.

Here's a list of the VIs which support polar axes.  Calling other VIs with a
polar plot will result in error :ref:`error_polar`.

Core VIs
~~~~~~~~

* :ref:`vi_new`
* :ref:`vi_close`
* :ref:`vi_save`
* :ref:`vi_view`

Plotting
~~~~~~~~

* :ref:`vi_bar`
* :ref:`vi_line`
* :ref:`vi_scatter`

Annotation
~~~~~~~~~~

* :ref:`vi_colorbar`
* :ref:`vi_legend`
* :ref:`vi_text`
* :ref:`vi_title`
* :ref:`vi_xlabel`
* :ref:`vi_ylabel`
* :ref:`vi_xticks`
* :ref:`vi_yticks`

Plot Config and Setup
~~~~~~~~~~~~~~~~~~~~~

* :ref:`vi_grids`
* :ref:`vi_limits` (Y limits only)
* :ref:`vi_size`
