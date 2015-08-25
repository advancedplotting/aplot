.. include:: /defs.txt
.. |hvline_props| image:: HVLineProps.png

.. _vi_vline:

Draw Vertical Line
==================

Draw a vertical line across the axis box, at a particular X location.

The starting and ending locations of the line may optionally be specified, in
units of the axis height (0.0 to 1.0).

.. image:: VLine.png

.. include:: /stdid.txt
    
|double_in| **X (data coords)**
    X location at which to draw the vertical line, in data coordinates.
    
|double_in| **Y Min (plot coords)**
    Start location of line, as a fraction of the plot height (0 to 1).  Default
    is to start at the bottom axis (0).

|double_in| **Y Max (plot coords)**
    End location of line, as a fraction of the plot height (0 to 1).  Default
    is to end at the top axis (1).
    
|hvline_props| **Properties**
    Property cluster, available under the "Properties" subpalette.
    
    |cluster_in| **Line**
        Controls the appearance of the line.
        
        .. include:: /stdline.txt
    
    |cluster_in| **Display**
        Controls display appearance of the line.
        
        .. include:: /stddisplay.txt
        
.. include:: /stderr.txt

.. include:: /stdpolar.txt

Errors
------

.. include:: /common_errors.txt

Other information
-----------------

If **X** is non-finite (NaN or Inf), the line will not be displayed, and no
error will be returned.

If **Y Min** or **Y Max** is non-finite or extend beyond the limits of the
axes, the default location will be used.  **Y Max** may be smaller than
**Y Min**; the line will be plotted normally.
