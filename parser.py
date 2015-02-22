import clang.cindex
from ctypes.util import find_library
clang.cindex.Config.set_library_file(find_library('clang'))

import os.path

#from stringify import *

link_name = None

def get_nodes(node, filename, kind_list):
    try:
        is_kind = (node.kind in kind_list)
    except ValueError as e:
        # unknown cursor kind
        is_kind = False

    if not is_kind:
        for c in node.get_children():
            for node in get_nodes(c, filename, kind_list):
                yield node
    else:
        if node.location.file is not None:
            path = os.path.dirname(filename)
            fname = os.path.dirname(str(node.location.file))
            is_in_dir = (os.path.commonprefix([fname, path]) == path)

            if is_in_dir:
                yield node

def get_function_arg_structs(all_functions):
    clang_types = clang.cindex.TypeKind

    is_struct = lambda arg: arg.get_canonical().get_pointee().get_canonical().kind is clang_types.RECORD
    get_struct_args = lambda fn: filter(is_struct, fn.type.argument_types())

    structs = map(get_struct_args, all_functions)
    structs = reduce(list.__add__, structs, [])

    structs = map(lambda n: n.get_pointee().get_declaration(), structs)

    return structs


def get_enums(node, filename):
    kind_list = [clang.cindex.CursorKind.ENUM_DECL]
    return get_nodes(node, filename, kind_list)

def get_macros(node, filename):
    kind_list = [clang.cindex.CursorKind.MACRO_DEFINITION]
    return get_nodes(node, filename, kind_list)


def get_functions(node, filename):
    kind_list = [clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD]
    return get_nodes(node, filename, kind_list)


def get_structs(node, filename):
    kind_list = [clang.cindex.CursorKind.STRUCT_DECL]
    
    nodes = get_nodes(node, filename, kind_list)
    structs = map(lambda n: n.type.get_declaration(), nodes)

    res = []
    for s in structs:
        if s not in res:
            res.append(s)
    return res

def get_typedefs(node, filename):
    kind_list = [clang.cindex.CursorKind.TYPEDEF_DECL]
    
    nodes = get_nodes(node, filename, kind_list)
    typedefs = map(lambda n: n.type.get_declaration(), nodes)

    res = []
    for t in typedefs:
        if t not in res:
            res.append(t)
    return res

def parent_path(node):
    parent = node.semantic_parent

    if parent is None:
        return []

    if parent.spelling is None:
        return []
    else:
        res = parent_path(parent) + [parent]
        return res

def canonical_function_name(node):
    res = ""
    for p in parent_path(node):
        if p.kind == clang.cindex.CursorKind.CLASS_DECL:
            res += "%s." % p.spelling
        elif p.kind == clang.cindex.CursorKind.NAMESPACE:
            res += "%s::" % p.spelling
        elif p.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
            pass
        else:
            assert(False)

    return res + node.spelling
