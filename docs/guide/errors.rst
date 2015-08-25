.. _guide_errors:

Error Codes
===========

Below is a list of all error codes used by the Toolkit, and a brief
description of what they mean.

The Toolkit uses a "low-noise" approach to error handling.  Only those errors
which absolutely must be caught and handled are assigned error codes.  In all
other cases, the Toolkit adopts reasonable behavior which is explicitly
specified in the documentation.

For example, imagine you call :ref:`vi_line` with X and Y arrays which are
not the same size.  Rather than generate an error, the Toolkit plots the
common portion of the arrays.

.. _error_init:

402900 - Failed to Initialize Plotting Library
----------------------------------------------

The Toolkit relies on a small bundled plotting library.
This error means that, for some reason, the library failed to start properly. 
The text portion of the error cluster will contain a detailed reason why.

Since this error is only possible when the first Toolkit VI is called, it is
good practice to check for it once, on app startup using :ref:`vi_init`,
rather than after each VI call.

**If you see this error, please contact us so we can investigate.**  It should
never be triggered in normal operation.

.. _error_plotting:

402901 - Error in Plotting Library
----------------------------------

While making the plot, an unspecified error occured and the
plot was not able to be completed.

**If you see this error, please contact us so we can investigate.**  It should
never be triggered in normal operation.

.. _error_invalid:

402902 - Invalid Plot Identifier
--------------------------------

The plot identifier wasn't recognized; for example, it has already been closed.
If you are unsure whether an identifier is valid, you can use
:ref:`vi_isvalid` to check.

.. _error_file_extension:

402903 - Unrecognized File Extension
------------------------------------

For :ref:`vi_save`, the desired format couldn't be determined based on the
file extension.  See :ref:`vi_save` docs for a list of supported formats.

.. _error_file_save:

402904 - Failed to Save File
----------------------------

For :ref:`vi_save`, the plot was rendered successfully but an error occurred
when saving the plot to disk.  See the error message for more information.
Typical causes include e.g. permissions issues.

.. _error_polar:

402905 - Operation Not Supported for Polar Plot
-----------------------------------------------

The plot was created with polar axes (:ref:`vi_new`), and an operation was
requested which doesn't make sense or is unimplemented for polar axes.
Consult the message in the error cluster for more details.  See also
:ref:`guide_polar`.

.. _error_scale:

402906 - Operation Not Supported for Axis Scale
-----------------------------------------------

The plot was created with log or symlog scales (:ref:`vi_new`), and an
operation was requested which doesn't make sense or is unimplemented for the
current scale type. Consult the message in the error cluster for more details.

.. _error_coordinates:

402907 - Coordinates Not Regular
--------------------------------

Certain VIs (e.g. :ref:`vi_streamline`) require that the X and Y coordinate
arrays, if provided, satisfy certain constraints.  For example, they might
be required to be equally spaced, or monotonically increasing.  Consult the
message in the error cluster for details.