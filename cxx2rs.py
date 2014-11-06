#!/usr/bin/env python
""" Usage: call with <filename> <typename>
"""

import sys
import clang.cindex
clang.cindex.Config.set_library_file('/usr/lib/x86_64-linux-gnu/libclang-3.5.so.1')

from rustify import *
from stringify import *

header = """
extern crate libc;
"""

def main():
    index = clang.cindex.Index.create()
    link_name = sys.argv[1]
    tu = index.parse(sys.argv[2])

    print header

    for func in get_functions(tu.cursor, tu.spelling):
        print "/*\n%s*/" % stringify_function_declaration(func)
        print rustify_function_declaration(func, link_name)
        print

    for struct in get_structs(tu.cursor, tu.spelling):
        print "/*\n%s*/" % stringify_struct_declaration(struct)
        print rustify_struct_declaration(struct)


main()
