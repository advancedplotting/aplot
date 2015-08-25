.. _guide_embedding:

Embedding the Toolkit in Your Application
=========================================

Using Toolkit VIs in your own LabVIEW application is very straightforward.
In this discussion, we will call the computer on which your app is written
the *development* environment, and the one on which it is intended to be used
the *target* environment.

.. note::

    Please be sure to read your License Agreement before distributing code that
    uses the Toolkit.  In the event of a conflict between the License Agreement
    and the documentation, the License Agreement is authoritative.
    
    You can read the License Agreement, and an overview of the licensing
    rules and responsibilities, here: :ref:`guide_licenses`.


Distributing a compiled LabVIEW app (Application Builder)
---------------------------------------------------------

If you compile your app for distribution using the LabVIEW Application Builder,
you only need a licensed copy of the Toolkit on the development computer.  The
Toolkit and its plotting runtime are "bootstrapped", and are pulled in
automatically from vi.lib when you compile your app.  Nothing special needs to
be installed on the target computer.

**There are no royalties or "runtime" fees for compiled apps which use the
Toolkit.**  Distribution, including as part of a for-profit app, is generally
permitted.  However, see :ref:`guide_licenses` and the License Agreement
for important licensing restrictions and required disclosure steps you must
perform.


Distributing a native LabVIEW app (Development Environment)
-----------------------------------------------------------

If your app requires the full LabVIEW development environment to run, both
the development and target computers must have a licensed copy of the Toolkit
installed.  Simply install and activate the Toolkit as normal, using the VI
Package Manager (2014 or later).

A note on the plotting cache
----------------------------

A small number of files, which support the plotting subsystem, are extracted
into a cache directory when the Toolkit is first run on any platform. They are
placed in the "local" AppData directory, e.g. ``C:\Users\<username>\AppData\Local.``
This directory will need to be readable, writable, and executable on any
platform on which the Toolkit is installed.  These permissions are the default
on all versions of Windows.  The amount of disk space used for cache files is
very small; less than 10 MB.