cxx2rs
======

A rust-binding generator for C/C++ files

Use it like this:

    cxx2rs.py glib-2.0 /usr/include/glib-2.0/glib/gmain.h > gmain.rs
              ^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^
              |        |                                    |
              |        |                                    rust include file
              |        C/C++ include file
              library name (rust's #[link(name="glib-2.0")]

Known Problems
==============

- gboolean (`typedef gint gboolean == int`) is converted to int(int*)
