cxx2rs
======

A rust-binding generator for C/C++ files


Installation:
-------------

::

    pip install cxx2rs



Use it like this:
-----------------

::

    cxx2rs glib-2.0 /usr/include/glib-2.0/glib/gmain.h `pkg-config --cflags-only-I glib-2.0` > gmain.rs
           ^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    ^^^^^^^^
              |        |                                  |                                       |
              |        |                                  compiler args (optional)                rust include file
              |        C/C++ include file
              library name (rust's #[link(name="glib-2.0")]

