.. include:: /defs.txt
.. |circle_props| image:: ShapeProps.png

.. _vi_circle:

Draw Circle
===========

Draw a circle, in data coordinates.

Places a circle on the plot, by specifying the X and Y location of the circle
center, along with the radius.  Note that since the circle is in
*data coordinates*, it may look "squashed" unless the aspect ratio of the
plot is 1.0 (see :ref:`vi_new`).

.. image:: Circle.png

.. include:: /stdid.txt
    
|double_in| **X Position**
    X position of the circle center.
    
|double_in| **Y Position**
    Y position of the circle center.

|double_in| **Radius**
    Circle radius.
    
|circle_props| **Properties**
    Property cluster, available under the "Properties" subpalette.

    |uint32_in| **Color**
        Fill color for the circle.  Defaults to light-grey.
    
    |cluster_in| **Line**
        Controls the appearance of the circle edge.
        
        .. include:: /stdline.txt
        
    |cluster_in| **Display**
        Controls general appearance of the circle.
        
        .. include:: /stddisplay.txt
        
.. include:: /stderr.txt

Axis Types
----------

This VI supports rectangular axes.  Use with :ref:`polar axes <guide_polar>`
will result in :ref:`error_polar`.  Likewise, only linear scales are supported.
Use with log or symlog axes will result in :ref:`error_scale`.

Errors
------

* :ref:`error_scale`
* :ref:`error_polar`
* :ref:`error_invalid`
* :ref:`error_plotting`
* :ref:`error_init`


Other information
-----------------

If **X Position** or **Y Position** is non-finite, or if **Radius** is
non-finite, zero, or negative, no circle is displayed and no error is returned.
