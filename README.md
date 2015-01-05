cxx2rs
======

A rust-binding generator for C/C++ files

Use it like this:

    cxx2rs.py glib-2.0 /usr/include/glib-2.0/glib/gmain.h `pkg-config --cflags-I-only glib-2.0` > gmain.rs
              ^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    ^^^^^^^^
              |        |                                  |                                       |
              |        |                                  compiler args (optional)                rust include file
              |        C/C++ include file
              library name (rust's #[link(name="glib-2.0")]
